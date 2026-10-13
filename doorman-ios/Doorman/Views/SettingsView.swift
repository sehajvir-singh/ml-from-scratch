import SwiftUI
import FamilyControls

/// Everything the user can change after onboarding.
struct SettingsView: View {
    @Environment(AppModel.self) private var model
    @Environment(StoreManager.self) private var store
    @Environment(\.openURL) private var openURL

    @State private var showPicker = false
    @State private var showPaywall = false
    @State private var isAskingScreenTime = false
    @State private var isRestoring = false
    @State private var restoreMessage: String?
    @State private var calendarOn = ContextProvider.shared.isAuthorized
    @State private var calendarAsked = false
    @State private var notificationsOn = false
    @State private var notificationsAsked = false

    var body: some View {
        @Bindable var model = model

        Form {
            doorSection
            appsSection
            nightSection(settings: $model.settings)
            morningSection(settings: $model.settings)
            budgetSection(settings: $model.settings)
            helpersSection
            proSection
            aboutSection
        }
        .scrollContentBackground(.hidden)
        .doormanBackground()
        .navigationTitle("Settings")
        .navigationBarTitleDisplayMode(.inline)
        .appPicker(isPresented: $showPicker)
        .sheet(isPresented: $showPaywall) {
            PaywallView()
        }
        .alert("Restore purchases", isPresented: showsRestoreMessage) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(restoreMessage ?? "")
        }
        .task {
            calendarOn = ContextProvider.shared.isAuthorized
            notificationsOn = await NotificationService.isAuthorized()
        }
    }

    // MARK: Door

    private var canCloseDoor: Bool {
        model.authorization == .approved && model.itemCount > 0
    }

    private var doorSection: some View {
        Section {
            Toggle(isOn: doorBinding) {
                Label("Doorman is on", systemImage: Theme.doorSymbol(isOpen: !model.settings.doorEnabled))
            }
            .disabled(!model.settings.doorEnabled && !canCloseDoor)

            if model.authorization != .approved {
                Button {
                    allowScreenTime()
                } label: {
                    Label("Allow Screen Time", systemImage: "hourglass")
                }
                .disabled(isAskingScreenTime)
            }
        } footer: {
            Text(doorFooter)
        }
        .listRowBackground(Theme.card)
    }

    private var doorBinding: Binding<Bool> {
        Binding(
            get: { model.settings.doorEnabled },
            set: { model.setDoorEnabled($0) }
        )
    }

    private var doorFooter: String {
        if model.authorization != .approved {
            return "Doorman needs Screen Time to lock your apps."
        }
        if model.itemCount == 0 {
            return "Pick at least one app to close the door."
        }
        return model.settings.doorEnabled
            ? "Your picked apps stay locked, except during a pass."
            : "The door is open. Your apps are not locked."
    }

    private func allowScreenTime() {
        isAskingScreenTime = true
        Task {
            defer { isAskingScreenTime = false }
            do {
                try await model.requestAuthorization()
            } catch {
                model.errorMessage = ScreenTimeCopy.message(for: error)
            }
        }
    }

    // MARK: Apps

    private var appsSection: some View {
        Section {
            Button {
                showPicker = true
            } label: {
                LabeledContent {
                    Text(pickedText)
                        .foregroundStyle(Theme.secondaryText)
                } label: {
                    Label("Edit apps", systemImage: "square.grid.2x2.fill")
                        .foregroundStyle(Theme.text)
                }
            }
            .disabled(model.authorization != .approved)
        } header: {
            Text("Apps behind the door")
        } footer: {
            if !model.isWithinLimit(model.selection) {
                Text("You have more than \(StoreManager.freeItemLimit) apps. Go Pro to keep them all, or pick fewer to save changes.")
            } else if !store.isPro {
                Text("Free plan: up to \(StoreManager.freeItemLimit) apps, categories or websites.")
            }
        }
        .listRowBackground(Theme.card)
    }

    private var pickedText: String {
        store.isPro
            ? "\(model.itemCount) picked"
            : "\(model.itemCount) of \(StoreManager.freeItemLimit)"
    }

    // MARK: Night and morning

    private func nightSection(settings: Binding<DoorSettings>) -> some View {
        Section {
            Toggle(isOn: settings.nightDoorEnabled) {
                Label("Night door", systemImage: "moon.stars.fill")
            }
            if settings.wrappedValue.nightDoorEnabled {
                if store.isPro {
                    ClockTimeRow("Starts", time: settings.nightStart)
                    ClockTimeRow("Ends", time: settings.nightEnd)
                } else {
                    Button {
                        showPaywall = true
                    } label: {
                        LabeledContent {
                            HStack(spacing: 6) {
                                Text("\(settings.wrappedValue.nightStart.formatted()) – \(settings.wrappedValue.nightEnd.formatted())")
                                Image(systemName: "lock.fill")
                                    .font(.caption)
                            }
                            .foregroundStyle(Theme.secondaryText)
                        } label: {
                            Text("Hours")
                                .foregroundStyle(Theme.text)
                        }
                    }
                }
            }
        } footer: {
            Text(store.isPro || !settings.wrappedValue.nightDoorEnabled
                 ? "At night only short, real reasons get in."
                 : "At night only short, real reasons get in. Pro lets you pick your own hours.")
        }
        .listRowBackground(Theme.card)
    }

    private func morningSection(settings: Binding<DoorSettings>) -> some View {
        Section {
            Toggle(isOn: settings.morningDoorEnabled) {
                Label("Morning door", systemImage: "sunrise.fill")
            }
        } footer: {
            Text("After you wake up, set your first task before any mindless scrolling.")
        }
        .listRowBackground(Theme.card)
    }

    private func budgetSection(settings: Binding<DoorSettings>) -> some View {
        Section {
            Stepper(value: settings.dailyBudgetMinutes, in: 15...240, step: 15) {
                LabeledContent("Daily budget", value: "\(settings.wrappedValue.dailyBudgetMinutes) min")
            }
        } footer: {
            Text("Pass minutes per day. When it's used up, only real tasks get in.")
        }
        .listRowBackground(Theme.card)
    }

    // MARK: Helpers

    private var helpersSection: some View {
        Section {
            PermissionRow(
                title: "Calendar",
                systemImage: "calendar",
                isOn: calendarOn,
                wasAsked: calendarAsked,
                allow: {
                    calendarOn = await ContextProvider.shared.requestAccess()
                    calendarAsked = true
                },
                openSettings: openAppSettings
            )
            PermissionRow(
                title: "Notifications",
                systemImage: "bell.badge.fill",
                isOn: notificationsOn,
                wasAsked: notificationsAsked,
                allow: {
                    notificationsOn = await NotificationService.requestAuthorization()
                    notificationsAsked = true
                },
                openSettings: openAppSettings
            )
        } header: {
            Text("Helpers")
        } footer: {
            Text("Calendar shows your next event on the block screen. Notifications let you tap “Ask Doorman”.")
        }
        .listRowBackground(Theme.card)
    }

    private func openAppSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            openURL(url)
        }
    }

    // MARK: Pro

    private var proSection: some View {
        Section {
            if store.isPro {
                Label {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Doorman Pro is on")
                        Text("Thank you for your support.")
                            .font(.footnote)
                            .foregroundStyle(Theme.secondaryText)
                    }
                } icon: {
                    Image(systemName: "checkmark.seal.fill")
                        .foregroundStyle(Theme.good)
                }
            } else {
                Button {
                    showPaywall = true
                } label: {
                    Label("Upgrade to Pro", systemImage: "sparkles")
                        .foregroundStyle(Theme.coral)
                }
            }
            Button {
                restore()
            } label: {
                HStack {
                    Text("Restore purchases")
                        .foregroundStyle(Theme.text)
                    Spacer()
                    if isRestoring {
                        ProgressView()
                    }
                }
            }
            .disabled(isRestoring)
        } header: {
            Text("Doorman Pro")
        } footer: {
            if !store.isPro {
                Text("Pro adds unlimited apps, Attention Wrapped and your own night hours.")
            }
        }
        .listRowBackground(Theme.card)
    }

    private var showsRestoreMessage: Binding<Bool> {
        Binding(
            get: { restoreMessage != nil },
            set: { if !$0 { restoreMessage = nil } }
        )
    }

    private func restore() {
        isRestoring = true
        Task {
            let hasPro = await store.restore()
            isRestoring = false
            restoreMessage = hasPro
                ? "Doorman Pro is on. Thank you!"
                : "We couldn't find Doorman Pro for this Apple Account."
        }
    }

    // MARK: About

    private var aboutSection: some View {
        Section {
            Label {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Everything stays on your iPhone.")
                    Text("No account, no server. Your apps, reasons and calendar never leave this phone.")
                        .font(.footnote)
                        .foregroundStyle(Theme.secondaryText)
                }
            } icon: {
                Image(systemName: "lock.shield.fill")
                    .foregroundStyle(Theme.good)
            }
            LabeledContent("Version", value: appVersion)
        }
        .listRowBackground(Theme.card)
    }

    private var appVersion: String {
        let info = Bundle.main.infoDictionary
        let version = info?["CFBundleShortVersionString"] as? String ?? "1.0"
        let build = info?["CFBundleVersion"] as? String ?? "1"
        return "\(version) (\(build))"
    }
}

// MARK: - Permission row

/// One optional permission: shows "On", an "Allow" button, or, once the user
/// said no, a way to Settings (iOS won't ask a second time).
private struct PermissionRow: View {
    let title: String
    let systemImage: String
    let isOn: Bool
    let wasAsked: Bool
    let allow: () async -> Void
    let openSettings: () -> Void

    @State private var isAsking = false

    var body: some View {
        LabeledContent {
            if isOn {
                Text("On")
                    .foregroundStyle(Theme.good)
            } else if wasAsked {
                Button("Open Settings", action: openSettings)
                    .buttonStyle(.doormanCapsule)
            } else {
                Button("Allow") {
                    isAsking = true
                    Task {
                        await allow()
                        isAsking = false
                    }
                }
                .buttonStyle(.doormanCapsule)
                .disabled(isAsking)
            }
        } label: {
            Label(title, systemImage: systemImage)
        }
    }
}

// MARK: - Screen Time errors

enum ScreenTimeCopy {
    /// A friendly line for an error from `AppModel.requestAuthorization()`.
    static func message(for error: Error) -> String {
        if let error = error as? FamilyControlsError {
            switch error {
            case .restricted:
                return "Screen Time is limited on this iPhone, for example by a parent or school."
            case .authenticationMethodUnavailable:
                return "Set a passcode for this iPhone first, then try again."
            case .invalidAccountType:
                return "Sign in to iCloud on this iPhone first, then try again."
            case .networkError:
                return "Check your internet connection and try again."
            case .authorizationConflict:
                return "Another app is managing Screen Time right now. Try again later."
            default:
                break
            }
        }
        return "Doorman can't lock apps without Screen Time. You can try again anytime."
    }
}

// MARK: - Night door times

extension ClockTime {
    init(date: Date, calendar: Calendar = .current) {
        let parts = calendar.dateComponents([.hour, .minute], from: date)
        self.init(hour: parts.hour ?? 0, minute: parts.minute ?? 0)
    }

    /// This hour and minute on `day`, for pickers.
    func date(on day: Date = .now, calendar: Calendar = .current) -> Date {
        calendar.date(bySettingHour: hour, minute: minute, second: 0, of: day) ?? day
    }
}

/// An hour-and-minute picker for a `ClockTime`. Changes are saved a moment
/// after the wheel stops, so the night schedule restarts once, not on every tick.
struct ClockTimeRow: View {
    private let title: String
    @Binding private var time: ClockTime
    @State private var draft: Date
    @State private var saveTask: Task<Void, Never>?

    init(_ title: String, time: Binding<ClockTime>) {
        self.title = title
        _time = time
        _draft = State(initialValue: time.wrappedValue.date())
    }

    var body: some View {
        DatePicker(title, selection: $draft, displayedComponents: .hourAndMinute)
            .onChange(of: draft) { _, newValue in
                saveTask?.cancel()
                saveTask = Task {
                    try? await Task.sleep(nanoseconds: 700_000_000)
                    guard !Task.isCancelled else { return }
                    let picked = ClockTime(date: newValue)
                    if picked != time { time = picked }
                }
            }
            .onChange(of: time) { _, newValue in
                if ClockTime(date: draft) != newValue {
                    draft = newValue.date()
                }
            }
    }
}

// MARK: - App picker with the free limit

/// Opens Apple's app picker and keeps free users within the free limit.
/// Picks over the limit are held back while the paywall is open. If the user
/// goes Pro there, they are saved; otherwise the old picks stay.
struct AppPickerModifier: ViewModifier {
    @Binding var isPresented: Bool

    @Environment(AppModel.self) private var model
    @State private var draft = FamilyActivitySelection()
    @State private var showPaywall = false

    func body(content: Content) -> some View {
        content
            .familyActivityPicker(isPresented: $isPresented, selection: $draft)
            .onChange(of: isPresented) { _, shown in
                if shown {
                    draft = model.selection
                } else {
                    // Let the picker finish writing the selection first.
                    Task { pickerDidClose() }
                }
            }
            .sheet(isPresented: $showPaywall, onDismiss: paywallDidClose) {
                PaywallView()
            }
    }

    private func pickerDidClose() {
        guard draft != model.selection else { return }
        if model.updateSelection(draft) { return }
        // Two sheets can't overlap, so wait until the picker has slid away.
        Task {
            try? await Task.sleep(nanoseconds: 600_000_000)
            showPaywall = true
        }
    }

    private func paywallDidClose() {
        if !model.updateSelection(draft) {
            draft = model.selection
        }
    }
}

extension View {
    /// Apple's app picker, saving to `AppModel` and enforcing the free limit.
    func appPicker(isPresented: Binding<Bool>) -> some View {
        modifier(AppPickerModifier(isPresented: isPresented))
    }
}
