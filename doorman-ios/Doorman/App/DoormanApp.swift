import SwiftUI

@main
struct DoormanApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(AppModel.shared)
                .environment(StoreManager.shared)
                .onOpenURL(perform: handle)
                .onChange(of: scenePhase, initial: true) { _, phase in
                    guard phase == .active else { return }
                    Task { await AppModel.shared.refresh() }
                }
        }
    }

    /// doorman://pass opens the pass screen (used by the shield and widgets).
    private func handle(_ url: URL) {
        guard url.scheme?.lowercased() == DoormanLink.scheme,
              url.host()?.lowercased() == "pass"
        else { return }
        AppModel.shared.presentPassRequest()
    }
}
