import Foundation
import ActivityKit
import WidgetKit
import os

/// Runs one trip through the door: judge the reason, open the apps,
/// start the countdown, and plan the honesty check.
@MainActor
enum PassService {
    private static let log = Logger(subsystem: "com.doorman.app", category: "Pass")

    /// Asks the judge for a pass and, if granted, unlocks the apps.
    /// Always returns a record; `grantedMinutes == 0` means denied.
    static func request(reason: String, now: Date = .now) async -> PassRecord {
        let store = SharedStore.shared
        let reason = reason.trimmingCharacters(in: .whitespacesAndNewlines)
        let settings = store.settings
        store.pendingRequestAt = nil

        guard settings.doorEnabled else {
            // Nothing to unlock. Not saved, so it does not count as a denial.
            return PassRecord(
                reason: reason,
                category: DoorPolicy.classify(reason),
                grantedMinutes: 0,
                requestedAt: now,
                expiresAt: now,
                doorReply: "Doorman is off, so your apps are already open."
            )
        }

        let input = makeInput(store: store, settings: settings, now: now)
        var decision = await PassJudge().decide(reason: reason, input: input)

        let requestedAt = Date.now
        var expiresAt = requestedAt
        if decision.minutes > 0 {
            do {
                expiresAt = try ShieldManager().grantPass(minutes: decision.minutes, now: requestedAt)
            } catch {
                log.error("Could not open the door: \(error.localizedDescription, privacy: .public)")
                decision = PassDecision(
                    minutes: 0,
                    category: decision.category,
                    reply: "Sorry, the door is stuck. Please try again in a moment."
                )
            }
        }

        let pass = PassRecord(
            reason: reason,
            category: decision.category,
            grantedMinutes: decision.minutes,
            requestedAt: requestedAt,
            expiresAt: expiresAt,
            doorReply: decision.reply
        )
        store.appendPass(pass)

        if !pass.wasDenied {
            // A new pass replaces any countdown still showing.
            await endAllActivities()
            startActivity(for: pass)
            // "Did you just check?" is not a useful question, so mindless passes skip it.
            if !pass.category.isMindless {
                NotificationService.scheduleHonesty(for: pass)
            }
        }

        WidgetCenter.shared.reloadAllTimelines()
        return pass
    }

    /// Ends the current pass early and locks the apps again.
    static func endPassNow() {
        if SharedStore.shared.settings.doorEnabled {
            ShieldManager().endPass()
        }
        NotificationService.cancelHonesty()
        WidgetCenter.shared.reloadAllTimelines()
        Task { await endAllActivities() }
    }

    // MARK: Live Activity

    /// Ends countdowns for passes that are over, including passes the night
    /// door cut short (the monitor clears the active pass when night starts).
    static func endExpiredActivities(now: Date = .now) async {
        let passIsRunning = SharedStore.shared.activePassExpiry != nil
        for activity in Activity<PassActivityAttributes>.activities
        where !passIsRunning || activity.content.state.expiresAt <= now {
            await activity.end(nil, dismissalPolicy: .immediate)
        }
    }

    static func endAllActivities() async {
        for activity in Activity<PassActivityAttributes>.activities {
            await activity.end(nil, dismissalPolicy: .immediate)
        }
    }

    private static func startActivity(for pass: PassRecord) {
        guard ActivityAuthorizationInfo().areActivitiesEnabled else { return }
        let attributes = PassActivityAttributes(
            reason: pass.reason.isEmpty ? pass.category.label : pass.reason,
            category: pass.category.rawValue
        )
        let state = PassActivityAttributes.ContentState(startedAt: pass.requestedAt, expiresAt: pass.expiresAt)
        let content = ActivityContent(state: state, staleDate: pass.expiresAt)
        do {
            _ = try Activity<PassActivityAttributes>.request(attributes: attributes, content: content, pushType: nil)
        } catch {
            log.error("Could not start the Live Activity: \(error.localizedDescription, privacy: .public)")
        }
    }

    // MARK: Helpers

    private static func makeInput(store: SharedStore, settings: DoorSettings, now: Date) -> PassJudge.Input {
        let passes = store.passes
        let attempts = store.attempts
        return PassJudge.Input(
            phase: DoorPolicy.phase(at: now, settings: settings, hasIntentionToday: store.hasIntentionToday),
            attemptsLastHour: attempts.filter { $0 >= now.addingTimeInterval(-3600) }.count,
            minutesUsedToday: DoorPolicy.minutesUsed(on: now, passes: passes),
            dailyBudgetMinutes: settings.dailyBudgetMinutes,
            eventLine: ShieldCopy.eventLine(context: store.context, now: now),
            honestyRate: WrappedSummary.make(attempts: attempts, passes: passes, endingAt: now).honestyRate
        )
    }
}
