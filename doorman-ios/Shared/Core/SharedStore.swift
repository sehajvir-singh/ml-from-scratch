import Foundation

/// Small key-value store in the App Group, shared by the app and all extensions.
/// Each value is JSON-encoded into the shared UserDefaults suite.
/// Extensions are separate processes, so always read fresh values; never cache.
final class SharedStore: @unchecked Sendable {
    static let shared = SharedStore()

    private let defaults: UserDefaults
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()
    private let lock = NSLock()

    init(defaults: UserDefaults = AppGroup.defaults) {
        self.defaults = defaults
    }

    private enum Key {
        static let settings = "settings.v1"
        static let passes = "passes.v1"
        static let attempts = "attempts.v1"
        static let context = "context.v1"
        static let activePassExpiry = "activePassExpiry.v1"
        static let pendingRequestAt = "pendingRequestAt.v1"
        static let intention = "morningIntention.v1"
        static let isPro = "isPro.v1"
    }

    // MARK: Generic helpers

    private func read<T: Decodable>(_ type: T.Type, _ key: String) -> T? {
        guard let data = defaults.data(forKey: key) else { return nil }
        return try? decoder.decode(T.self, from: data)
    }

    private func write<T: Encodable>(_ value: T?, _ key: String) {
        if let value, let data = try? encoder.encode(value) {
            defaults.set(data, forKey: key)
        } else {
            defaults.removeObject(forKey: key)
        }
    }

    private func mutate<T: Codable>(_ key: String, default value: T, _ change: (inout T) -> Void) {
        lock.lock(); defer { lock.unlock() }
        var current = read(T.self, key) ?? value
        change(&current)
        write(current, key)
    }

    // MARK: Settings

    var settings: DoorSettings {
        get { read(DoorSettings.self, Key.settings) ?? DoorSettings() }
        set { write(newValue, Key.settings) }
    }

    var isPro: Bool {
        get { defaults.bool(forKey: Key.isPro) }
        set { defaults.set(newValue, forKey: Key.isPro) }
    }

    // MARK: Passes

    var passes: [PassRecord] {
        read([PassRecord].self, Key.passes) ?? []
    }

    func appendPass(_ pass: PassRecord) {
        mutate(Key.passes, default: [PassRecord]()) { list in
            list.append(pass)
            // Keep about 60 days of history.
            let cutoff = Date.now.addingTimeInterval(-60 * 86_400)
            list.removeAll { $0.requestedAt < cutoff }
        }
    }

    func setHonored(_ honored: Bool, forPass id: UUID) {
        mutate(Key.passes, default: [PassRecord]()) { list in
            if let index = list.firstIndex(where: { $0.id == id }) {
                list[index].honored = honored
            }
        }
    }

    // MARK: Attempts (every time the shield's "Ask Doorman" button is tapped)

    var attempts: [Date] {
        read([Date].self, Key.attempts) ?? []
    }

    func recordAttempt(at date: Date = .now) {
        mutate(Key.attempts, default: [Date]()) { list in
            list.append(date)
            let cutoff = date.addingTimeInterval(-8 * 86_400)
            list.removeAll { $0 < cutoff }
        }
    }

    func attemptCount(since date: Date) -> Int {
        attempts.filter { $0 >= date }.count
    }

    // MARK: Context for the shield line

    var context: ContextSnapshot? {
        get { read(ContextSnapshot.self, Key.context) }
        set { write(newValue, Key.context) }
    }

    // MARK: Active pass

    /// When the current pass ends. nil = no pass, door is locked.
    var activePassExpiry: Date? {
        get {
            guard let date = defaults.object(forKey: Key.activePassExpiry) as? Date else { return nil }
            return date > .now ? date : nil
        }
        set { defaults.set(newValue, forKey: Key.activePassExpiry) }
    }

    /// Set by the shield action extension when the user taps "Ask Doorman".
    var pendingRequestAt: Date? {
        get { defaults.object(forKey: Key.pendingRequestAt) as? Date }
        set { defaults.set(newValue, forKey: Key.pendingRequestAt) }
    }

    // MARK: Morning door

    var morningIntention: MorningIntention? {
        get { read(MorningIntention.self, Key.intention) }
        set { write(newValue, Key.intention) }
    }

    /// True if an intention was set today.
    var hasIntentionToday: Bool {
        guard let intention = morningIntention else { return false }
        return Calendar.current.isDateInToday(intention.setAt)
    }
}
