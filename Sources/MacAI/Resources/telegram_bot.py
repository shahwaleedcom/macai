#!/usr/bin/env python3
"""
Telegram bot for controlling a MacBook.

Required environment variables:
  TELEGRAM_BOT_TOKEN=<your bot token>

Optional environment variables:
  TELEGRAM_ALLOWED_CHAT_ID=<numeric chat id allowed to issue commands>
"""

import asyncio
import logging
import os
import shlex
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


ALLOWED_CHAT_ID = os.environ.get("TELEGRAM_ALLOWED_CHAT_ID")


def _is_allowed_chat(update: Update) -> bool:
    if ALLOWED_CHAT_ID is None:
        return True
    chat = update.effective_chat
    return chat is not None and str(chat.id) == ALLOWED_CHAT_ID


def _run_command(command: list[str], timeout: int = 10) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if completed.returncode == 0:
            output = (completed.stdout or "").strip()
            return True, output or "Done."
        error = (completed.stderr or completed.stdout or "Unknown error").strip()
        return False, error
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _execute_mac_command(raw_text: str) -> tuple[bool, str]:
    text = raw_text.strip()
    lower = text.lower()

    if lower in {"lock", "lock screen"}:
        return _run_command([
            "osascript",
            "-e",
            'tell application "System Events" to keystroke "q" using {control down, command down}',
        ])

    if lower in {"sleep", "sleep now"}:
        return _run_command(["pmset", "sleepnow"])

    if lower in {"mute", "mute volume"}:
        return _run_command(["osascript", "-e", "set volume with output muted"])

    if lower in {"unmute", "unmute volume"}:
        return _run_command(["osascript", "-e", "set volume without output muted"])

    if lower.startswith("volume "):
        amount = lower.removeprefix("volume ").strip()
        if not amount.isdigit():
            return False, "Usage: volume <0-100>"
        value = int(amount)
        if value < 0 or value > 100:
            return False, "Volume must be between 0 and 100."
        return _run_command(["osascript", "-e", f"set volume output volume {value}"])

    if lower.startswith("say "):
        phrase = text[4:].strip()
        if not phrase:
            return False, "Usage: say <message>"
        return _run_command(["say", phrase])

    if lower.startswith("open "):
        app_name = text[5:].strip()
        if not app_name:
            return False, "Usage: open <application name>"
        return _run_command(["open", "-a", app_name])

    if lower in {"screenshot", "screencap"}:
        path = os.path.expanduser("~/Desktop/telegram_screenshot.png")
        return _run_command(["screencapture", "-x", path])

    if lower.startswith("run "):
        shell_cmd = text[4:].strip()
        if not shell_cmd:
            return False, "Usage: run <safe-shell-command>"

        # Minimal safety guard: block obvious high-risk commands.
        blocked_terms = [
            " rm ",
            "sudo ",
            "shutdown",
            "reboot",
            "mkfs",
            ":(){",
            " dd ",
        ]
        check_target = f" {shell_cmd.lower()} "
        if any(term in check_target for term in blocked_terms):
            return False, "Blocked potentially dangerous command."

        try:
            parts = shlex.split(shell_cmd)
        except ValueError as exc:
            return False, f"Invalid command syntax: {exc}"

        if not parts:
            return False, "Usage: run <safe-shell-command>"

        return _run_command(parts, timeout=20)

    return False, (
        "Unknown command. Try: lock, sleep, mute, unmute, volume <0-100>, "
        "open <App>, say <text>, screenshot, run <cmd>."
    )


async def _reject_if_not_allowed(update: Update) -> bool:
    if _is_allowed_chat(update):
        return False
    if update.message:
        await update.message.reply_text("Unauthorized chat.")
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_not_allowed(update):
        return

    await update.message.reply_text(
        "MacAI bot online. Send commands like:\n"
        "- lock\n"
        "- sleep\n"
        "- volume 30\n"
        "- open Safari\n"
        "- say hello"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_not_allowed(update):
        return

    await update.message.reply_text(
        "Commands:\n"
        "lock | sleep | mute | unmute\n"
        "volume <0-100>\n"
        "open <Application Name>\n"
        "say <text>\n"
        "screenshot\n"
        "run <safe-shell-command>"
    )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_not_allowed(update):
        return

    await update.message.reply_text(
        "Voice received, but transcription is not configured yet. Send text commands for now."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_not_allowed(update):
        return

    incoming = (update.message.text or "").strip()
    if not incoming:
        await update.message.reply_text("Send a command or /help.")
        return

    ok, output = _execute_mac_command(incoming)
    prefix = "✅" if ok else "❌"
    await update.message.reply_text(f"{prefix} {output}")


async def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logging.info("Starting Telegram MacBook-control bot")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    try:
        while True:
            await asyncio.sleep(5)
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
