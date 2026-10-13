import Foundation
import UserNotifications
import os

/// Local notifications: the honesty check after a pass, and the categories
/// for the "Ask Doorman" notification that the shield action extension posts.
enum NotificationService {
    /// Ask a little after the pass ends, once the apps are locked again.
    static let honestyDelay: TimeInterval = 10

    private static let log = Logger(subsystem: "com.doorman.app", category: "Notifications")
    private static var center: UNUserNotificationCenter { .current() }

    // MARK: Permission

    @discardableResult
    static func requestAuthorization() async -> Bool {
        do {
            return try await center.requestAuthorization(options: [.alert, .sound])
        } catch {
            log.error("Notification permission failed: \(error.localizedDescription, privacy: .public)")
            return false
        }
    }

    static func isAuthorized() async -> Bool {
        let status = await center.notificationSettings().authorizationStatus
        return status == .authorized || status == .provisional || status == .ephemeral
    }

    // MARK: Categories

    static func registerCategories() {
        let passRequest = UNNotificationCategory(
            identifier: DoormanLink.passRequestCategory,
            actions: [],
            intentIdentifiers: []
        )
        let yes = UNNotificationAction(
            identifier: DoormanLink.honestyYesAction,
            title: "Yes, done",
            options: [],
            icon: UNNotificationActionIcon(systemImageName: "checkmark.circle")
        )
        let no = UNNotificationAction(
            identifier: DoormanLink.honestyNoAction,
            title: "No",
            options: [],
            icon: UNNotificationActionIcon(systemImageName: "xmark.circle")
        )
        let honesty = UNNotificationCategory(
            identifier: DoormanLink.honestyCategory,
            actions: [yes, no],
            intentIdentifiers: []
        )
        center.setNotificationCategories([passRequest, honesty])
    }

    // MARK: Honesty check

    /// "Did you reply to Maya?", shown just after the pass ends.
    /// Replaces any earlier honesty check that has not fired yet.
    static func scheduleHonesty(for pass: PassRecord) {
        let content = UNMutableNotificationContent()
        content.title = "Doorman"
        content.body = honestyQuestion(for: pass)
        content.sound = .default
        content.categoryIdentifier = DoormanLink.honestyCategory
        content.userInfo = [DoormanLink.passIDKey: pass.id.uuidString]

        // The trigger interval must be greater than zero.
        let delay = max(1, pass.expiresAt.timeIntervalSinceNow + honestyDelay)
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: delay, repeats: false)
        let request = UNNotificationRequest(
            identifier: DoormanLink.honestyNotificationID,
            content: content,
            trigger: trigger
        )
        center.add(request) { error in
            if let error {
                Self.log.error("Could not schedule honesty check: \(error.localizedDescription, privacy: .public)")
            }
        }
    }

    static func cancelHonesty() {
        center.removePendingNotificationRequests(withIdentifiers: [DoormanLink.honestyNotificationID])
        center.removeDeliveredNotifications(withIdentifiers: [DoormanLink.honestyNotificationID])
    }

    // MARK: Wording

    /// Turns the reason into a yes/no question: "reply to my mom" → "Did you reply to your mom?".
    /// Falls back to quoting the reason when it does not start with a plain verb.
    static func honestyQuestion(for pass: PassRecord) -> String {
        let reason = pass.reason
            .trimmingCharacters(in: .whitespacesAndNewlines.union(.punctuationCharacters))
        guard !reason.isEmpty else { return "Did you do what you came for?" }

        var words = reason.split(whereSeparator: \.isWhitespace).map(String.init)
        while let first = words.first, leadIns.contains(first.lowercased()) {
            words.removeFirst()
        }
        words = words.map { swappedPronoun($0) }

        if let verb = words.first?.lowercased(), verbs.contains(verb), words.count <= 9 {
            words[0] = verb
            return "Did you \(words.joined(separator: " "))?"
        }

        let quote = reason.count > 40 ? String(reason.prefix(39)) + "…" : reason
        return "You said “\(quote)”. Did you do it?"
    }

    /// Words people put before the actual task, like "I need to" or "just".
    private static let leadIns: Set<String> = [
        "i", "i'm", "im", "i’m", "need", "want", "wanna", "have", "has", "gotta", "got",
        "going", "gonna", "must", "should", "will", "i'll", "i’ll", "let", "me", "to",
        "just", "quickly", "please", "real", "really", "so",
    ]

    /// Plain verbs that read well after "Did you".
    private static let verbs: Set<String> = [
        "reply", "respond", "answer", "text", "message", "dm", "call", "email", "send",
        "check", "look", "find", "search", "read", "watch", "see", "post", "upload",
        "share", "create", "make", "edit", "film", "write", "comment", "book", "buy",
        "order", "pay", "get", "join", "confirm", "sign", "update", "finish", "open",
        "download", "save", "follow", "learn", "study", "plan", "ask", "tell", "wish",
        "thank", "schedule", "submit", "review", "fix", "record", "return", "grab",
    ]

    private static func swappedPronoun(_ word: String) -> String {
        switch word.lowercased() {
        case "my": "your"
        case "me": "you"
        case "myself": "yourself"
        case "mine": "yours"
        default: word
        }
    }
}
