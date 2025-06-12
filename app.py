import asyncio
import os
from dotenv import load_dotenv
import uvicorn

from bot.api import app as api_app, init_bot
from bot.bot import TelegramBot
from utils.logger import logger

load_dotenv(override=True)


async def start_uvicorn():
    config = uvicorn.Config(
        api_app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


async def start_bot(bot: TelegramBot):
    await bot.app.initialize()
    await bot.app.start()
    if (bot.app.updater):
        await bot.app.updater.start_polling()
        logger.info("Telegram bot started")
    else:
        logger.info("Telegram bot failed to be started")


async def stop_bot(bot: TelegramBot):
    if (bot.app.updater):
        await bot.app.updater.stop()
        await bot.app.stop()
        await bot.app.shutdown()


async def main():
    logger.info("Starting Telegram Bot and API Integration...")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

    telegram_bot = TelegramBot(bot_token)

    init_bot(telegram_bot)

    try:
        await asyncio.gather(
            start_bot(telegram_bot),
            start_uvicorn()
        )
    finally:
        await stop_bot(telegram_bot)

if __name__ == "__main__":
    asyncio.run(main())
