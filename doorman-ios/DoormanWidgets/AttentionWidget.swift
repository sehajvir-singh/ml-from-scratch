import SwiftUI
import WidgetKit

/// "Attention budget": pass minutes used today, the daily budget, and how
/// often the user knocked on the door. Shows a countdown while a pass runs.
struct AttentionWidget: Widget {
    /// The app and extensions can refresh it with
    /// `WidgetCenter.shared.reloadTimelines(ofKind: "AttentionWidget")`.
    static let kind = "AttentionWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: Self.kind, provider: AttentionProvider()) { entry in
            AttentionWidgetView(entry: entry)
        }
        .configurationDisplayName("Attention budget")
        .description("Pass minutes used today, and how often you tried to open your apps.")
        .supportedFamilies([.accessoryCircular, .accessoryRectangular, .accessoryInline, .systemSmall])
    }
}

// MARK: - Entry

struct AttentionEntry: TimelineEntry, Sendable {
    let date: Date
    let minutesUsed: Int
    let budgetMinutes: Int
    let opensToday: Int
    /// When the running pass ends. nil = no pass at `date`.
    let passEndsAt: Date?

    /// Share of today's budget used, 0...1.
    var progress: Double {
        min(Double(minutesUsed) / Double(max(budgetMinutes, 1)), 1)
    }

    var isOverBudget: Bool { minutesUsed >= budgetMinutes }

    var minutesLeft: Int { max(budgetMinutes - minutesUsed, 0) }

    /// "48 min left today" or "Budget used up"
    var budgetStatus: String {
        isOverBudget ? "Budget used up" : "\(minutesLeft) min left today"
    }

    /// Countdown range for the running pass, if any.
    var passTimer: ClosedRange<Date>? {
        guard let end = passEndsAt, end > date else { return nil }
        return date...end
    }

    var opensLabel: String { opensToday == 1 ? "1 open" : "\(opensToday) opens" }

    /// "12 / 60 min · 9 opens"
    var summary: String { "\(minutesUsed) / \(budgetMinutes) min · \(opensLabel)" }

    /// "12/60 min", for tight spaces.
    var shortSummary: String { "\(minutesUsed)/\(budgetMinutes) min" }

    static func sample(at date: Date = .now) -> AttentionEntry {
        AttentionEntry(date: date, minutesUsed: 12, budgetMinutes: 60, opensToday: 9, passEndsAt: nil)
    }
}

// MARK: - Timeline

struct AttentionProvider: TimelineProvider {
    typealias Entry = AttentionEntry

    /// How often the widget asks for fresh numbers. The app reloads widgets
    /// after a pass, but new attempts come from the shield, so we also poll.
    static let refreshInterval: TimeInterval = 15 * 60
    /// Entries are planned this far ahead, in case WidgetKit delays the reload.
    static let horizon: TimeInterval = 60 * 60

    func placeholder(in context: Context) -> AttentionEntry {
        .sample()
    }

    func getSnapshot(in context: Context, completion: @escaping @Sendable (AttentionEntry) -> Void) {
        if context.isPreview {
            completion(.sample())
        } else {
            completion(AttentionHistory.load().entry(at: .now))
        }
    }

    func getTimeline(in context: Context, completion: @escaping @Sendable (Timeline<AttentionEntry>) -> Void) {
        let now = Date.now
        let history = AttentionHistory.load()
        let entries = Self.entryDates(from: now, passEndsAt: history.passEndsAt)
            .map { history.entry(at: $0) }
        let nextReload = now.addingTimeInterval(Self.refreshInterval)
        completion(Timeline(entries: entries, policy: .after(nextReload)))
    }

    /// Every 15 minutes, plus the moment the pass ends (the door closes)
    /// and midnight (the day's numbers start over).
    static func entryDates(
        from now: Date,
        passEndsAt: Date?,
        calendar: Calendar = .current
    ) -> [Date] {
        var dates: [Date] = []
        var next = now
        while next <= now.addingTimeInterval(horizon) {
            dates.append(next)
            next = next.addingTimeInterval(refreshInterval)
        }
        if let passEndsAt, passEndsAt > now {
            dates.append(passEndsAt)
        }
        if let midnight = calendar.date(byAdding: .day, value: 1, to: calendar.startOfDay(for: now)),
           midnight <= now.addingTimeInterval(horizon) {
            dates.append(midnight)
        }
        return Array(Set(dates)).sorted()
    }
}

/// One read of the App Group, so every entry in a timeline uses the same data.
/// Each entry then works out its own numbers for its own moment.
struct AttentionHistory: Sendable {
    var passes: [PassRecord]
    var attempts: [Date]
    var budgetMinutes: Int
    var passEndsAt: Date?

    static func load(from store: SharedStore = .shared) -> AttentionHistory {
        AttentionHistory(
            passes: store.passes,
            attempts: store.attempts,
            budgetMinutes: store.settings.dailyBudgetMinutes,
            passEndsAt: store.activePassExpiry
        )
    }

    func entry(at date: Date, calendar: Calendar = .current) -> AttentionEntry {
        let startOfDay = calendar.startOfDay(for: date)
        return AttentionEntry(
            date: date,
            minutesUsed: DoorPolicy.minutesUsed(on: date, passes: passes, calendar: calendar),
            budgetMinutes: budgetMinutes,
            opensToday: attempts.filter { $0 >= startOfDay }.count,
            passEndsAt: passEndsAt.flatMap { $0 > date ? $0 : nil }
        )
    }
}

// MARK: - Views

struct AttentionWidgetView: View {
    @Environment(\.widgetFamily) private var family
    let entry: AttentionEntry

    var body: some View {
        content
            .containerBackground(for: .widget) {
                background
            }
            .widgetURL(DoormanWidgetStyle.homeURL)
    }

    @ViewBuilder
    private var content: some View {
        switch family {
        case .accessoryCircular:
            AttentionCircularView(entry: entry)
        case .accessoryRectangular:
            AttentionRectangularView(entry: entry)
        case .accessoryInline:
            AttentionInlineView(entry: entry)
        default:
            AttentionCardView(entry: entry)
        }
    }

    @ViewBuilder
    private var background: some View {
        switch family {
        case .systemSmall:
            LinearGradient(
                colors: [DoormanWidgetStyle.card, DoormanWidgetStyle.night],
                startPoint: .top,
                endPoint: .bottom
            )
        default:
            // Lock Screen widgets are drawn by the system on the wallpaper.
            Color.clear
        }
    }
}

/// Lock Screen circle: a ring of today's budget, minutes in the middle.
private struct AttentionCircularView: View {
    let entry: AttentionEntry

    var body: some View {
        Gauge(value: entry.progress) {
            Image(systemName: DoormanWidgetStyle.doorSymbol(isOpen: entry.passTimer != nil))
        } currentValueLabel: {
            Text("\(entry.minutesUsed)")
                .font(.system(.body, design: .rounded, weight: .semibold))
        }
        .gaugeStyle(.accessoryCircular)
        .widgetAccentable()
        .accessibilityLabel("\(entry.minutesUsed) of \(entry.budgetMinutes) pass minutes used today")
    }
}

/// Lock Screen rectangle: "Doorman", the summary, then a bar or the pass countdown.
private struct AttentionRectangularView: View {
    let entry: AttentionEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Label("Doorman", systemImage: DoormanWidgetStyle.doorSymbol(isOpen: entry.passTimer != nil))
                .font(.headline)
                .widgetAccentable()

            Text(entry.summary)
                .font(.subheadline)
                .lineLimit(1)
                .minimumScaleFactor(0.8)

            if let end = entry.passTimer?.upperBound {
                Text("Door open · \(end, style: .timer)")
                    .font(.subheadline)
                    .monospacedDigit()
                    .lineLimit(1)
            } else {
                Gauge(value: entry.progress) {
                    EmptyView()
                }
                .gaugeStyle(.accessoryLinearCapacity)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

/// One line above the clock. Falls back to a shorter text when space is tight.
private struct AttentionInlineView: View {
    let entry: AttentionEntry

    var body: some View {
        if let end = entry.passTimer?.upperBound {
            Label {
                Text("Door open · \(end, style: .timer)")
            } icon: {
                Image(systemName: DoormanWidgetStyle.doorOpenSymbol)
            }
        } else {
            ViewThatFits {
                Label(entry.summary, systemImage: DoormanWidgetStyle.doorClosedSymbol)
                Label(entry.shortSummary, systemImage: DoormanWidgetStyle.doorClosedSymbol)
            }
        }
    }
}

/// Home screen card: big minutes number, budget bar, opens today.
private struct AttentionCardView: View {
    let entry: AttentionEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack(spacing: 6) {
                Image(systemName: DoormanWidgetStyle.doorSymbol(isOpen: entry.passTimer != nil))
                    .foregroundStyle(DoormanWidgetStyle.coral)
                    .widgetAccentable()
                Text("Doorman")
                    .font(.subheadline.weight(.semibold))
                Spacer(minLength: 0)
            }

            Spacer(minLength: 6)

            if let timer = entry.passTimer {
                passCountdown(timer)
            } else {
                budget
            }

            Spacer(minLength: 6)

            ProgressView(value: entry.progress)
                .tint(DoormanWidgetStyle.coral)

            Text("\(entry.opensLabel) today")
                .font(.caption)
                .foregroundStyle(DoormanWidgetStyle.secondaryText)
                .padding(.top, 6)
        }
        .foregroundStyle(.white)
    }

    private var budget: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Text("\(entry.minutesUsed)")
                    .font(.system(size: 40, weight: .bold, design: .rounded))
                    .widgetAccentable()
                Text("/ \(entry.budgetMinutes) min")
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(DoormanWidgetStyle.secondaryText)
            }
            .lineLimit(1)
            .minimumScaleFactor(0.6)

            Text(entry.budgetStatus)
                .font(.caption.weight(.medium))
                .foregroundStyle(entry.isOverBudget ? DoormanWidgetStyle.coral : DoormanWidgetStyle.secondaryText)
                .lineLimit(1)
        }
    }

    private func passCountdown(_ timer: ClosedRange<Date>) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text("Door open")
                .font(.caption.weight(.medium))
                .foregroundStyle(DoormanWidgetStyle.secondaryText)
            Text(timerInterval: timer, countsDown: true)
                .font(.system(size: 36, weight: .bold, design: .rounded))
                .monospacedDigit()
                .foregroundStyle(DoormanWidgetStyle.coral)
                .lineLimit(1)
                .minimumScaleFactor(0.6)
                .widgetAccentable()
        }
    }
}
