# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from gql.transport.requests import log as requests_logger

from src.handlers import handler_button, handler_help, handler_md_guide, handler_message, handler_start
from src.settings import Settings

tg_log_handler = logging.FileHandler("issue_tgbot_telegram_updater.log")
tg_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
tg_logger = logging.getLogger('telegram.ext._updater')
tg_logger.propagate = False
tg_logger.addHandler(tg_log_handler)

requests_logger.setLevel(logging.WARNING)
logging.getLogger("httpx").propagate = False

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

settings = Settings()


class StartWithBotMention(filters.MessageFilter):
    def filter(self, message):
        if message.text is None:
            return False
        return message.text.startswith(settings.BOT_NICKNAME)


if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', handler_start))
    application.add_handler(CommandHandler('help', handler_help))
    application.add_handler(CommandHandler('md_guide', handler_md_guide))
    application.add_handler(CallbackQueryHandler(handler_button))
    application.add_handler(MessageHandler(StartWithBotMention(), handler_message))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE, handler_message))
    application.run_polling()
