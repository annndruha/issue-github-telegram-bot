# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging
import threading
import traceback

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from telegram.constants import ParseMode

from src.settings import Settings
from src.issue_message import TgIssueMessage
from src.github_api import Github, GithubIssueDisabledError, add_to_scrum
from src.answers import ans

settings = Settings()
github = Github(settings.GH_ORGANIZATION_NICKNAME, settings.GH_ACCOUNT_TOKEN)


async def native_error_handler(update, context):
    pass


def error_handler(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await func(update, context)
        except Exception as err:
            logging.error(err)
            traceback.print_tb(err.__traceback__)

    return wrapper


def str_sender_info(update):
    if update.callback_query is None:
        return f'[{update.message.from_user.id} {update.message.from_user.full_name}]'
    else:
        return f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}] ' \
               f'[{update.callback_query.message.id}] callback_data={update.callback_query.data}]'


@error_handler
async def handler_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f'{str_sender_info(update)} call /start')
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans['start'].format(settings.GH_ORGANIZATION_NICKNAME),
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))


@error_handler
async def handler_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f'{str_sender_info(update)} call /help')
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans['help'].format(settings.BOT_NICKNAME),
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))


@error_handler
async def handler_md_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f'{str_sender_info(update)} call /md_guide')
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans['markdown_guide_tg'],
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans['markdown_guide_md'],
                                   disable_web_page_preview=True,
                                   )


@error_handler
async def handler_button(update: Update, context: CallbackContext) -> None:
    logging.info(f'{str_sender_info(update)}')
    callback_data = update.callback_query.data
    text = update.callback_query.message.text_html

    if callback_data == 'setup':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data='quite'),
                                          InlineKeyboardButton('👤', callback_data='assign_1'),
                                          InlineKeyboardButton('❌', callback_data='close')]])
    elif callback_data == 'quite':
        imessage = TgIssueMessage(update.callback_query.message.text_html)
        if not imessage.is_created():
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton('⚠️ Select repo to create', callback_data='repos_start')]])
        else:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])

    elif callback_data == 'close':
        keyboard, text = __close_issue(update)

    elif callback_data == 'reopen':
        keyboard, text = __reopen_issue(update)

    elif callback_data.startswith('repos_'):
        page_info = callback_data.split('_')[1]
        keyboard = __keyboard_repos(page_info)

    elif callback_data.startswith('repo_'):
        keyboard, text = await __create_issue(update, context)

    elif callback_data.startswith('assign_'):
        page = int(callback_data.split('_')[1])
        keyboard = __keyboard_assign(page)

    elif callback_data.startswith('member_'):
        keyboard, text = __set_assign(update)

    else:
        keyboard, text = None, 'Видимо бот обновился, эту issue нельзя настроить'
        logging.error(f'Old callback: {str_sender_info(update)}')
    await update.callback_query.edit_message_text(text=text,
                                                  reply_markup=keyboard,
                                                  disable_web_page_preview=True,
                                                  parse_mode=ParseMode('HTML'))


@error_handler
async def handler_message(update: Update, context: CallbackContext) -> None:
    mentions = update.effective_message.parse_entities(["mention"])
    captions = update.effective_message.parse_caption_entities(["mention"])

    if settings.BOT_NICKNAME.lower() in [mention.lower() for mention in list(mentions.values())]:
        text = update.message.text_html.replace(settings.BOT_NICKNAME, '').strip()
    elif settings.BOT_NICKNAME.lower() in [caption.lower() for caption in list(captions.values())]:
        text = update.message.caption_html.replace(settings.BOT_NICKNAME, '').strip()
    else:
        return

    if len(text) == 0:
        text = 'После упоминания требуется ввести название issue. Больше в /help'
        keyboard = None
        logging.warning(f'{str_sender_info(update)} call with no title')
    else:
        imessage = TgIssueMessage(text, from_user=True)
        text = imessage.get_text()
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('⚠️ Select repo to create',
                                                               callback_data='repos_start')]])
        logging.info(f'{str_sender_info(update)} create draft with message:{repr(update.message.text)}')

    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=text,
                                   reply_markup=keyboard,
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))


def __keyboard_repos(cursor):
    if cursor == 'start':
        repos_info = github.get_repos()
    else:
        repos_info = github.get_repos(cursor)

    buttons = []
    for repo in repos_info['edges']:
        buttons.append([InlineKeyboardButton(repo['node']['name'], callback_data='repo_' + repo['node']['name'])])

    buttons.append([])
    if repos_info['pageInfo']['hasPreviousPage']:
        cb_data = f'''repos_before: "{repos_info['pageInfo']['startCursor']}"'''
        buttons[-1].append(InlineKeyboardButton('⬅️', callback_data=cb_data))

    buttons[-1].append(InlineKeyboardButton('↩️ Выйти', callback_data='quite'))

    if repos_info['pageInfo']['hasNextPage']:
        cb_data = f'''repos_after: "{repos_info['pageInfo']['endCursor']}"'''
        buttons[-1].append(InlineKeyboardButton('➡️', callback_data=cb_data))

    return InlineKeyboardMarkup(buttons)


def __keyboard_assign(page):
    members = github.get_members(page)
    if len(members) == 0:
        page = 1
        members = github.get_members(page)
        if len(members) == 0:
            return InlineKeyboardMarkup([[InlineKeyboardButton('↩️ Выйти', callback_data='quite')]])

    buttons = [[InlineKeyboardButton(member['login'], callback_data='member_' + member['login'])] for member in members]
    buttons.append([])
    if page > 1:
        buttons[-1].append(InlineKeyboardButton('⬅️', callback_data=f'assign_{page - 1}'))
    buttons[-1].append(InlineKeyboardButton('↩️ Выйти', callback_data='quite'))
    buttons[-1].append(InlineKeyboardButton('➡️', callback_data=f'assign_{page + 1}'))

    return InlineKeyboardMarkup(buttons)


async def __create_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo_name = str(update.callback_query.data.split('_')[1])
    imessage = TgIssueMessage(update.callback_query.message.text_html)

    link_to_msg = __get_link_to_telegram_message(update)
    github_comment = imessage.comment + ans['issue_open'].format(update.callback_query.from_user.full_name, link_to_msg)

    try:
        r = github.open_issue(repo_name, imessage.issue_title, github_comment)
    except GithubIssueDisabledError:
        await context.bot.answer_callback_query(update.callback_query.id, 'У этого репозитория отключены Issue.')
        logging.warning(f'{str_sender_info(update)} Try to open issue, but issue for {repo_name} disabled')
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('⚠️ Select repo to create', callback_data='repos_start')]])
        return keyboard, imessage.get_text()

    if r.status_code == 201:
        response = r.json()
        imessage.set_issue_url(response['html_url'])

        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data='quite'),
                                          InlineKeyboardButton('👤', callback_data='assign_1'),
                                          InlineKeyboardButton('❌', callback_data='close')]])
        logging.info(f'{str_sender_info(update)} Succeeded open Issue: {response["html_url"]}')
        threading.Thread(target=add_to_scrum, args=(github.headers, response['node_id'])).start()

    else:
        await context.bot.answer_callback_query(update.callback_query.id, f'Response code: {r.status_code}')
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])
        logging.error(f'{str_sender_info(update)} Failed to open Issue [{r.status_code}] {r.text}')

    return keyboard, imessage.get_text()


def __set_assign(update: Update):
    new_assigned = str(update.callback_query.data.split('_')[1])
    imessage = TgIssueMessage(update.callback_query.message.text_html)

    r, status_code = github.get_issue(imessage.issue_url)
    if status_code != 200:
        return None, imessage.get_problem_text(r)

    assign_github_comment = r['body'] + ans['assign_change'].format(imessage.assigned, new_assigned,
                                                                    update.callback_query.from_user.full_name)

    r = github.set_assignee(imessage.issue_url, new_assigned, assign_github_comment)
    if r.status_code != 200:
        return None, imessage.get_problem_text(r)

    imessage.set_assigned(new_assigned)
    return InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]]), imessage.get_text()


def __close_issue(update: Update):
    imessage = TgIssueMessage(update.callback_query.message.text_html)

    r, status_code = github.get_issue(imessage.issue_url)
    if status_code != 200:
        return None, imessage.get_problem_text(r)

    close_github_comment = r['body'] + ans['issue_close'].format(update.callback_query.from_user.full_name)

    r = github.close_issue(imessage.issue_url, close_github_comment)
    if r.status_code != 200:
        return None, imessage.get_problem_text(r)

    text = imessage.get_close_message(update.callback_query.from_user.full_name)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('🔄 Reopen', callback_data='reopen')]])

    logging.info(f'{str_sender_info(update)} Succeeded closed Issue: {imessage.issue_url}')
    return keyboard, text


def __reopen_issue(update):
    imessage = TgIssueMessage(update.callback_query.message.text_html, from_reopen=True)
    r, status_code = github.get_issue(imessage.issue_url)
    if status_code != 200:
        return None, imessage.get_problem_text(r)

    reopen_github_comment = r['body'] + ans['issue_reopen'].format(update.callback_query.from_user.full_name)

    r, status_code = github.reopen_issue(imessage.issue_url, reopen_github_comment)
    if status_code != 200:
        return None, imessage.get_problem_text(r)

    if len(r['assignees']) != 0:
        imessage.set_assigned(r['assignees'][0]['login'])

    imessage.comment = r['body'].split('\n>')[0]

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])
    logging.info(f'{str_sender_info(update)} Succeeded Reopen Issue: {imessage.issue_url}')
    return keyboard, imessage.get_text()


def __get_link_to_telegram_message(update):
    if update.callback_query.message.chat.type == "supergroup":
        message_thread_id = update.callback_query.message.message_thread_id
        message_thread_id = 1 if message_thread_id is None else message_thread_id  # If 'None' set '1'
        chat_id = str(update.callback_query.message.chat_id)
        message_id = update.callback_query.message.message_id
        return f"""<a href="https://t.me/c/{chat_id[4:]}/{message_thread_id}/{message_id}">telegram message.</a>"""
    else:
        logging.warning(f"Chat {update.callback_query.message.chat_id} is not a supergroup, can't create a msg link.")
        return 'telegram message.'
