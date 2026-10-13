import SwiftUI
import StoreKit

/// Doorman Pro: Apple's subscription store under a short list of benefits,
/// plus the one-time lifetime option when it has loaded.
/// Closes itself as soon as Pro becomes active.
struct PaywallView: View {
    /// Must match `StoreManager.productIDs`.
    static let subscriptionIDs = ["doorman.pro.yearly", "doorman.pro.monthly"]
    static let lifetimeID = "doorman.pro.lifetime"

    @Environment(StoreManager.self) private var store
    @Environment(\.dismiss) private var dismiss

    @State private var isRestoring = false
    @State private var showsNothingToRestore = false

    var body: some View {
        NavigationStack {
            SubscriptionStoreView(productIDs: Self.subscriptionIDs) {
                PaywallHeader(lifetime: lifetime)
            }
            .subscriptionStoreControlStyle(.prominentPicker)
            .subscriptionStoreButtonLabel(.multiline)
            .storeButton(.visible, for: .policies)
            // The toolbar has our own Close and Restore, which also refresh `isPro`.
            .storeButton(.hidden, for: .cancellation)
            .storeButton(.hidden, for: .restorePurchases)
            .containerBackground(Theme.background, for: .subscriptionStoreFullHeight)
            .onInAppPurchaseCompletion { _, result in
                await finish(result)
            }
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") { dismiss() }
                }
                ToolbarItem(placement: .primaryAction) {
                    Button("Restore") { restore() }
                        .disabled(isRestoring)
                }
            }
        }
        .tint(Theme.coral)
        .preferredColorScheme(.dark)
        .task {
            if lifetime == nil { await store.loadProducts() }
        }
        .onChange(of: store.isPro) { _, isPro in
            if isPro { dismiss() }
        }
        .alert("Nothing to restore", isPresented: $showsNothingToRestore) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("We couldn't find Doorman Pro for this Apple Account.")
        }
    }

    private var lifetime: Product? {
        store.products.first { $0.id == Self.lifetimeID }
    }

    /// Finishes a verified purchase and refreshes `isPro`, which closes the paywall.
    private func finish(_ result: Result<Product.PurchaseResult, any Error>) async {
        if case .success(.success(let verification)) = result,
           case .verified(let transaction) = verification {
            await transaction.finish()
        }
        await store.updateEntitlements()
    }

    private func restore() {
        isRestoring = true
        Task {
            let hasPro = await store.restore()
            isRestoring = false
            if !hasPro { showsNothingToRestore = true }
        }
    }
}

/// The top of the paywall: what Pro gives you.
private struct PaywallHeader: View {
    let lifetime: Product?

    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            IconBadge(systemName: Theme.doorSymbol(isOpen: false), size: 64)

            VStack(alignment: .leading, spacing: 8) {
                Text("Doorman Pro")
                    .font(.doormanLargeTitle)
                    .foregroundStyle(Theme.text)
                Text("A stronger door for your attention.")
                    .font(.system(.title3, design: .rounded))
                    .foregroundStyle(Theme.secondaryText)
            }

            VStack(alignment: .leading, spacing: 16) {
                Benefit(symbol: "square.stack.3d.up.fill", title: "Unlimited apps", detail: "Put every distraction behind the door.")
                Benefit(symbol: "sparkles", title: "Attention Wrapped", detail: "Your week in one card. Share it if you dare.")
                Benefit(symbol: "moon.stars.fill", title: "Your night hours", detail: "Pick when the night door starts and ends.")
                Benefit(symbol: "lock.shield.fill", title: "Still 100% private", detail: "Everything stays on your iPhone.")
            }

            if let lifetime {
                VStack(alignment: .leading, spacing: 10) {
                    SectionLabel("Or pay once")
                    ProductView(lifetime)
                        .productViewStyle(.compact)
                        .cardStyle(padding: 14)
                }
            }
        }
        .padding(.horizontal, Theme.gutter)
        .padding(.top, 8)
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct Benefit: View {
    let symbol: String
    let title: String
    let detail: String

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            Image(systemName: symbol)
                .font(.system(size: 18, weight: .semibold))
                .foregroundStyle(Theme.coral)
                .frame(width: 28)
                .accessibilityHidden(true)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.doormanHeadline)
                    .foregroundStyle(Theme.text)
                Text(detail)
                    .font(.subheadline)
                    .foregroundStyle(Theme.secondaryText)
            }
        }
    }
}
