import ActivityKit
import SwiftUI
import WidgetKit

/// The pass countdown on the Lock Screen and in the Dynamic Island.
/// The app starts the activity; this extension only draws it.
struct PassLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: PassActivityAttributes.self) { context in
            PassLockScreenView(pass: PassDisplay(context))
                .activityBackgroundTint(DoormanWidgetStyle.night)
                .activitySystemActionForegroundColor(.white)
                .widgetURL(DoormanWidgetStyle.homeURL)
        } dynamicIsland: { context in
            let pass = PassDisplay(context)
            return DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    PassIslandLeading(pass: pass)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    PassIslandTrailing(pass: pass)
                }
                DynamicIslandExpandedRegion(.bottom) {
                    PassIslandBottom(pass: pass)
                }
            } compactLeading: {
                PassDoorIcon(isOpen: !pass.isOver)
            } compactTrailing: {
                PassCompactTrailing(pass: pass)
            } minimal: {
                PassDoorIcon(isOpen: !pass.isOver)
            }
            .keylineTint(DoormanWidgetStyle.coral)
            .widgetURL(DoormanWidgetStyle.homeURL)
        }
    }
}

// MARK: - Data for the views

/// What every view needs from the activity, worked out once.
private struct PassDisplay {
    let reason: String
    let categoryLabel: String
    let timer: ClosedRange<Date>
    /// The pass ran out. The monitor extension re-locks the apps on its own,
    /// so the activity may still be on screen for a moment after that.
    let isOver: Bool

    init(_ context: ActivityViewContext<PassActivityAttributes>, now: Date = .now) {
        let state = context.state
        // A range whose end is before its start would crash, so clamp the start.
        timer = min(state.startedAt, state.expiresAt)...state.expiresAt
        isOver = context.isStale || state.expiresAt <= now

        let trimmed = context.attributes.reason.trimmingCharacters(in: .whitespacesAndNewlines)
        reason = trimmed.isEmpty ? "Short pass" : trimmed
        categoryLabel = ReasonCategory(rawValue: context.attributes.category)?.label ?? "Pass"
    }
}

private enum PassCopy {
    static let doorClosed = "Door closed"
    static let timeIsUp = "Time's up. Back to your day."
}

// MARK: - Lock Screen and banner

private struct PassLockScreenView: View {
    let pass: PassDisplay

    var body: some View {
        Group {
            if pass.isOver {
                closed
            } else {
                running
            }
        }
        .padding(16)
        .foregroundStyle(.white)
    }

    private var running: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .center, spacing: 12) {
                PassDoorBadge(isOpen: true)

                VStack(alignment: .leading, spacing: 2) {
                    Text("Pass: \(pass.reason)")
                        .font(.headline)
                        .lineLimit(2)
                    Text(pass.categoryLabel)
                        .font(.subheadline)
                        .foregroundStyle(DoormanWidgetStyle.secondaryText)
                }

                Spacer(minLength: 8)

                PassCountdown(timer: pass.timer)
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                    // Timer text grows to fill its row, so give it a fixed lane.
                    .frame(maxWidth: 112, alignment: .trailing)
            }

            PassProgressBar(timer: pass.timer)
        }
    }

    private var closed: some View {
        HStack(alignment: .center, spacing: 12) {
            PassDoorBadge(isOpen: false)

            VStack(alignment: .leading, spacing: 2) {
                Text(PassCopy.doorClosed)
                    .font(.headline)
                Text(PassCopy.timeIsUp)
                    .font(.subheadline)
                    .foregroundStyle(DoormanWidgetStyle.secondaryText)
            }

            Spacer(minLength: 0)
        }
    }
}

// MARK: - Dynamic Island

private struct PassIslandLeading: View {
    let pass: PassDisplay

    var body: some View {
        Label {
            Text(pass.isOver ? PassCopy.doorClosed : pass.categoryLabel)
                .lineLimit(1)
        } icon: {
            PassDoorIcon(isOpen: !pass.isOver)
        }
        .font(.headline)
        .foregroundStyle(.white)
    }
}

private struct PassIslandTrailing: View {
    let pass: PassDisplay

    var body: some View {
        if !pass.isOver {
            PassCountdown(timer: pass.timer)
                .font(.title2.weight(.semibold))
                .foregroundStyle(DoormanWidgetStyle.coral)
                .frame(maxWidth: 88, alignment: .trailing)
        }
    }
}

private struct PassIslandBottom: View {
    let pass: PassDisplay

    var body: some View {
        if pass.isOver {
            Text(PassCopy.timeIsUp)
                .font(.subheadline)
                .foregroundStyle(DoormanWidgetStyle.secondaryText)
                .frame(maxWidth: .infinity, alignment: .leading)
        } else {
            VStack(alignment: .leading, spacing: 8) {
                Text("Pass: \(pass.reason)")
                    .font(.subheadline)
                    .foregroundStyle(.white)
                    .lineLimit(1)
                PassProgressBar(timer: pass.timer)
            }
        }
    }
}

private struct PassCompactTrailing: View {
    let pass: PassDisplay

    var body: some View {
        if pass.isOver {
            Image(systemName: "lock.fill")
                .foregroundStyle(DoormanWidgetStyle.coral)
        } else {
            PassCountdown(timer: pass.timer)
                .foregroundStyle(DoormanWidgetStyle.coral)
                .frame(maxWidth: 44)
        }
    }
}

// MARK: - Small parts

/// Counts down to the end of the pass. The system updates it every second.
private struct PassCountdown: View {
    let timer: ClosedRange<Date>

    var body: some View {
        Text(timerInterval: timer, countsDown: true)
            .monospacedDigit()
            .multilineTextAlignment(.trailing)
            .lineLimit(1)
    }
}

/// A bar that empties as the pass runs out.
private struct PassProgressBar: View {
    let timer: ClosedRange<Date>

    var body: some View {
        // Empty labels: the default label repeats the countdown under the bar.
        ProgressView(timerInterval: timer, countsDown: true) {
            EmptyView()
        } currentValueLabel: {
            EmptyView()
        }
        .tint(DoormanWidgetStyle.coral)
    }
}

private struct PassDoorIcon: View {
    let isOpen: Bool

    var body: some View {
        Image(systemName: DoormanWidgetStyle.doorSymbol(isOpen: isOpen))
            .foregroundStyle(DoormanWidgetStyle.coral)
    }
}

private struct PassDoorBadge: View {
    let isOpen: Bool

    var body: some View {
        Image(systemName: DoormanWidgetStyle.doorSymbol(isOpen: isOpen))
            .font(.system(size: 20, weight: .semibold))
            .foregroundStyle(isOpen ? DoormanWidgetStyle.coral : .white)
            .frame(width: 44, height: 44)
            .background(DoormanWidgetStyle.coral.opacity(isOpen ? 0.18 : 0.35), in: Circle())
    }
}
