import SwiftUI
import AppKit

@main
struct MacAIMenuBarApp: App {
    @StateObject private var botManager = TelegramBotProcessManager()

    init() {
        NSApplication.shared.setActivationPolicy(.accessory)
    }

    var body: some Scene {
        MenuBarExtra("MacAI", systemImage: botManager.isRunning ? "waveform.circle.fill" : "waveform.circle") {
            VStack(alignment: .leading, spacing: 8) {
                Text(botManager.isRunning ? "AI is running" : "AI is stopped")
                    .font(.headline)

                Button("Start AI") {
                    botManager.start()
                }
                .disabled(botManager.isRunning)

                Button("Stop AI") {
                    botManager.stop()
                }
                .disabled(!botManager.isRunning)

                Divider()

                Button("Quit") {
                    NSApplication.shared.terminate(nil)
                }
            }
            .padding(8)
            .frame(width: 210)
        }
        .menuBarExtraStyle(.window)
    }
}
