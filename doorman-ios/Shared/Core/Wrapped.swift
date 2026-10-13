import Foundation

/// The weekly "Attention Wrapped" summary.
struct WrappedSummary: Hashable, Sendable {
    var attempts: Int
    var passes: Int
    var denied: Int
    var minutesGranted: Int
    /// Share of passes with no concrete goal ("just checking" or "bored"), 0...1.
    var mindlessShare: Double
    /// Share of answered honesty checks where the user did what they said, 0...1.
    /// nil if no honesty check was answered.
    var honestyRate: Double?
    /// Hour of day (0-23) with the most attempts. nil if no attempts.
    var worstHour: Int?
    var topCategory: ReasonCategory?

    static func make(
        attempts: [Date],
        passes: [PassRecord],
        endingAt end: Date = .now,
        days: Int = 7,
        calendar: Calendar = .current
    ) -> WrappedSummary {
        let start = end.addingTimeInterval(-Double(days) * 86_400)
        let weekAttempts = attempts.filter { $0 >= start && $0 <= end }
        let weekPasses = passes.filter { $0.requestedAt >= start && $0.requestedAt <= end }
        let granted = weekPasses.filter { !$0.wasDenied }

        let mindless = granted.filter { $0.category.isMindless }.count
        let answered = granted.compactMap(\.honored)
        let honest = answered.filter { $0 }.count

        var byHour: [Int: Int] = [:]
        for date in weekAttempts {
            byHour[calendar.component(.hour, from: date), default: 0] += 1
        }
        let worstHour = byHour.max { a, b in a.value == b.value ? a.key > b.key : a.value < b.value }?.key

        var byCategory: [ReasonCategory: Int] = [:]
        for pass in granted { byCategory[pass.category, default: 0] += 1 }
        let top = byCategory.max { a, b in a.value == b.value ? a.key.rawValue > b.key.rawValue : a.value < b.value }?.key

        return WrappedSummary(
            attempts: weekAttempts.count,
            passes: granted.count,
            denied: weekPasses.count - granted.count,
            minutesGranted: granted.reduce(0) { $0 + $1.grantedMinutes },
            mindlessShare: granted.isEmpty ? 0 : Double(mindless) / Double(granted.count),
            honestyRate: answered.isEmpty ? nil : Double(honest) / Double(answered.count),
            worstHour: worstHour,
            topCategory: top
        )
    }

    static func hourLabel(_ hour: Int) -> String {
        switch hour {
        case 0: "12am"
        case 1..<12: "\(hour)am"
        case 12: "12pm"
        default: "\(hour - 12)pm"
        }
    }
}
