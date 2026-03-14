# MacAI Menu Bar App

A macOS SwiftUI menu bar app that starts/stops a Python Telegram bot to control your MacBook.

## Features
- Menu bar status item with **Start AI** and **Stop AI** actions.
- Runs as an accessory app (no Dock icon).
- Launches `/usr/bin/python3` with an embedded `telegram_bot.py` script.
- Telegram commands for common Mac actions (lock, sleep, volume, open app, etc.).

## Setup
1. Install Python dependency:
   ```bash
   pip3 install python-telegram-bot
   ```
2. Export your bot token:
   ```bash
   export TELEGRAM_BOT_TOKEN="<your token>"
   ```
3. (Recommended) restrict control to your own chat ID:
   ```bash
   export TELEGRAM_ALLOWED_CHAT_ID="<numeric chat id>"
   ```
4. Build/run from Xcode or SwiftPM.

## Telegram Commands
Send any of these commands to your bot:
- `lock` or `lock screen`
- `sleep`
- `mute` / `unmute`
- `volume <0-100>`
- `open <Application Name>`
- `say <text>`
- `screenshot` (saves to `~/Desktop/telegram_screenshot.png`)
- `run <safe-shell-command>` (with basic safety blocking)

## Notes
- Voice messages are acknowledged but transcription is not wired yet.
- The `run` command blocks some obviously dangerous terms, but you should still keep `TELEGRAM_ALLOWED_CHAT_ID` set.
