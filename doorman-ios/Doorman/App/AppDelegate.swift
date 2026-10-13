import UIKit
import UserNotifications

final class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        // The delegate must be set before launch ends, or taps that launched the app are lost.
        UNUserNotificationCenter.current().delegate = self
        NotificationService.registerCategories()
        // Start listening for StoreKit transactions as early as possible.
        _ = StoreManager.shared
        return true
    }

    // MARK: UNUserNotificationCenterDelegate

    // The notification center may call these off the main thread, so they are
    // nonisolated and hop to the main actor only for app state.

    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping @Sendable (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound, .list])
    }

    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping @Sendable () -> Void
    ) {
        let tap = NotificationTap(response)
        Task { @MainActor in
            Self.handle(tap)
            completionHandler()
        }
    }

    @MainActor
    private static func handle(_ tap: NotificationTap) {
        switch tap {
        case .passRequest:
            AppModel.shared.presentPassRequest()
        case let .honestyAnswer(honored, passID):
            SharedStore.shared.setHonored(honored, forPass: passID)
            AppModel.shared.reloadFromStore()
        case .openApp:
            break // The system already brings the app to the front.
        }
    }
}

/// What a notification tap means for Doorman.
private enum NotificationTap: Sendable {
    case passRequest
    case honestyAnswer(honored: Bool, passID: UUID)
    case openApp

    init(_ response: UNNotificationResponse) {
        let request = response.notification.request
        let content = request.content
        let action = response.actionIdentifier

        let isPassRequest = content.categoryIdentifier == DoormanLink.passRequestCategory
            || request.identifier.hasPrefix(DoormanLink.passRequestNotificationID)
        if isPassRequest {
            self = action == UNNotificationDismissActionIdentifier ? .openApp : .passRequest
            return
        }

        let isHonesty = content.categoryIdentifier == DoormanLink.honestyCategory
            || request.identifier == DoormanLink.honestyNotificationID
        let passID = (content.userInfo[DoormanLink.passIDKey] as? String).flatMap(UUID.init(uuidString:))
        if isHonesty, let passID {
            switch action {
            case DoormanLink.honestyYesAction:
                self = .honestyAnswer(honored: true, passID: passID)
                return
            case DoormanLink.honestyNoAction:
                self = .honestyAnswer(honored: false, passID: passID)
                return
            default:
                break // Plain tap: just open the app.
            }
        }
        self = .openApp
    }
}
