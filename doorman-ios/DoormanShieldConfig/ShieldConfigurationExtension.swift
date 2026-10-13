import ManagedSettings
import ManagedSettingsUI
import UIKit

/// Draws the screen people see when they open an app that is behind the door.
/// The system may keep this extension alive, so every value is read fresh
/// from the App Group on each call.
final class ShieldConfigurationExtension: ShieldConfigurationDataSource {
    override func configuration(shielding application: Application) -> ShieldConfiguration {
        makeConfiguration(appName: application.localizedDisplayName)
    }

    override func configuration(
        shielding application: Application,
        in category: ActivityCategory
    ) -> ShieldConfiguration {
        makeConfiguration(appName: application.localizedDisplayName)
    }

    override func configuration(shielding webDomain: WebDomain) -> ShieldConfiguration {
        makeConfiguration(appName: webDomain.domain)
    }

    override func configuration(
        shielding webDomain: WebDomain,
        in category: ActivityCategory
    ) -> ShieldConfiguration {
        makeConfiguration(appName: webDomain.domain)
    }

    // MARK: Building the shield

    /// How long after tapping "Ask Doorman" the shield points at the notification.
    private static let pendingRequestWindow: TimeInterval = 60

    private func makeConfiguration(appName: String?) -> ShieldConfiguration {
        ShieldConfiguration(
            backgroundBlurStyle: .systemUltraThinMaterialDark,
            backgroundColor: ShieldPalette.background,
            icon: Self.doorIcon,
            title: ShieldConfiguration.Label(text: title(appName: appName), color: ShieldPalette.title),
            subtitle: ShieldConfiguration.Label(text: subtitle(now: .now), color: ShieldPalette.subtitle),
            primaryButtonLabel: ShieldConfiguration.Label(
                text: ShieldCopy.primaryButton,
                color: ShieldPalette.primaryButtonText
            ),
            primaryButtonBackgroundColor: ShieldPalette.coral,
            secondaryButtonLabel: ShieldConfiguration.Label(
                text: ShieldCopy.secondaryButton,
                color: ShieldPalette.secondaryButtonText
            )
        )
    }

    private func title(appName: String?) -> String {
        guard let name = appName?.trimmingCharacters(in: .whitespacesAndNewlines), !name.isEmpty else {
            return ShieldCopy.title
        }
        return "\(name) is behind the door"
    }

    private func subtitle(now: Date) -> String {
        let store = SharedStore.shared

        // The user just tapped "Ask Doorman": show them where to go next.
        if let requestedAt = store.pendingRequestAt {
            let age = now.timeIntervalSince(requestedAt)
            if age >= 0, age < Self.pendingRequestWindow {
                return "Tap the Doorman notification above to ask."
            }
        }

        let phase = DoorPolicy.phase(
            at: now,
            settings: store.settings,
            hasIntentionToday: store.hasIntentionToday
        )
        return ShieldCopy.subtitle(
            context: store.context,
            attemptsToday: store.attemptCount(since: Calendar.current.startOfDay(for: now)),
            phase: phase,
            now: now
        )
    }

    private static var doorIcon: UIImage? {
        let config = UIImage.SymbolConfiguration(pointSize: 56, weight: .semibold)
        let symbol = UIImage(systemName: "door.left.hand.closed", withConfiguration: config)
            ?? UIImage(systemName: "lock.fill", withConfiguration: config)
        // Bake the color in; the shield does not tint icons for us.
        return symbol?.withTintColor(ShieldPalette.coral, renderingMode: .alwaysOriginal)
    }
}

/// Doorman's shield colors: dark glass with a coral accent.
private enum ShieldPalette {
    /// #FF4A5E
    static let coral = UIColor(red: 1, green: 74 / 255, blue: 94 / 255, alpha: 1)
    static let background = UIColor(red: 14 / 255, green: 14 / 255, blue: 18 / 255, alpha: 1)
    static let title = UIColor.white
    static let subtitle = UIColor(white: 1, alpha: 0.75)
    static let primaryButtonText = UIColor.white
    static let secondaryButtonText = UIColor(white: 0.62, alpha: 1)
}
