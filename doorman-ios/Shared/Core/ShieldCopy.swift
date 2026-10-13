import Foundation

/// Text shown on the shield screen. Kept in Core so it can be unit tested.
enum ShieldCopy {
    static let title = "Doorman"
    static let primaryButton = "Ask Doorman"
    static let secondaryButton = "Not now"

    /// One live line about the user's day, for example
    /// "Deck review in 47 min · 6th open today".
    static func subtitle(
        context: ContextSnapshot?,
        attemptsToday: Int,
        phase: DoorPhase,
        now: Date = .now
    ) -> String {
        var parts: [String] = []

        switch phase {
        case .night: parts.append("Night door is on")
        case .morning: parts.append("Set your first task first")
        case .normal:
            if let event = eventLine(context: context, now: now) { parts.append(event) }
        }

        // attemptsToday counts earlier opens; this one is the next.
        parts.append("\(ordinal(attemptsToday + 1)) open today")
        return parts.joined(separator: " · ")
    }

    static func eventLine(context: ContextSnapshot?, now: Date) -> String? {
        guard let context, let title = context.nextEventTitle, let start = context.nextEventStart else { return nil }
        let minutes = Int(start.timeIntervalSince(now) / 60)
        guard minutes >= 0, minutes <= 12 * 60 else { return nil }
        let shortTitle = title.count > 28 ? String(title.prefix(27)) + "…" : title
        if minutes < 60 { return "\(shortTitle) in \(max(minutes, 1)) min" }
        let hours = minutes / 60
        let rest = minutes % 60
        return rest == 0 ? "\(shortTitle) in \(hours) h" : "\(shortTitle) in \(hours) h \(rest) min"
    }

    static func ordinal(_ n: Int) -> String {
        let suffix: String
        switch (n % 100, n % 10) {
        case (11...13, _): suffix = "th"
        case (_, 1): suffix = "st"
        case (_, 2): suffix = "nd"
        case (_, 3): suffix = "rd"
        default: suffix = "th"
        }
        return "\(n)\(suffix)"
    }
}
