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
github = Github('profcomff', settings.GITHUB_ORGANIZATION_TOKEN)


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
    callback_data = update.callback_query.data
    text = update.callback_query.message.text_html

    if callback_data == 'setup':
        _, old_repo_name, _, _ = __parse_text(update.callback_query.message.text)
        if old_repo_name == 'No repo':
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data='quite'),
                                              InlineKeyboardButton('⚠️ Select repo to create', callback_data='repos_1')]])
        else:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data='quite'),
                                              # InlineKeyboardButton('📂', callback_data='repos_1'),
                                              InlineKeyboardButton('👤', callback_data='assign'),
                                              InlineKeyboardButton('❌', callback_data='close')]])
    elif callback_data == 'quite':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])

    elif callback_data == 'close':
        keyboard, text = __close_issue(update)

    elif callback_data.startswith('repos_'):
        page = int(callback_data.split('_')[1])
        keyboard = __keyboard_repos(page)

    elif callback_data.startswith('repo_'):
        keyboard, text = __create_issue(update)

    else:
        await update.callback_query.edit_message_text(text='Видимо бот обновился, эту issue нельзя настроить',
                                                      disable_web_page_preview=True,
                                                      parse_mode=ParseMode('HTML'))
        return

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

    text = __create_base_message_text(text)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=text,
                                   reply_markup=keyboard,
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))


def __keyboard_repos(page):
    repos = github.get_repos(page)
    if len(repos) == 0:
        page = 1
        repos = github.get_repos(page)
        if len(repos) == 0:
            return InlineKeyboardMarkup([[InlineKeyboardButton('↩️ Выйти', callback_data='quite')]])

    buttons = [[InlineKeyboardButton(repo['name'], callback_data='repo_' + repo['name'])] for repo in repos]
    buttons.append([])
    if page > 1:
        buttons[-1].append(InlineKeyboardButton('⬅️', callback_data=f'repos_{page - 1}'))
    buttons[-1].append(InlineKeyboardButton('↩️ Выйти', callback_data='quite'))
    buttons[-1].append(InlineKeyboardButton('➡️', callback_data=f'repos_{page + 1}'))

    return InlineKeyboardMarkup(buttons)


def __create_issue(update: Update):
    repo_name = str(update.callback_query.data.split('_')[1])
    title, old_repo_name, assigned, comment = __parse_text(update.callback_query.message.text)
    # TODO: Repo changed, assigned changed

    github_comment = f'**Issue open by {update.callback_query.from_user.full_name} via Telegram bot**\n\n' + comment

    r = github.open_issue(repo_name, title, github_comment)
    if r.status_code == 201:
        response = r.json()
        assignees = response['assignees']
        title = f'''<a href="{response['html_url']}">{title}</a>'''
        'https://api.github.com/repos/profcomff/print-tgbot'
        repo_name = f'''<a href="{response['repository_url'].replace('api.github.com/repos', 'github.com')}">{repo_name}</a>'''
        text = __join_to_message_text(title, repo_name, assigned, comment, '📂')
    else:
        text = __join_to_message_text(title, 'No repo', assigned, comment, '⚠️')

    return InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]]), text


def __close_issue(update: Update):
    title, repo_name, assigned, comment = __parse_text(update.callback_query.message.text_html)

    github_comment = f'**Issue closed by {update.callback_query.from_user.full_name} via Telegram bot**\n\n' + comment


    # r = github.close_issue(repo_name, title, github_comment)

    text = 'Issue {} closed'

    return None, text


def __create_base_message_text(text):
    if len(text.split('\n')) == 1:
        issue_title = text
        comment = ''
    else:
        issue_title = text.split('\n')[0]
        comment = '\n'.join(text.split('\n')[1:])

    repo_name = 'No repo'
    assigned = 'No assigned'
    answer = f'🔘 {issue_title}\n⚠️ {repo_name}\n👤 {assigned}'
    answer = answer + f'\nℹ️ {comment}' if comment != '' else answer
    return answer


def __join_to_message_text(title, repo_name, assigned, comment, flag='📂'):
    answer = f'🔘 {title}\n{flag} {repo_name}\n👤 {assigned}'
    answer = answer + f'\nℹ️ {comment}' if comment != '' else answer
    return answer


def __parse_text(text):
    stext = text.split('\n')
    if len(stext) == 3:
        return stext[0].replace('🔘 ', ''), stext[1].replace('📂 ', '').replace('⚠️ ', ''), stext[2].replace('👤 ', ''), ''
    else:
        comment = '\n'.join(stext[3:]).replace('ℹ️ ', '')
        return stext[0].replace('🔘 ', ''), stext[1].replace('📂 ', '').replace('⚠️ ', ''), stext[2].replace('👤 ', ''), comment
