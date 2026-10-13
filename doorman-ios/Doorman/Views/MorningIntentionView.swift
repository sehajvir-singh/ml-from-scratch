import SwiftUI

/// The morning door: one real task before any mindless scrolling.
/// Shown as a sheet from home, or inline on the pass screen (pass `onDone`).
struct MorningIntentionView: View {
    /// Called after the task is saved. When nil, the view dismisses itself.
    var onDone: (() -> Void)?
    /// Shown under the button when set, for example "Skip for now" on the pass screen.
    var skipTitle: String?
    var onSkip: (() -> Void)?

    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss

    @State private var text = ""
    @State private var savedCount = 0
    @FocusState private var isFocused: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            IconBadge(systemName: "sunrise.fill", tint: Theme.warn, size: 56)

            VStack(alignment: .leading, spacing: 8) {
                Text("Good morning")
                    .font(.system(.subheadline, design: .rounded, weight: .semibold))
                    .foregroundStyle(Theme.secondaryText)
                Text("What's your first task today?")
                    .font(.doormanTitle)
                    .foregroundStyle(Theme.text)
                    .fixedSize(horizontal: false, vertical: true)
                Text("Pick one real thing. Until it's set, “just checking” stays outside.")
                    .font(.subheadline)
                    .foregroundStyle(Theme.secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
            }

            TextField("For example: finish the deck", text: $text)
                .doormanField()
                .focused($isFocused)
                .submitLabel(.done)
                .onSubmit(save)

            VStack(spacing: 10) {
                Button("Set my first task", action: save)
                    .buttonStyle(.doormanPrimary)
                    .disabled(trimmedText.isEmpty)

                if let skipTitle, let onSkip {
                    Button(skipTitle, action: onSkip)
                        .font(.system(.subheadline, design: .rounded, weight: .medium))
                        .foregroundStyle(Theme.secondaryText)
                        .frame(maxWidth: .infinity, minHeight: 44)
                }
            }
        }
        .sensoryFeedback(.success, trigger: savedCount)
        .onAppear {
            // Edit today's task if there already is one.
            if text.isEmpty, let current = model.morningIntention?.text {
                text = current
            }
        }
    }

    private var trimmedText: String {
        text.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private func save() {
        guard !trimmedText.isEmpty else { return }
        model.setMorningIntention(trimmedText)
        isFocused = false
        savedCount += 1
        if let onDone {
            onDone()
        } else {
            dismiss()
        }
    }
}

/// MorningIntentionView in its own sheet, with a close button.
struct MorningIntentionSheet: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            MorningIntentionView()
                .padding(.horizontal, Theme.gutter)
                .padding(.top, 8)
                .padding(.bottom, 24)
        }
        .scrollDismissesKeyboard(.interactively)
        .safeAreaInset(edge: .top) {
            HStack {
                Spacer()
                Button {
                    dismiss()
                } label: {
                    Image(systemName: "xmark")
                        .font(.system(size: 15, weight: .bold))
                        .foregroundStyle(Theme.secondaryText)
                        .frame(width: 34, height: 34)
                        .background(Theme.cardRaised, in: Circle())
                }
                .accessibilityLabel("Close")
            }
            .padding(.horizontal, Theme.gutter)
            .padding(.top, 16)
        }
        .doormanBackground()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
        .presentationBackground(Theme.background)
        .preferredColorScheme(.dark)
    }
}
