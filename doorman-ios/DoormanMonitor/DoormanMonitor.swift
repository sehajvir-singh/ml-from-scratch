import DeviceActivity
import ManagedSettings
import WidgetKit

/// Wakes up when a Doorman schedule starts, warns or ends, and closes the door.
/// Monitor extensions get about 6 MB of memory, so this only flips shields and
/// asks widgets to refresh. No UI, no models, no big reads.
final class DoormanMonitor: DeviceActivityMonitor {
    override func intervalDidStart(for activity: DeviceActivityName) {
        super.intervalDidStart(for: activity)
        guard activity == .night, doorIsOn else { return }
        // The night door beats a running pass: stop the pass schedule and lock.
        ShieldManager().endPass()
        refreshWidgets()
    }

    override func intervalWillEndWarning(for activity: DeviceActivityName) {
        super.intervalWillEndWarning(for: activity)
        // Passes under 15 minutes run on a 15 minute schedule whose warning
        // fires exactly when the pass is over (see ShieldManager.scheduleRelock).
        guard activity == .pass else { return }
        relock()
    }

    override func intervalDidEnd(for activity: DeviceActivityName) {
        super.intervalDidEnd(for: activity)
        // The real end for passes of 15+ minutes, and a backup for shorter ones.
        guard activity == .pass else { return }
        relock()
    }

    // MARK: Helpers

    /// Read fresh every time: the app can switch the door off while we sleep.
    private var doorIsOn: Bool {
        SharedStore.shared.settings.doorEnabled
    }

    private func relock() {
        guard doorIsOn else { return }
        ShieldManager().lock()
        refreshWidgets()
    }

    private func refreshWidgets() {
        WidgetCenter.shared.reloadAllTimelines()
    }
}
