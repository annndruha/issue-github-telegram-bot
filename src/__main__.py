# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging

from gql.transport.requests import log as requests_logger
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, MessageHandler, filters)

from src.handlers import (handler_button, handler_help, handler_md_guide,
                          handler_message, handler_start)
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


class BotMentionOrCommand(filters.MessageFilter):
    def filter(self, message):
        if message.text_html is not None:
            return message.text_html.startswith((settings.BOT_NICKNAME, '/issue'))
        if message.caption_html is not None:
            return message.caption_html.startswith((settings.BOT_NICKNAME, '/issue'))
        return False


if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    application.add_handler(CallbackQueryHandler(handler_button))
    application.add_handler(CommandHandler('start', handler_start, filters=filters.UpdateType.MESSAGE))
    application.add_handler(CommandHandler('help', handler_help, filters=filters.UpdateType.MESSAGE))
    application.add_handler(CommandHandler('md_guide', handler_md_guide, filters=filters.UpdateType.MESSAGE))
    application.add_handler(CommandHandler('issue', handler_message, filters=filters.UpdateType.MESSAGE))

    message_filter = filters.UpdateType.MESSAGE & (BotMentionOrCommand() | filters.ChatType.PRIVATE)
    application.add_handler(MessageHandler(message_filter, handler_message))
    application.run_polling()
