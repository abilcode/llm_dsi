from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from telegram.error import TelegramError

from agents.main_agent import MainAgent

from utils.logger import logger


class TelegramBot:
    def __init__(self, bot_token: str):
        self.agent = MainAgent()
        self.app = Application.builder().token(bot_token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))

        self.app.add_handler(MessageHandler(
            filters.TEXT, self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🔍 Cek Status Kamar",
                                  callback_data="Ketersediaan Kamar")],
            [InlineKeyboardButton("📝 Peraturan Kos-kosan",
                                  callback_data="Peraturan Kos")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_msg = (
            "Halo selamat datang di Pak Kos Bot\n\n"
            "Kalau punya pertanyaan terkait dengan kos-kosan, langsung saja tanyakan pada saya"
            "Anda bisa menekan tombol di bawah ini, atau langsung saja bertanya ya!"
        )

        if (update.message):
            await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id if update.effective_user else -1
        if (update.message):
            await update.message.reply_text("🔄 Mohon Menunggu, Bapak Kos sedang mencari informasi", parse_mode='Markdown')
            agent_response = self.agent.run(update.message.text, user_id)
            await update.message.reply_text(agent_response, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query

        if query:
            await query.answer()
            logger.info(f"Callback data: {query.data}")
            if query.data and query.message:
                await query.message.reply_text("🔄 Mohon Menunggu, Bapak Kos sedang mencari informasi", parse_mode='Markdown') # type: ignore
                agent_response = self.agent.run(query.data)  # type: ignore
                await query.message.reply_text(agent_response, parse_mode='Markdown') # type: ignore

    async def send_message_to_user(self, user_id: int, message: str, parse_mode: str = "Markdown") -> bool:
        try:
            await self.app.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Message sent successfully to user {user_id}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error sending message to user {user_id}: {e}")
            return False
