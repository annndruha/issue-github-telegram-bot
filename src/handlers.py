# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging
import time
import traceback

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError, NetworkError
from telegram.ext import ContextTypes, CallbackContext

from src.settings import get_settings
from src.github_issue_api import Github, GithubIssueDisabledError
from src.answers import ans

settings = get_settings()
github = Github(settings.GH_ORGANIZATION_NICKNAME, settings.GH_ACCOUNT_TOKEN)


def handler(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await func(update, context)
        except NetworkError as err:
            logging.error(f'Exception {str(err.args)}.')
            time.sleep(2)
        except (TelegramError, Exception) as err:
            logging.error(f'Exception {str(err.args)}, traceback:')
            traceback.print_tb(err.__traceback__)
            time.sleep(5)

    return wrapper


@handler
async def handler_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans['start'].format(settings.GH_ORGANIZATION_NICKNAME),
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))
    logging.info(f'[{update.message.from_user.id} {update.message.from_user.full_name}] call /start')


@handler
async def handler_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans['help'].format(settings.BOT_NICKNAME),
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))
    logging.info(f'[{update.message.from_user.id} {update.message.from_user.full_name}] call /help')


@handler
async def handler_button(update: Update, context: CallbackContext) -> None:
    callback_data = update.callback_query.data
    logging.info(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}]'
                 f'[{update.callback_query.message.id}] button pressed with callback_data={callback_data}')
    text = update.callback_query.message.text_html

    if callback_data == 'setup':
        _, old_repo_name, _, _ = __parse_text(update.callback_query.message.text)
        if old_repo_name == 'No repo':
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data='quite'),
                                              InlineKeyboardButton('⚠️ Select repo to create',
                                                                   callback_data='repos_1')]])
        else:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data='quite'),
                                              InlineKeyboardButton('👤', callback_data='assign_1'),
                                              InlineKeyboardButton('❌', callback_data='close')]])
    elif callback_data == 'quite':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])

    elif callback_data == 'close':
        keyboard, text = __close_issue(update)

    elif callback_data.startswith('repos_'):
        page = int(callback_data.split('_')[1])
        keyboard = __keyboard_repos(page)

    elif callback_data.startswith('repo_'):
        keyboard, text = await __create_issue(update, context)

    elif callback_data.startswith('assign_'):
        page = int(callback_data.split('_')[1])
        keyboard = __keyboard_assign(page)

    elif callback_data.startswith('member_'):
        keyboard, text = __set_assign(update)

    else:
        await update.callback_query.edit_message_text(text='Видимо бот обновился, эту issue нельзя настроить',
                                                      disable_web_page_preview=True,
                                                      parse_mode=ParseMode('HTML'))
        logging.error(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}]'
                      f' button pressed with old callback_data={callback_data}')
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
        text = 'После упоминания требуется ввести название issue. Больше в /help'
        keyboard = None
        logging.warning(f'[{update.message.from_user.id} {update.message.from_user.full_name}] call with no title')
    else:
        text = __create_base_message_text(text)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])
        logging.info(f'[{update.message.from_user.id} {update.message.from_user.full_name}]'
                     f' create draft with message:{repr(update.message.text)}')

    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
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
    title, _, assigned, comment = __parse_text(update.callback_query.message.text)

    github_comment = ans['issue_open'].format(update.callback_query.from_user.full_name) + comment
    try:
        r = github.open_issue(repo_name, title, github_comment)
    except GithubIssueDisabledError:
        await context.bot.answer_callback_query(update.callback_query.id, 'У этого репозитория отключены Issue.')
        text = __join_to_message_text(title, 'No repo', assigned, comment, '⚠️')
        logging.warning(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}]'
                        f'[{update.callback_query.message.id}] Try to open issue, but issue for {repo_name} disabled')
        return InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]]), text

    if r.status_code == 201:
        response = r.json()
        title = ans['link'].format(response['html_url'], title)
        repo_link = response['repository_url'].replace('api.github.com/repos', 'github.com')
        repo_name = ans['link'].format(repo_link, repo_name)
        text = __join_to_message_text(title, repo_name, assigned, comment, '📂')
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data='quite'),
                                          InlineKeyboardButton('👤', callback_data='assign_1'),
                                          InlineKeyboardButton('❌', callback_data='close')]])
        logging.info(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}]'
                     f'[{update.callback_query.message.id}] Succeeded open Issue: {response["html_url"]}')

    else:
        await context.bot.answer_callback_query(update.callback_query.id, f'Response code: {r.status_code}')
        text = __join_to_message_text(title, 'No repo', assigned, comment, '⚠️')
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])
        logging.error(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}]'
                      f'[{update.callback_query.message.id}] Failed to open Issue [{r.status_code}] {r.text}')

    return keyboard, text


def __set_assign(update: Update):
    member_login = str(update.callback_query.data.split('_')[1])
    _, clean_repo_name, _, _ = __parse_text(update.callback_query.message.text)
    title, repo_name, old_assigned, comment = __parse_text(update.callback_query.message.text_html)
    issue_number_str = title.split('/issues/')[1].split('"')[0]

    r, status_code = github.get_issue(clean_repo_name, issue_number_str)
    if status_code != 200:
        return None, __get_problem(clean_repo_name, issue_number_str, r)

    assigned = ans['member_to_login'].format(member_login, member_login)
    assign_github_comment = r['body'] + ans['assign_change'].format(old_assigned, assigned,
                                                                    update.callback_query.from_user.full_name)

    r = github.set_assignee(clean_repo_name, issue_number_str, member_login, assign_github_comment)
    if r.status_code != 200:
        return None, __get_problem(clean_repo_name, issue_number_str, r)

    text = __join_to_message_text(title, repo_name, assigned, comment)

    return InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]]), text


def __close_issue(update: Update):
    title, _, _, _ = __parse_text(update.callback_query.message.text_html)
    _, clean_repo_name, _, _ = __parse_text(update.callback_query.message.text)
    issue_number_str = title.split('/issues/')[1].split('"')[0]

    r, status_code = github.get_issue(clean_repo_name, issue_number_str)
    if status_code != 200:
        return None, __get_problem(clean_repo_name, issue_number_str, r)

    close_github_comment = r['body'] + ans['issue_close'].format(update.callback_query.from_user.full_name)

    r = github.close_issue(clean_repo_name, issue_number_str, close_github_comment)
    if r.status_code != 200:
        return None, __get_problem(clean_repo_name, issue_number_str, r)

    text = f'Issue {title} closed by {update.callback_query.from_user.full_name}'
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
    st = text.split('\n')
    if len(st) == 3:
        return st[0].replace('🔘 ', ''), st[1].replace('📂 ', '').replace('⚠️ ', ''), st[2].replace('👤 ', ''), ''
    else:
        comment = '\n'.join(st[3:]).replace('ℹ️ ', '')
        return st[0].replace('🔘 ', ''), st[1].replace('📂 ', '').replace('⚠️ ', ''), st[2].replace('👤 ', ''), comment


def __get_problem(clean_repo_name, issue_number_str, r):
    text = f'Problem with ' \
           f'{ans["link"].format(github.get_issue_human_link(clean_repo_name, issue_number_str), "issue")}:\n' \
           f'{r["message"]}'
    return text
