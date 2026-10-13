import Foundation
import EventKit
import os

/// Reads the next calendar event so the shield can say "Deck review in 47 min".
/// Writes the result to the App Group, where the shield extensions read it.
/// Calendar data never leaves the phone.
final class ContextProvider: @unchecked Sendable {
    static let shared = ContextProvider()

    /// Only events starting within this window are shown.
    static let lookahead: TimeInterval = 12 * 60 * 60

    private let store = EKEventStore()
    private let log = Logger(subsystem: "com.doorman.app", category: "Context")

    var isAuthorized: Bool {
        EKEventStore.authorizationStatus(for: .event) == .fullAccess
    }

    /// Asks for calendar access. Returns true if Doorman may read events.
    @discardableResult
    func requestAccess() async -> Bool {
        do {
            let granted = try await store.requestFullAccessToEvents()
            if granted { await refresh() }
            return granted
        } catch {
            log.error("Calendar access failed: \(error.localizedDescription, privacy: .public)")
            return false
        }
    }

    /// Saves the next timed event that has not started yet, or clears it.
    func refresh(now: Date = .now) async {
        guard isAuthorized else {
            // Without access (or after it was taken away) show no event at all.
            if SharedStore.shared.context?.nextEventTitle != nil {
                SharedStore.shared.context = ContextSnapshot(updatedAt: now)
            }
            return
        }

        let predicate = store.predicateForEvents(
            withStart: now,
            end: now.addingTimeInterval(Self.lookahead),
            calendars: nil
        )
        let next = store.events(matching: predicate)
            .compactMap { Upcoming(event: $0, after: now) }
            .min { $0.start < $1.start }

        SharedStore.shared.context = ContextSnapshot(
            nextEventTitle: next?.title,
            nextEventStart: next?.start,
            updatedAt: now
        )
    }
}

/// A timed, not cancelled event that starts after `now`.
private struct Upcoming {
    var title: String
    var start: Date

    init?(event: EKEvent, after now: Date) {
        // EventKit declares these as implicitly unwrapped, so bind them safely.
        guard !event.isAllDay,
              event.status != .canceled,
              let start = event.startDate,
              start > now
        else { return nil }

        let title = (event.title ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        self.title = title.isEmpty ? "Next event" : title
        self.start = start
    }
}
