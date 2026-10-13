import Foundation

/// Why the user says they want in. Used for stats and for the honesty check.
enum ReasonCategory: String, Codable, CaseIterable, Sendable {
    case reply      // answer a specific person or message
    case lookup     // look up one specific thing
    case work       // work, school or business task
    case create     // post or create something on purpose
    case habit      // "just checking", no clear goal
    case bored      // boredom, procrastination, winding down

    var label: String {
        switch self {
        case .reply: "Reply"
        case .lookup: "Look up"
        case .work: "Work"
        case .create: "Create"
        case .habit: "Just checking"
        case .bored: "Bored"
        }
    }

    /// Opens with no concrete goal. These count against the user in Wrapped.
    var isMindless: Bool { self == .habit || self == .bored }
}

/// One granted (or denied) pass through the door.
struct PassRecord: Codable, Identifiable, Hashable, Sendable {
    var id: UUID = UUID()
    var reason: String
    var category: ReasonCategory
    var grantedMinutes: Int          // 0 means the pass was denied
    var requestedAt: Date
    var expiresAt: Date
    var doorReply: String            // what Doorman said back
    /// Answer to "Did you do it?" after the pass. nil = not answered yet.
    var honored: Bool? = nil

    var wasDenied: Bool { grantedMinutes == 0 }
}

/// Hour + minute, stored without a date. Used for night door times.
struct ClockTime: Codable, Hashable, Sendable {
    var hour: Int
    var minute: Int

    var dateComponents: DateComponents { DateComponents(hour: hour, minute: minute) }

    func formatted() -> String {
        var comps = DateComponents()
        comps.hour = hour
        comps.minute = minute
        let date = Calendar.current.date(from: comps) ?? .now
        return date.formatted(date: .omitted, time: .shortened)
    }
}

struct DoorSettings: Codable, Hashable, Sendable {
    /// Master switch. When on, chosen apps are shielded except during a pass.
    var doorEnabled: Bool = false
    var nightDoorEnabled: Bool = true
    var nightStart = ClockTime(hour: 23, minute: 0)
    var nightEnd = ClockTime(hour: 7, minute: 0)
    /// Morning door: after nightEnd, passes need a first task to be set.
    var morningDoorEnabled: Bool = true
    /// Daily "attention budget" in pass minutes, shown in the widget.
    var dailyBudgetMinutes: Int = 60
    var hasCompletedOnboarding: Bool = false
}

/// Context the shield screen shows. Written by the app, read by extensions.
struct ContextSnapshot: Codable, Hashable, Sendable {
    var nextEventTitle: String?
    var nextEventStart: Date?
    var updatedAt: Date = .now
}

/// The task the user commits to in the morning door.
struct MorningIntention: Codable, Hashable, Sendable {
    var text: String
    var setAt: Date
}
