// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "macai",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "MacAI", targets: ["MacAI"])
    ],
    targets: [
        .executableTarget(
            name: "MacAI",
            path: "Sources/MacAI",
            resources: [
                .copy("Resources/telegram_bot.py")
            ]
        )
    ]
)
