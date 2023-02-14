# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging
import time
import traceback


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes, CallbackContext

from src.settings import get_settings
from src.github_issue_api import Github

settings = get_settings()


def handler(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await func(update, context)
        except (TelegramError, Exception) as err:
            logging.error(f'Exception {str(err.args)}, traceback:')
            traceback.print_tb(err.__traceback__)
            time.sleep(2)

    return wrapper


@handler
async def handler_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Start message', disable_web_page_preview=True, parse_mode=ParseMode('HTML'))


@handler
async def handler_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Help message', disable_web_page_preview=True, parse_mode=ParseMode('HTML'))


@handler
async def handler_button(update: Update, context: CallbackContext) -> None:
    try:
        d = {
            'setup': InlineKeyboardMarkup([[InlineKeyboardButton('⬅️', callback_data='back'),
                                            InlineKeyboardButton('👤', callback_data='assign'),
                                            InlineKeyboardButton('🗃', callback_data='repo'),
                                            InlineKeyboardButton('❌', callback_data='close')]]),
            'back': InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])
        }
        keyboard = d[update.callback_query.data]
    except KeyError:
        await update.callback_query.edit_message_text(text='Видимо бот обновился, эту issue нельзя настроить',
                                                      disable_web_page_preview=True,
                                                      parse_mode=ParseMode('HTML'))
        return

    text = update.callback_query.message.text
    await update.callback_query.edit_message_text(text=text,
                                                  reply_markup=keyboard,
                                                  disable_web_page_preview=True,
                                                  parse_mode=ParseMode('HTML'))


@handler
async def handler_message(update: Update, context: CallbackContext) -> None:
    mentions = update.effective_message.parse_entities(["mention"])
    if settings.BOT_NICKNAME.lower() not in [mention.lower() for mention in list(mentions.values())]:
        return
    text = update.message.text.replace(settings.BOT_NICKNAME, '').strip()
    if len(text) == 0:
        return

    if len(text.split('\n')) == 1:
        issue_title = text
        comment = ''
    else:
        issue_title = text.split('\n')[0]
        comment = '\n'.join(text.split('\n')[1:])

    repo_name = 'No repo'
    assigned = 'No assigned'
    answer = f'🔘 {issue_title}\n🗃 {repo_name}\n👤 {assigned}\nℹ️ {comment}'

    # github = Github('Annndruha', 'issue-github-telegram-bot', settings.GITHUB_ORGANIZATION_TOKEN)
    # github.open_issue('2')

    # from github import Github
    #
    # # First create a Github instance:
    #
    # # using an access token
    # g = Github(settings.GITHUB_ORGANIZATION_TOKEN)
    #
    # # Github Enterprise with custom hostname
    # g = Github(base_url="https://api.github.com/api/v3", login_or_token=settings.GITHUB_ORGANIZATION_TOKEN)
    #
    # # Then play with your Github objects:
    # for repo in g.get_user().get_repos():
    #     print(repo.name)

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=answer,
                                   reply_markup=keyboard,
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))
