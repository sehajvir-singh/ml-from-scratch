import XCTest
@testable import DoormanCore

final class DoorPolicyTests: XCTestCase {
    private var calendar: Calendar = {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "UTC")!
        return cal
    }()

    private func date(_ hour: Int, _ minute: Int = 0) -> Date {
        calendar.date(from: DateComponents(year: 2026, month: 10, day: 13, hour: hour, minute: minute))!
    }

    func testWindowCrossingMidnight() {
        XCTAssertTrue(DoorPolicy.isInWindow(23 * 60 + 30, start: 23 * 60, end: 7 * 60))
        XCTAssertTrue(DoorPolicy.isInWindow(2 * 60, start: 23 * 60, end: 7 * 60))
        XCTAssertFalse(DoorPolicy.isInWindow(7 * 60, start: 23 * 60, end: 7 * 60))
        XCTAssertFalse(DoorPolicy.isInWindow(12 * 60, start: 23 * 60, end: 7 * 60))
        XCTAssertFalse(DoorPolicy.isInWindow(5, start: 5, end: 5))
    }

    func testWindowSameDay() {
        XCTAssertTrue(DoorPolicy.isInWindow(10 * 60, start: 9 * 60, end: 17 * 60))
        XCTAssertFalse(DoorPolicy.isInWindow(17 * 60, start: 9 * 60, end: 17 * 60))
    }

    func testPhases() {
        let settings = DoorSettings()
        XCTAssertEqual(DoorPolicy.phase(at: date(23, 30), settings: settings, hasIntentionToday: false, calendar: calendar), .night)
        XCTAssertEqual(DoorPolicy.phase(at: date(7, 30), settings: settings, hasIntentionToday: false, calendar: calendar), .morning)
        XCTAssertEqual(DoorPolicy.phase(at: date(7, 30), settings: settings, hasIntentionToday: true, calendar: calendar), .normal)
        XCTAssertEqual(DoorPolicy.phase(at: date(10, 30), settings: settings, hasIntentionToday: false, calendar: calendar), .normal)

        var off = settings
        off.nightDoorEnabled = false
        off.morningDoorEnabled = false
        XCTAssertEqual(DoorPolicy.phase(at: date(1), settings: off, hasIntentionToday: false, calendar: calendar), .normal)
    }

    func testClassify() {
        XCTAssertEqual(DoorPolicy.classify("reply to Maya"), .reply)
        XCTAssertEqual(DoorPolicy.classify("just checking"), .habit)
        XCTAssertEqual(DoorPolicy.classify("I'm bored"), .bored)
        XCTAssertEqual(DoorPolicy.classify("look up the restaurant address"), .lookup)
        XCTAssertEqual(DoorPolicy.classify("post my story"), .create)
        XCTAssertEqual(DoorPolicy.classify("client sent a brief"), .work)
        XCTAssertEqual(DoorPolicy.classify(""), .habit)
    }

    func testFallbackNormal() {
        let d = DoorPolicy.fallbackDecision(reason: "reply to Maya", phase: .normal, attemptsLastHour: 0, minutesUsedToday: 0, dailyBudgetMinutes: 60)
        XCTAssertEqual(d.category, .reply)
        XCTAssertEqual(d.minutes, 3)
        XCTAssertTrue(d.reply.contains("3 minutes"))
    }

    func testFallbackNightDeniesMindless() {
        let d = DoorPolicy.fallbackDecision(reason: "just checking", phase: .night, attemptsLastHour: 0, minutesUsedToday: 0, dailyBudgetMinutes: 60)
        XCTAssertEqual(d.minutes, 0)
        XCTAssertTrue(d.reply.contains("late"))
    }

    func testFallbackNightAllowsShortReply() {
        let d = DoorPolicy.fallbackDecision(reason: "reply to mom", phase: .night, attemptsLastHour: 0, minutesUsedToday: 0, dailyBudgetMinutes: 60)
        XCTAssertEqual(d.minutes, 1) // 2 minutes, halved because night is high risk
    }

    func testFallbackMorningNeedsTask() {
        let d = DoorPolicy.fallbackDecision(reason: "bored", phase: .morning, attemptsLastHour: 0, minutesUsedToday: 0, dailyBudgetMinutes: 60)
        XCTAssertEqual(d.minutes, 0)
        XCTAssertTrue(d.reply.contains("first task"))
    }

    func testFallbackOverBudget() {
        let mindless = DoorPolicy.fallbackDecision(reason: "scroll", phase: .normal, attemptsLastHour: 0, minutesUsedToday: 60, dailyBudgetMinutes: 60)
        XCTAssertEqual(mindless.minutes, 0)
        let work = DoorPolicy.fallbackDecision(reason: "client meeting notes", phase: .normal, attemptsLastHour: 0, minutesUsedToday: 60, dailyBudgetMinutes: 60)
        XCTAssertEqual(work.minutes, 2)
    }

    func testRisk() {
        XCTAssertEqual(DoorPolicy.risk(attemptsLastHour: 0, phase: .normal), .low)
        XCTAssertEqual(DoorPolicy.risk(attemptsLastHour: 4, phase: .normal), .medium)
        XCTAssertEqual(DoorPolicy.risk(attemptsLastHour: 9, phase: .normal), .high)
        XCTAssertEqual(DoorPolicy.risk(attemptsLastHour: 0, phase: .night), .high)
    }

    func testClamp() {
        XCTAssertEqual(DoorPolicy.clamp(-5), 0)
        XCTAssertEqual(DoorPolicy.clamp(99), DoorPolicy.maxPassMinutes)
    }

    func testMinutesUsed() {
        let today = date(12)
        let passes = [
            PassRecord(reason: "a", category: .reply, grantedMinutes: 3, requestedAt: date(9), expiresAt: date(9, 3), doorReply: ""),
            PassRecord(reason: "b", category: .work, grantedMinutes: 10, requestedAt: date(11), expiresAt: date(11, 10), doorReply: ""),
            PassRecord(reason: "c", category: .habit, grantedMinutes: 5, requestedAt: today.addingTimeInterval(-86_400), expiresAt: today, doorReply: ""),
        ]
        XCTAssertEqual(DoorPolicy.minutesUsed(on: today, passes: passes, calendar: calendar), 13)
    }
}

final class ShieldCopyTests: XCTestCase {
    func testOrdinal() {
        XCTAssertEqual(ShieldCopy.ordinal(1), "1st")
        XCTAssertEqual(ShieldCopy.ordinal(2), "2nd")
        XCTAssertEqual(ShieldCopy.ordinal(3), "3rd")
        XCTAssertEqual(ShieldCopy.ordinal(4), "4th")
        XCTAssertEqual(ShieldCopy.ordinal(11), "11th")
        XCTAssertEqual(ShieldCopy.ordinal(12), "12th")
        XCTAssertEqual(ShieldCopy.ordinal(13), "13th")
        XCTAssertEqual(ShieldCopy.ordinal(21), "21st")
        XCTAssertEqual(ShieldCopy.ordinal(112), "112th")
    }

    func testSubtitleWithEvent() {
        let now = Date(timeIntervalSince1970: 1_800_000_000)
        let ctx = ContextSnapshot(nextEventTitle: "Deck review", nextEventStart: now.addingTimeInterval(47 * 60))
        XCTAssertEqual(ShieldCopy.subtitle(context: ctx, attemptsToday: 5, phase: .normal, now: now), "Deck review in 47 min · 6th open today")
    }

    func testSubtitleHours() {
        let now = Date(timeIntervalSince1970: 1_800_000_000)
        let ctx = ContextSnapshot(nextEventTitle: "Gym", nextEventStart: now.addingTimeInterval(125 * 60))
        XCTAssertEqual(ShieldCopy.subtitle(context: ctx, attemptsToday: 0, phase: .normal, now: now), "Gym in 2 h 5 min · 1st open today")
    }

    func testSubtitlePastEventIgnored() {
        let now = Date(timeIntervalSince1970: 1_800_000_000)
        let ctx = ContextSnapshot(nextEventTitle: "Old", nextEventStart: now.addingTimeInterval(-60))
        XCTAssertEqual(ShieldCopy.subtitle(context: ctx, attemptsToday: 1, phase: .normal, now: now), "2nd open today")
    }

    func testSubtitleNight() {
        XCTAssertEqual(ShieldCopy.subtitle(context: nil, attemptsToday: 2, phase: .night), "Night door is on · 3rd open today")
    }
}

final class WrappedTests: XCTestCase {
    func testSummary() {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "UTC")!
        let end = cal.date(from: DateComponents(year: 2026, month: 10, day: 13, hour: 23))!
        func at(_ day: Int, _ hour: Int) -> Date { cal.date(from: DateComponents(year: 2026, month: 10, day: day, hour: hour))! }

        let attempts = [at(12, 22), at(12, 22), at(11, 22), at(10, 9), at(1, 22)]
        let passes = [
            PassRecord(reason: "x", category: .habit, grantedMinutes: 2, requestedAt: at(12, 22), expiresAt: at(12, 22), doorReply: "", honored: false),
            PassRecord(reason: "y", category: .reply, grantedMinutes: 3, requestedAt: at(11, 22), expiresAt: at(11, 22), doorReply: "", honored: true),
            PassRecord(reason: "z", category: .bored, grantedMinutes: 0, requestedAt: at(10, 9), expiresAt: at(10, 9), doorReply: ""),
            PassRecord(reason: "old", category: .work, grantedMinutes: 10, requestedAt: at(1, 9), expiresAt: at(1, 9), doorReply: ""),
        ]
        let s = WrappedSummary.make(attempts: attempts, passes: passes, endingAt: end, calendar: cal)
        XCTAssertEqual(s.attempts, 4)
        XCTAssertEqual(s.passes, 2)
        XCTAssertEqual(s.denied, 1)
        XCTAssertEqual(s.minutesGranted, 5)
        XCTAssertEqual(s.mindlessShare, 0.5, accuracy: 0.001)
        XCTAssertEqual(s.honestyRate ?? -1, 0.5, accuracy: 0.001)
        XCTAssertEqual(s.worstHour, 22)
    }

    func testEmpty() {
        let s = WrappedSummary.make(attempts: [], passes: [])
        XCTAssertEqual(s.attempts, 0)
        XCTAssertNil(s.worstHour)
        XCTAssertNil(s.honestyRate)
        XCTAssertEqual(s.mindlessShare, 0)
    }

    func testHourLabel() {
        XCTAssertEqual(WrappedSummary.hourLabel(0), "12am")
        XCTAssertEqual(WrappedSummary.hourLabel(9), "9am")
        XCTAssertEqual(WrappedSummary.hourLabel(12), "12pm")
        XCTAssertEqual(WrappedSummary.hourLabel(22), "10pm")
    }
}

final class SharedStoreTests: XCTestCase {
    func testRoundTrip() {
        let suite = "doorman.tests.\(UUID().uuidString)"
        let store = SharedStore(defaults: UserDefaults(suiteName: suite)!)
        XCTAssertEqual(store.settings, DoorSettings())

        var settings = store.settings
        settings.dailyBudgetMinutes = 42
        store.settings = settings
        XCTAssertEqual(store.settings.dailyBudgetMinutes, 42)

        let pass = PassRecord(reason: "reply", category: .reply, grantedMinutes: 3, requestedAt: .now, expiresAt: .now.addingTimeInterval(180), doorReply: "ok")
        store.appendPass(pass)
        store.setHonored(true, forPass: pass.id)
        XCTAssertEqual(store.passes.first?.honored, true)

        store.recordAttempt()
        store.recordAttempt()
        XCTAssertEqual(store.attemptCount(since: .now.addingTimeInterval(-60)), 2)

        store.activePassExpiry = .now.addingTimeInterval(-1)
        XCTAssertNil(store.activePassExpiry)
        store.activePassExpiry = .now.addingTimeInterval(60)
        XCTAssertNotNil(store.activePassExpiry)

        XCTAssertFalse(store.hasIntentionToday)
        store.morningIntention = MorningIntention(text: "Write report", setAt: .now)
        XCTAssertTrue(store.hasIntentionToday)
    }
}
