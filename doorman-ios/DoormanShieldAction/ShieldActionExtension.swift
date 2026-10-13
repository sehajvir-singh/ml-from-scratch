import ManagedSettings
import UserNotifications

/// Handles the two buttons on the shield.
/// "Ask Doorman" can't open the app directly (shield extensions are not
/// allowed to), so it posts a notification that opens the pass screen.
final class ShieldActionExtension: ShieldActionDelegate {
    override func handle(
        action: ShieldAction,
        for application: ApplicationToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        respond(to: action, completionHandler: completionHandler)
    }

    override func handle(
        action: ShieldAction,
        for webDomain: WebDomainToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        respond(to: action, completionHandler: completionHandler)
    }

    override func handle(
        action: ShieldAction,
        for category: ActivityCategoryToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        respond(to: action, completionHandler: completionHandler)
    }

    // MARK: Actions

    private func respond(
        to action: ShieldAction,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        switch action {
        case .primaryButtonPressed:
            askDoorman(completionHandler: completionHandler)
        case .secondaryButtonPressed:
            completionHandler(.close)
        @unknown default:
            completionHandler(.close)
        }
    }

    private func askDoorman(completionHandler: @escaping (ShieldActionResponse) -> Void) {
        let store = SharedStore.shared
        store.recordAttempt()
        store.pendingRequestAt = .now

        // Answer only once the notification is queued (or failed), then
        // `.defer` so the shield redraws with "Tap the Doorman notification".
        UNUserNotificationCenter.current().add(Self.passRequest()) { _ in
            completionHandler(.defer)
        }
    }

    private static func passRequest() -> UNNotificationRequest {
        let content = UNMutableNotificationContent()
        content.title = "Doorman"
        content.body = "Tap here and tell me why you want in."
        content.sound = .default
        content.categoryIdentifier = DoormanLink.passRequestCategory
        content.interruptionLevel = .active

        // nil trigger = deliver right away. The fixed id replaces an older
        // request instead of stacking a new banner for every tap.
        return UNNotificationRequest(
            identifier: DoormanLink.passRequestNotificationID,
            content: content,
            trigger: nil
        )
    }
}
