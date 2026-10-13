import SwiftUI
import WidgetKit

@main
struct DoormanWidgetsBundle: WidgetBundle {
    var body: some Widget {
        AttentionWidget()
        PassLiveActivity()
    }
}

/// Colors, icons and links shared by the widget and the Live Activity.
/// The colors match the shield screen, so the whole app feels like one door.
enum DoormanWidgetStyle {
    /// #FF4A5E
    static let coral = Color(red: 1, green: 74 / 255, blue: 94 / 255)
    /// #0E0E12, the shield's background.
    static let night = Color(red: 14 / 255, green: 14 / 255, blue: 18 / 255)
    /// #1C1C24, the top of the home screen card.
    static let card = Color(red: 28 / 255, green: 28 / 255, blue: 36 / 255)
    static let secondaryText = Color.white.opacity(0.65)

    static let doorClosedSymbol = "door.left.hand.closed"
    static let doorOpenSymbol = "door.left.hand.open"

    /// Opens Doorman's main screen. Widgets never open the pass screen directly:
    /// asking for a pass should start at the door, not from a shortcut.
    static let homeURL = URL(string: "doorman://home")

    static func doorSymbol(isOpen: Bool) -> String {
        isOpen ? doorOpenSymbol : doorClosedSymbol
    }
}
