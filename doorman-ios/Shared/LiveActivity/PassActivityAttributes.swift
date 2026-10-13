import Foundation
import ActivityKit

/// Live Activity shown in the Dynamic Island and on the Lock Screen while a pass runs.
/// Started by the app (PassService); drawn by the DoormanWidgets extension.
struct PassActivityAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        var startedAt: Date
        var expiresAt: Date
    }

    /// What the user said they would do, e.g. "reply to Maya".
    var reason: String
    /// ReasonCategory raw value.
    var category: String
}
