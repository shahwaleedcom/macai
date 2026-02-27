import Foundation

final class TelegramBotProcessManager: ObservableObject {
    @Published private(set) var isRunning = false

    private var process: Process?

    func start() {
        guard process == nil else { return }

        let scriptPath = Bundle.main.path(forResource: "telegram_bot", ofType: "py")
            ?? FileManager.default.currentDirectoryPath + "/Resources/telegram_bot.py"

        let pythonProcess = Process()
        pythonProcess.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        pythonProcess.arguments = [scriptPath]
        pythonProcess.currentDirectoryURL = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)

        var environment = ProcessInfo.processInfo.environment
        environment["PYTHONUNBUFFERED"] = "1"
        pythonProcess.environment = environment

        let outputPipe = Pipe()
        pythonProcess.standardOutput = outputPipe
        pythonProcess.standardError = outputPipe

        outputPipe.fileHandleForReading.readabilityHandler = { handle in
            let data = handle.availableData
            guard !data.isEmpty, let output = String(data: data, encoding: .utf8) else { return }
            print("[TelegramBot] \(output)", terminator: "")
        }

        pythonProcess.terminationHandler = { [weak self] _ in
            DispatchQueue.main.async {
                self?.cleanup()
            }
        }

        do {
            try pythonProcess.run()
            process = pythonProcess
            isRunning = true
        } catch {
            print("Failed to start Telegram bot process: \(error.localizedDescription)")
            cleanup()
        }
    }

    func stop() {
        guard let process else { return }
        process.terminate()
        cleanup()
    }

    private func cleanup() {
        process = nil
        isRunning = false
    }
}
