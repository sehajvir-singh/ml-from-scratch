import Foundation
import Observation
import StoreKit
import os

/// Doorman Pro with StoreKit 2. `isPro` is mirrored into the App Group so the
/// extensions and widgets can read it without StoreKit.
@MainActor
@Observable
final class StoreManager {
    static let shared = StoreManager()

    /// Free users may put this many apps, categories or websites behind the door.
    static let freeItemLimit = 3
    static let productIDs = ["doorman.pro.yearly", "doorman.pro.monthly", "doorman.pro.lifetime"]

    private static let log = Logger(subsystem: "com.doorman.app", category: "Store")

    /// Sorted in the order of `productIDs`.
    private(set) var products: [Product] = []
    private(set) var isPro: Bool = SharedStore.shared.isPro

    @ObservationIgnored private var updatesTask: Task<Void, Never>?

    private init() {
        // Purchases can finish outside the app (renewals, Ask to Buy, other devices).
        updatesTask = Task.detached(priority: .background) { [weak self] in
            for await result in StoreKit.Transaction.updates {
                await self?.handle(result)
            }
        }
        Task { await updateEntitlements() }
    }

    func loadProducts() async {
        do {
            let loaded = try await Product.products(for: Self.productIDs)
            products = loaded.sorted { rank($0) < rank($1) }
        } catch {
            Self.log.error("Could not load products: \(error.localizedDescription, privacy: .public)")
        }
    }

    /// Returns true when the purchase went through. Cancelled or pending
    /// (for example waiting for a parent's approval) returns false.
    func purchase(_ product: Product) async throws -> Bool {
        let result = try await product.purchase()
        switch result {
        case .success(let verification):
            guard case .verified(let transaction) = verification else { return false }
            await transaction.finish()
            await updateEntitlements()
            return true
        case .userCancelled, .pending:
            return false
        @unknown default:
            return false
        }
    }

    /// Syncs purchases with the App Store. Returns true if Pro is active afterwards.
    @discardableResult
    func restore() async -> Bool {
        do {
            try await AppStore.sync()
        } catch {
            Self.log.error("Restore failed: \(error.localizedDescription, privacy: .public)")
        }
        await updateEntitlements()
        return isPro
    }

    /// Recomputes `isPro` from verified, unrevoked entitlements.
    func updateEntitlements() async {
        var hasPro = false
        for await result in StoreKit.Transaction.currentEntitlements {
            guard case .verified(let transaction) = result,
                  Self.productIDs.contains(transaction.productID),
                  transaction.revocationDate == nil
            else { continue }
            hasPro = true
        }
        isPro = hasPro
        SharedStore.shared.isPro = hasPro
    }

    private func handle(_ result: VerificationResult<StoreKit.Transaction>) async {
        guard case .verified(let transaction) = result else { return }
        await transaction.finish()
        await updateEntitlements()
    }

    private func rank(_ product: Product) -> Int {
        Self.productIDs.firstIndex(of: product.id) ?? Self.productIDs.count
    }
}
