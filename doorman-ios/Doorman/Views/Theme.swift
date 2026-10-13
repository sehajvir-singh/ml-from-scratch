import SwiftUI

/// Doorman's look: near-black surfaces, one coral accent, big rounded type.
/// The colors match the shield and the widgets, so it all feels like one door.
enum Theme {
    /// #FF4A5E
    static let coral = Color(hex: 0xFF4A5E)
    static let coralSoft = Color(hex: 0xFF4A5E).opacity(0.14)
    static let background = Color(hex: 0x0E0E12)
    static let card = Color(hex: 0x18171E)
    static let cardRaised = Color(hex: 0x22212A)
    static let line = Color(hex: 0x2C2B35)
    static let text = Color(hex: 0xF4F2F6)
    static let secondaryText = Color(hex: 0xA19EAA)
    static let faintText = Color(hex: 0x6D6A76)
    static let good = Color(hex: 0x4FD18B)
    static let warn = Color(hex: 0xFFB547)
    static let violet = Color(hex: 0x785AFF)

    static let cornerRadius: CGFloat = 22
    /// Side padding for every screen.
    static let gutter: CGFloat = 20

    static func doorSymbol(isOpen: Bool) -> String {
        isOpen ? "door.left.hand.open" : "door.left.hand.closed"
    }

    /// "1 app" or "3 apps".
    static func count(_ number: Int, _ singular: String, _ plural: String) -> String {
        "\(number) \(number == 1 ? singular : plural)"
    }
}

extension Font {
    /// Screen titles like "Doorman" and "Why do you want in?".
    static let doormanLargeTitle = Font.system(.largeTitle, design: .rounded, weight: .heavy)
    static let doormanTitle = Font.system(.title, design: .rounded, weight: .bold)
    static let doormanTitle2 = Font.system(.title2, design: .rounded, weight: .bold)
    static let doormanHeadline = Font.system(.headline, design: .rounded, weight: .semibold)

    /// Big numbers in stats, the pass result and Wrapped.
    static func doormanNumber(_ size: CGFloat) -> Font {
        .system(size: size, weight: .heavy, design: .rounded)
    }
}

private extension Color {
    init(hex: UInt32) {
        self.init(
            red: Double((hex >> 16) & 0xFF) / 255,
            green: Double((hex >> 8) & 0xFF) / 255,
            blue: Double(hex & 0xFF) / 255
        )
    }
}

// MARK: - Cards and screens

/// The rounded dark panel every block on a screen sits on.
struct CardStyle: ViewModifier {
    var padding: CGFloat = 18
    var fill: Color = Theme.card

    func body(content: Content) -> some View {
        content
            .padding(padding)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(fill, in: RoundedRectangle(cornerRadius: Theme.cornerRadius, style: .continuous))
    }
}

extension View {
    func cardStyle(padding: CGFloat = 18, fill: Color = Theme.card) -> some View {
        modifier(CardStyle(padding: padding, fill: fill))
    }

    /// Full-bleed near-black background behind a screen.
    func doormanBackground() -> some View {
        background(Theme.background.ignoresSafeArea())
    }

    /// A dark text field with a soft border.
    func doormanField() -> some View {
        self
            .font(.system(.body, design: .rounded))
            .foregroundStyle(Theme.text)
            .padding(.horizontal, 16)
            .padding(.vertical, 15)
            .background(Theme.card, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .strokeBorder(Theme.line, lineWidth: 1)
            )
    }
}

// MARK: - Buttons

/// The big coral call to action: "Ask for a pass", "Close the door".
struct PrimaryButtonStyle: ButtonStyle {
    @Environment(\.isEnabled) private var isEnabled

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(.headline, design: .rounded, weight: .bold))
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity, minHeight: 58)
            .padding(.horizontal, 20)
            .background(
                Theme.coral.opacity(isEnabled ? 1 : 0.35),
                in: RoundedRectangle(cornerRadius: 18, style: .continuous)
            )
            .contentShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
            .opacity(configuration.isPressed ? 0.9 : 1)
            .animation(.spring(response: 0.25, dampingFraction: 0.7), value: configuration.isPressed)
    }
}

/// A calm, dark button for second choices: "Change apps", "Done".
struct SecondaryButtonStyle: ButtonStyle {
    @Environment(\.isEnabled) private var isEnabled

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(.headline, design: .rounded, weight: .semibold))
            .foregroundStyle(Theme.text.opacity(isEnabled ? 1 : 0.4))
            .frame(maxWidth: .infinity, minHeight: 54)
            .padding(.horizontal, 20)
            .background(Theme.cardRaised, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            .contentShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
            .animation(.spring(response: 0.25, dampingFraction: 0.7), value: configuration.isPressed)
    }
}

/// A small rounded pill button, for actions inside a card ("End pass").
struct CapsuleButtonStyle: ButtonStyle {
    var tint: Color = Theme.cardRaised

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(.subheadline, design: .rounded, weight: .semibold))
            .foregroundStyle(Theme.text)
            .padding(.horizontal, 14)
            .padding(.vertical, 9)
            .background(tint, in: Capsule())
            .contentShape(Capsule())
            .opacity(configuration.isPressed ? 0.7 : 1)
    }
}

extension ButtonStyle where Self == PrimaryButtonStyle {
    static var doormanPrimary: PrimaryButtonStyle { PrimaryButtonStyle() }
}

extension ButtonStyle where Self == SecondaryButtonStyle {
    static var doormanSecondary: SecondaryButtonStyle { SecondaryButtonStyle() }
}

extension ButtonStyle where Self == CapsuleButtonStyle {
    static var doormanCapsule: CapsuleButtonStyle { CapsuleButtonStyle() }
}

// MARK: - Small shared pieces

/// Small uppercase label above a group: "TODAY".
struct SectionLabel: View {
    let text: String

    init(_ text: String) {
        self.text = text
    }

    var body: some View {
        Text(text.uppercased())
            .font(.system(.caption, design: .rounded, weight: .semibold))
            .tracking(0.8)
            .foregroundStyle(Theme.faintText)
            .frame(maxWidth: .infinity, alignment: .leading)
    }
}

/// A rounded square with a symbol in it, used at the start of cards.
struct IconBadge: View {
    let systemName: String
    var tint: Color = Theme.coral
    var size: CGFloat = 44

    var body: some View {
        Image(systemName: systemName)
            .font(.system(size: size * 0.45, weight: .semibold))
            .foregroundStyle(tint)
            .frame(width: size, height: size)
            .background(tint.opacity(0.16), in: RoundedRectangle(cornerRadius: size * 0.3, style: .continuous))
            .accessibilityHidden(true)
    }
}

/// A tiny colored tag: "3 min", "Kept out", "Did it".
struct Pill: View {
    let text: String
    var systemImage: String?
    var tint: Color

    var body: some View {
        HStack(spacing: 4) {
            if let systemImage {
                Image(systemName: systemImage)
            }
            Text(text)
        }
        .font(.system(.caption, design: .rounded, weight: .bold))
        .foregroundStyle(tint)
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(tint.opacity(0.15), in: Capsule())
    }
}

/// A ring that fills from the top, clockwise. `progress` is 0...1.
struct ProgressRing: View {
    var progress: Double
    var lineWidth: CGFloat = 6
    var tint: Color = Theme.coral

    var body: some View {
        ZStack {
            Circle()
                .stroke(Theme.line, lineWidth: lineWidth)
            Circle()
                .trim(from: 0, to: min(max(progress, 0), 1))
                .stroke(tint, style: StrokeStyle(lineWidth: lineWidth, lineCap: .round))
                .rotationEffect(.degrees(-90))
        }
        .padding(lineWidth / 2)
    }
}

extension ReasonCategory {
    /// SF Symbol for lists and stats.
    var symbol: String {
        switch self {
        case .reply: "arrowshape.turn.up.left.fill"
        case .lookup: "magnifyingglass"
        case .work: "briefcase.fill"
        case .create: "camera.fill"
        case .habit: "hand.tap.fill"
        case .bored: "zzz"
        }
    }
}
