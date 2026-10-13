import Foundation

/// The time-of-day mode the door is in.
enum DoorPhase: String, Codable, Sendable {
    case normal
    case morning   // after wake-up, before the first task is set
    case night     // inside the night window
}

enum RiskLevel: Int, Codable, Comparable, Sendable {
    case low, medium, high
    static func < (a: RiskLevel, b: RiskLevel) -> Bool { a.rawValue < b.rawValue }
}

/// The door's answer to a pass request. Produced by the on-device model
/// (see PassJudge in the app) or by `DoorPolicy.fallbackDecision`.
struct PassDecision: Codable, Hashable, Sendable {
    var minutes: Int            // 0 = denied
    var category: ReasonCategory
    var reply: String
}

/// Pure rules with no Apple-only frameworks, so they run in every target
/// and in unit tests on any platform.
enum DoorPolicy {
    /// Longest pass the door ever grants, in minutes.
    static let maxPassMinutes = 30
    /// How long the morning door stays active after the night window ends.
    static let morningWindowHours = 3

    // MARK: Phase

    static func phase(
        at date: Date,
        settings: DoorSettings,
        hasIntentionToday: Bool,
        calendar: Calendar = .current
    ) -> DoorPhase {
        let minuteOfDay = minutes(of: date, calendar: calendar)
        let start = settings.nightStart.hour * 60 + settings.nightStart.minute
        let end = settings.nightEnd.hour * 60 + settings.nightEnd.minute

        if settings.nightDoorEnabled, isInWindow(minuteOfDay, start: start, end: end) {
            return .night
        }
        if settings.morningDoorEnabled, !hasIntentionToday {
            let morningEnd = (end + morningWindowHours * 60) % (24 * 60)
            if isInWindow(minuteOfDay, start: end, end: morningEnd) {
                return .morning
            }
        }
        return .normal
    }

    /// True if `minute` is inside [start, end), where the window may cross midnight.
    static func isInWindow(_ minute: Int, start: Int, end: Int) -> Bool {
        if start == end { return false }
        if start < end { return minute >= start && minute < end }
        return minute >= start || minute < end
    }

    static func minutes(of date: Date, calendar: Calendar = .current) -> Int {
        let comps = calendar.dateComponents([.hour, .minute], from: date)
        return (comps.hour ?? 0) * 60 + (comps.minute ?? 0)
    }

    // MARK: Risk

    /// How much friction to show before the user may even ask.
    static func risk(attemptsLastHour: Int, phase: DoorPhase) -> RiskLevel {
        if phase == .night { return .high }
        switch attemptsLastHour {
        case ..<3: return .low
        case 3..<6: return .medium
        default: return .high
        }
    }

    // MARK: Classification

    /// Keyword fallback when the on-device model is unavailable.
    static func classify(_ reason: String) -> ReasonCategory {
        let text = reason.lowercased()
        func has(_ words: [String]) -> Bool { words.contains { text.contains($0) } }

        if text.trimmingCharacters(in: .whitespacesAndNewlines).count < 3 { return .habit }
        if has(["bored", "boring", "nothing to do", "procrastinat", "relax", "chill", "kill time", "wind down"]) {
            return .bored
        }
        if has(["just check", "checking", "scroll", "see what", "nothing", "idk", "dunno", "just because", "quick look"]) {
            return .habit
        }
        if has(["reply", "respond", "answer", "message", "dm", "text ", "chat", "call ", "comment back"]) {
            return .reply
        }
        if has(["post", "upload", "create", "film", "story", "reel", "publish", "edit my"]) {
            return .create
        }
        if has(["work", "client", "boss", "meeting", "school", "class", "homework", "study", "job", "business", "email", "deadline"]) {
            return .work
        }
        if has(["look up", "lookup", "find", "search", "check the", "address", "recipe", "price", "how to", "what is", "directions", "event", "ticket"]) {
            return .lookup
        }
        return .habit
    }

    // MARK: Fallback decision

    /// Rule-based decision used when Apple Intelligence is not available.
    static func fallbackDecision(
        reason: String,
        phase: DoorPhase,
        attemptsLastHour: Int,
        minutesUsedToday: Int,
        dailyBudgetMinutes: Int
    ) -> PassDecision {
        let category = classify(reason)
        let overBudget = minutesUsedToday >= dailyBudgetMinutes
        let risk = risk(attemptsLastHour: attemptsLastHour, phase: phase)

        var minutes: Int
        switch category {
        case .reply: minutes = 3
        case .lookup: minutes = 2
        case .work: minutes = 10
        case .create: minutes = 8
        case .habit: minutes = 1
        case .bored: minutes = 2
        }

        switch phase {
        case .night:
            minutes = (category == .reply || category == .lookup) ? 2 : 0
        case .morning:
            if category.isMindless { minutes = 0 }
        case .normal:
            break
        }

        if overBudget { minutes = category.isMindless ? 0 : min(minutes, 2) }
        if risk == .high, minutes > 1 { minutes = max(1, minutes / 2) }
        minutes = clamp(minutes)

        return PassDecision(
            minutes: minutes,
            category: category,
            reply: reply(for: category, minutes: minutes, phase: phase, overBudget: overBudget)
        )
    }

    static func clamp(_ minutes: Int) -> Int {
        min(max(minutes, 0), maxPassMinutes)
    }

    static func reply(for category: ReasonCategory, minutes: Int, phase: DoorPhase, overBudget: Bool) -> String {
        if minutes == 0 {
            switch phase {
            case .night: return "It's late. The door opens again in the morning."
            case .morning: return "Set your first task for today, then ask again."
            case .normal:
                return overBudget
                    ? "Today's attention budget is used up. Only real tasks get in now."
                    : "Not this time. Come back with a clear reason."
            }
        }
        let unit = minutes == 1 ? "minute" : "minutes"
        switch category {
        case .reply: return "Granted: \(minutes) \(unit) to reply. Then out."
        case .lookup: return "Granted: \(minutes) \(unit). Find it and leave."
        case .work: return "Granted: \(minutes) \(unit) for work. Stay on task."
        case .create: return "Granted: \(minutes) \(unit) to create. Post and go."
        case .habit: return "\(minutes) \(unit). Notice the habit."
        case .bored: return "\(minutes) \(unit). Maybe stand up and stretch after?"
        }
    }

    // MARK: Usage

    static func minutesUsed(on day: Date, passes: [PassRecord], calendar: Calendar = .current) -> Int {
        passes
            .filter { calendar.isDate($0.requestedAt, inSameDayAs: day) }
            .reduce(0) { $0 + $1.grantedMinutes }
    }
}
