# MacAI Menu Bar App

A macOS SwiftUI menu bar app that starts/stops a Python Telegram voice-control bot in the background.

## Features
- Menu bar status item with **Start AI** and **Stop AI** actions.
- Runs as an accessory app (no Dock icon).
- Launches `/usr/bin/python3` with an embedded `telegram_bot.py` script.

## Setup
1. Install Python dependency:
   ```bash
   pip3 install python-telegram-bot
   ```
2. Export your bot token:
   ```bash
   export TELEGRAM_BOT_TOKEN="<your token>"
   ```
3. Build/run from Xcode or SwiftPM.

## Notes
- Voice messages are currently acknowledged and routed as a placeholder hook in `telegram_bot.py`.
- You can extend the Python script with speech-to-text + command execution logic.
Test sync working