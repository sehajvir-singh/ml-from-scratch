import SwiftUI

/// First screen: onboarding until it is done, then home.
/// Also hosts the pass screen, which can open from anywhere
/// (the "Ask Doorman" notification, a deep link, or the home button).
struct RootView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model

        Group {
            if model.settings.hasCompletedOnboarding {
                HomeView()
                    .transition(.opacity)
            } else {
                OnboardingView()
                    .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.4), value: model.settings.hasCompletedOnboarding)
        .sheet(isPresented: $model.isPassRequestPresented) {
            PassRequestView()
        }
        .alert("Something went wrong", isPresented: showsError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(model.errorMessage ?? "")
        }
        .tint(Theme.coral)
        .preferredColorScheme(.dark)
        .task { await model.refresh() }
    }

    private var showsError: Binding<Bool> {
        Binding(
            get: { model.errorMessage != nil },
            set: { if !$0 { model.errorMessage = nil } }
        )
    }
}
