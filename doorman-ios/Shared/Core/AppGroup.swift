import Foundation

/// Every target (app + extensions) shares data through one App Group.
/// If you change the bundle ID prefix in project.yml, change `id` here too.
enum AppGroup {
    static let id = "group.com.doorman.app"

    static var defaults: UserDefaults {
        UserDefaults(suiteName: id) ?? .standard
    }
}

/// Deep links and notification identifiers shared by the app and extensions.
enum DoormanLink {
    static let scheme = "doorman"
    static let passRequestURL = URL(string: "doorman://pass")!

    static let passRequestNotificationID = "doorman.pass.request"
    static let passRequestCategory = "DOORMAN_PASS_REQUEST"

    static let honestyNotificationID = "doorman.pass.honesty"
    static let honestyCategory = "DOORMAN_HONESTY"
    static let honestyYesAction = "DOORMAN_HONESTY_YES"
    static let honestyNoAction = "DOORMAN_HONESTY_NO"

    /// userInfo key that carries a PassRecord id (UUID string).
    static let passIDKey = "passID"
}
