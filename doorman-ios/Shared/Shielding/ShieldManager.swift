import Foundation
import FamilyControls
import ManagedSettings
import DeviceActivity

extension ManagedSettingsStore.Name {
    static let doorman = Self("doorman")
}

extension DeviceActivityName {
    /// One-shot schedule that re-locks the door when a pass ends.
    static let pass = Self("doorman.pass")
    /// Daily repeating schedule for the night door.
    static let night = Self("doorman.night")
}

/// The apps, categories and websites the user put behind the door.
/// FamilyActivitySelection is Codable, so it is stored in the App Group.
enum SelectionStore {
    private static let key = "selection.v1"

    static func load() -> FamilyActivitySelection {
        guard let data = AppGroup.defaults.data(forKey: key),
              let selection = try? JSONDecoder().decode(FamilyActivitySelection.self, from: data)
        else { return FamilyActivitySelection() }
        return selection
    }

    static func save(_ selection: FamilyActivitySelection) {
        if let data = try? JSONEncoder().encode(selection) {
            AppGroup.defaults.set(data, forKey: key)
        }
    }

    /// Number of picked apps + categories + websites (used for the free tier limit).
    static func itemCount(_ selection: FamilyActivitySelection) -> Int {
        selection.applicationTokens.count + selection.categoryTokens.count + selection.webDomainTokens.count
    }
}

/// Applies and removes shields, and schedules the re-lock after a pass.
/// Used by the app and by the DeviceActivity monitor extension.
struct ShieldManager {
    /// DeviceActivity rejects intervals shorter than 15 minutes.
    static let minimumIntervalMinutes = 15

    private let store = ManagedSettingsStore(named: .doorman)
    private let center = DeviceActivityCenter()

    /// Close the door: shield every selected app, category and website.
    func lock() {
        let selection = SelectionStore.load()
        store.shield.applications = selection.applicationTokens.isEmpty ? nil : selection.applicationTokens
        store.shield.applicationCategories = selection.categoryTokens.isEmpty
            ? nil
            : .specific(selection.categoryTokens)
        store.shield.webDomains = selection.webDomainTokens.isEmpty ? nil : selection.webDomainTokens
        SharedStore.shared.activePassExpiry = nil
    }

    /// Turn Doorman off completely: no shields, no schedules.
    func disable() {
        store.clearAllSettings()
        center.stopMonitoring()
        SharedStore.shared.activePassExpiry = nil
    }

    /// Open the door for `minutes` and schedule the re-lock.
    /// Returns the moment the pass ends.
    @discardableResult
    func grantPass(minutes: Int, now: Date = .now) throws -> Date {
        precondition(minutes > 0, "A pass needs at least one minute")
        try scheduleRelock(afterMinutes: minutes, now: now)
        store.clearAllSettings()
        let expiry = now.addingTimeInterval(TimeInterval(minutes * 60))
        SharedStore.shared.activePassExpiry = expiry
        return expiry
    }

    /// End the current pass now.
    func endPass() {
        center.stopMonitoring([.pass])
        lock()
    }

    /// Re-lock after `minutes`. Intervals shorter than 15 minutes are not allowed,
    /// so for short passes we schedule a 15 minute interval and use `warningTime`:
    /// `intervalWillEndWarning` then fires `minutes` after now, and the monitor
    /// extension re-locks there. `intervalDidEnd` re-locks again as a backup.
    func scheduleRelock(afterMinutes minutes: Int, now: Date = .now) throws {
        center.stopMonitoring([.pass])

        let intervalMinutes = max(Self.minimumIntervalMinutes, minutes)
        let end = now.addingTimeInterval(TimeInterval(intervalMinutes * 60))
        let warning: DateComponents? = minutes < intervalMinutes
            ? DateComponents(minute: intervalMinutes - minutes)
            : nil

        // Full date components so a pass that crosses midnight still works.
        let parts: Set<Calendar.Component> = [.year, .month, .day, .hour, .minute, .second]
        let calendar = Calendar.current
        let schedule = DeviceActivitySchedule(
            intervalStart: calendar.dateComponents(parts, from: now),
            intervalEnd: calendar.dateComponents(parts, from: end),
            repeats: false,
            warningTime: warning
        )
        try center.startMonitoring(.pass, during: schedule)
    }

    /// Start or stop the daily night door schedule to match the settings.
    func applyNightSchedule(_ settings: DoorSettings) throws {
        center.stopMonitoring([.night])
        guard settings.doorEnabled, settings.nightDoorEnabled else { return }
        let schedule = DeviceActivitySchedule(
            intervalStart: settings.nightStart.dateComponents,
            intervalEnd: settings.nightEnd.dateComponents,
            repeats: true
        )
        try center.startMonitoring(.night, during: schedule)
    }
}
