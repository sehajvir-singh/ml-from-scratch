import Foundation
import Observation
import FamilyControls
import WidgetKit
import os

/// App-wide state for the screens. The App Group (`SharedStore`) is the source
/// of truth, because the extensions change it too; this model mirrors it and
/// turns user actions into shield changes.
@MainActor
@Observable
final class AppModel {
    static let shared = AppModel()

    /// Opening the app this soon after tapping "Ask Doorman" goes straight to the pass screen.
    static let pendingRequestWindow: TimeInterval = 5 * 60

    private static let log = Logger(subsystem: "com.doorman.app", category: "AppModel")

    // MARK: State

    /// Setting this saves the settings and updates the shields and the night schedule.
    var settings: DoorSettings {
        get { storedSettings }
        set { commit(newValue, forceApply: false) }
    }

    private(set) var selection = FamilyActivitySelection()
    private(set) var authorization: AuthorizationStatus = .notDetermined

    /// Drives the pass screen. Closing it drops the pending "Ask Doorman" request,
    /// so the screen does not pop up again on the next launch.
    var isPassRequestPresented: Bool {
        get { passScreenShown }
        set {
            if passScreenShown, !newValue {
                SharedStore.shared.pendingRequestAt = nil
            }
            passScreenShown = newValue
        }
    }

    /// True while the judge is thinking about a reason.
    private(set) var isJudging = false
    /// When the current pass ends. nil means the door is closed.
    private(set) var activePassExpiry: Date?
    private(set) var passes: [PassRecord] = []
    private(set) var attemptsToday = 0
    private(set) var attemptsLastHour = 0
    private(set) var phase: DoorPhase = .normal
    private(set) var risk: RiskLevel = .low
    private(set) var minutesUsedToday = 0
    /// Today's first task, if the user set one today.
    private(set) var morningIntention: MorningIntention?
    private(set) var wrapped = WrappedSummary.make(attempts: [], passes: [])
    private(set) var context: ContextSnapshot?
    /// A short, friendly message when something went wrong. The UI may show it and set it to nil.
    var errorMessage: String?

    private var storedSettings = DoorSettings()
    private var passScreenShown = false
    @ObservationIgnored private var expiryTask: Task<Void, Never>?

    private init() {
        selection = SelectionStore.load()
        reloadFromStore()
    }

    // MARK: Derived values

    /// For example "Deck review in 47 min".
    var eventLine: String? { ShieldCopy.eventLine(context: context, now: .now) }

    var hasActivePass: Bool { activePassExpiry != nil }

    var itemCount: Int { SelectionStore.itemCount(selection) }

    // MARK: Screen Time

    func requestAuthorization() async throws {
        defer { authorization = AuthorizationCenter.shared.authorizationStatus }
        try await AuthorizationCenter.shared.requestAuthorization(for: .individual)
    }

    /// Saves the picked apps and shields them right away when the door is closed.
    /// Returns false, and saves nothing, if a free user picked more than the free limit.
    @discardableResult
    func updateSelection(_ newSelection: FamilyActivitySelection) -> Bool {
        guard isWithinLimit(newSelection) else { return false }
        selection = newSelection
        SelectionStore.save(newSelection)
        if settings.doorEnabled, SharedStore.shared.activePassExpiry == nil {
            ShieldManager().lock()
        }
        return true
    }

    /// True if the user may pick one more item on top of `selection`.
    func canAddMoreItems(for selection: FamilyActivitySelection) -> Bool {
        StoreManager.shared.isPro || SelectionStore.itemCount(selection) < StoreManager.freeItemLimit
    }

    /// True if `selection` fits the user's plan.
    func isWithinLimit(_ selection: FamilyActivitySelection) -> Bool {
        StoreManager.shared.isPro || SelectionStore.itemCount(selection) <= StoreManager.freeItemLimit
    }

    // MARK: Door

    func setDoorEnabled(_ on: Bool) {
        var updated = settings
        updated.doorEnabled = on
        commit(updated, forceApply: true)
    }

    /// Marks onboarding done and opens for business: the door turns on when
    /// Screen Time access is granted and at least one app is picked.
    func completeOnboarding() {
        var updated = settings
        updated.hasCompletedOnboarding = true
        if authorization == .approved, itemCount > 0 {
            updated.doorEnabled = true
        }
        commit(updated, forceApply: updated.doorEnabled)
        Task { await refresh() }
    }

    // MARK: Passes

    func presentPassRequest() {
        reloadFromStore()
        isPassRequestPresented = true
    }

    /// Asks the judge for a pass and updates the state with the answer.
    func requestPass(reason: String) async -> PassRecord {
        isJudging = true
        defer { isJudging = false }
        let pass = await PassService.request(reason: reason)
        reloadFromStore()
        return pass
    }

    func endPassNow() {
        PassService.endPassNow()
        reloadFromStore()
    }

    // MARK: Morning door

    func setMorningIntention(_ text: String) {
        let task = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !task.isEmpty else { return }
        SharedStore.shared.morningIntention = MorningIntention(text: task, setAt: .now)
        reloadFromStore()
        WidgetCenter.shared.reloadAllTimelines()
    }

    // MARK: Refresh

    /// Called when the app comes to the front.
    func refresh() async {
        reloadFromStore()
        await PassService.endExpiredActivities()
        relockIfNeeded()
        await ContextProvider.shared.refresh()
        await StoreManager.shared.updateEntitlements()
        reloadFromStore()

        if let pending = SharedStore.shared.pendingRequestAt,
           Date.now.timeIntervalSince(pending) < Self.pendingRequestWindow,
           activePassExpiry == nil {
            isPassRequestPresented = true
        }
        WidgetCenter.shared.reloadAllTimelines()
    }

    /// Re-reads everything the extensions may have changed.
    func reloadFromStore(now: Date = .now) {
        let store = SharedStore.shared
        let attempts = store.attempts
        let hasIntentionToday = store.hasIntentionToday
        let startOfDay = Calendar.current.startOfDay(for: now)

        storedSettings = store.settings
        passes = store.passes
        attemptsToday = attempts.filter { $0 >= startOfDay }.count
        attemptsLastHour = attempts.filter { $0 >= now.addingTimeInterval(-3600) }.count
        phase = DoorPolicy.phase(at: now, settings: storedSettings, hasIntentionToday: hasIntentionToday)
        risk = DoorPolicy.risk(attemptsLastHour: attemptsLastHour, phase: phase)
        minutesUsedToday = DoorPolicy.minutesUsed(on: now, passes: passes)
        morningIntention = hasIntentionToday ? store.morningIntention : nil
        wrapped = WrappedSummary.make(attempts: attempts, passes: passes, endingAt: now)
        context = store.context
        authorization = AuthorizationCenter.shared.authorizationStatus
        trackPassExpiry(store.activePassExpiry)
    }

    // MARK: Private

    private func commit(_ newSettings: DoorSettings, forceApply: Bool) {
        let old = storedSettings
        guard forceApply || newSettings != old else { return }
        storedSettings = newSettings
        SharedStore.shared.settings = newSettings

        // Restarting the night schedule inside the night window makes the monitor
        // run again, so only touch it when something it depends on changed.
        let nightChanged = newSettings.doorEnabled != old.doorEnabled
            || newSettings.nightDoorEnabled != old.nightDoorEnabled
            || newSettings.nightStart != old.nightStart
            || newSettings.nightEnd != old.nightEnd
        if forceApply || nightChanged {
            applyDoorState()
        }
        reloadFromStore()
        WidgetCenter.shared.reloadAllTimelines()
    }

    private func applyDoorState() {
        let shields = ShieldManager()
        guard settings.doorEnabled else {
            shields.disable()
            Task { await PassService.endAllActivities() }
            return
        }
        do {
            try shields.applyNightSchedule(settings)
        } catch {
            Self.log.error("Night schedule failed: \(error.localizedDescription, privacy: .public)")
            errorMessage = "The night door could not start. Try times at least 15 minutes apart."
        }
        if SharedStore.shared.activePassExpiry == nil {
            shields.lock()
        }
    }

    /// The door is closed whenever no pass is running. This catches a pass that
    /// ended while the app was not running and the monitor missed it.
    private func relockIfNeeded() {
        guard settings.doorEnabled, SharedStore.shared.activePassExpiry == nil else { return }
        ShieldManager().lock()
    }

    /// Wakes up when the pass ends, so the screens update while the app is open.
    private func trackPassExpiry(_ expiry: Date?) {
        activePassExpiry = expiry
        expiryTask?.cancel()
        expiryTask = nil
        guard let expiry else { return }
        expiryTask = Task { [weak self] in
            let delay = expiry.timeIntervalSinceNow + 1
            if delay > 0 {
                try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
            }
            guard !Task.isCancelled else { return }
            await self?.passDidExpire()
        }
    }

    private func passDidExpire() async {
        await PassService.endExpiredActivities()
        relockIfNeeded()
        reloadFromStore()
        WidgetCenter.shared.reloadAllTimelines()
    }
}
