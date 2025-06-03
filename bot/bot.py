from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes
)

from agents.main_agent import MainAgent

from utils.logger import logger


class TelegramBot:
    def __init__(self, bot_token: str):
        self.agent = MainAgent()
        self.app = Application.builder().token(bot_token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.app.add_handler(MessageHandler(
            filters.TEXT, self.handle_message))

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if (update.message):
            agent_response = self.agent.run(update.message.text)
            await update.message.reply_text(agent_response)
