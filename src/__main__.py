# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler
from telegram.ext.filters import ALL, TEXT
from telegram.ext import filters

from src.settings import get_settings
from src.handlers import handler_start, handler_help, handler_button, handler_message

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == '__main__':
    settings = get_settings()
    # application = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    # # application.add_handler(CommandHandler('start', handler_start))
    # # application.add_handler(CommandHandler('help', handler_help))
    # application.add_handler(CallbackQueryHandler(handler_button))
    # # application.add_handler(MessageHandler(ALL, handler_message))
    # application.add_handler(MessageHandler(filters.Entity("mention"), handler_message))
    # application.run_polling()

    import requests
    # r = requests.get('https://api.github.com/repos/Annndruha/issue-github-telegram-bot/issues/1')
    # payload = {'title': 'Test title'}
    # r = requests.post('https://api.github.com/repos/Annndruha/issue-github-telegram-bot/issues',
    #                   json=payload,
    #                   auth=self.auth)
    # print(r.text)

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {settings.GITHUB_ORGANIZATION_TOKEN}',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = '{"title":"Found a bug"}'


    r = requests.post('https://api.github.com/repos/profcomff/print-tgbot/issues', headers=headers, data=data)
    print(r.text)
    # response = requests.post(
    #     'http://\'m having a problem with this.","assignees":["octocat"],"milestone":1,"labels":["bug"]}',
    #     headers=headers,
    #     data=data,
    # )
