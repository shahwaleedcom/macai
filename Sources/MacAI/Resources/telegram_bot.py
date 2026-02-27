#!/usr/bin/env python3
"""
Simple Telegram voice-control bot.

Required environment variables:
  TELEGRAM_BOT_TOKEN=<your bot token>
"""

import asyncio
import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("MacAI bot online. Send voice notes to control your assistant.")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Hook your transcription + command router here.
    await update.message.reply_text("Voice command received. Processing...")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip().lower()
    if text in {"start ai", "stop ai"}:
        await update.message.reply_text(f"Command '{text}' forwarded to local AI controller.")
    else:
        await update.message.reply_text("Send a voice note or 'start ai' / 'stop ai'.")


async def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logging.info("Starting Telegram voice-control bot")
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
