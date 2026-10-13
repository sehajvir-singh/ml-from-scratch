// swift-tools-version:5.10
// Swift package for the platform-independent core, so its logic can be
// unit tested with `swift test` (also on Linux CI). The iOS app itself is
// built from Doorman.xcodeproj, which is generated from project.yml.
import PackageDescription

let package = Package(
    name: "DoormanCore",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "DoormanCore", targets: ["DoormanCore"]),
    ],
    targets: [
        .target(name: "DoormanCore", path: "Shared/Core"),
        .testTarget(name: "DoormanCoreTests", dependencies: ["DoormanCore"], path: "Tests/CoreTests"),
    ]
)
