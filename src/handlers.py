# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging
import threading
import traceback

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from telegram.constants import ParseMode
from telegram.constants import MessageEntityType

from src.settings import Settings
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


@error_handler
async def handler_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans['start'].format(settings.GH_ORGANIZATION_NICKNAME),
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))
    logging.info(f'[{update.message.from_user.id} {update.message.from_user.full_name}] call /start')


@error_handler
async def handler_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans['help'].format(settings.BOT_NICKNAME),
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))
    logging.info(f'[{update.message.from_user.id} {update.message.from_user.full_name}] call /help')


@error_handler
async def handler_button(update: Update, context: CallbackContext) -> None:
    callback_data = update.callback_query.data
    logging.info(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}]'
                 f'[{update.callback_query.message.id}] button pressed with callback_data={callback_data}')
    text = update.callback_query.message.text_html

    if callback_data == 'setup':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data='quite'),
                                          InlineKeyboardButton('👤', callback_data='assign_1'),
                                          InlineKeyboardButton('❌', callback_data='close')]])
    elif callback_data == 'quite':
        _, repo_name, _, _ = __parse_text(update.callback_query.message.text)
        if repo_name == 'No repo':
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
        logging.warning(f'[{update.message.from_user.id} {update.message.from_user.full_name}] call with no title')
    else:
        text = __create_base_message_text(text)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('⚠️ Select repo to create', callback_data='repos_start')]])
        logging.info(f'[{update.message.from_user.id} {update.message.from_user.full_name}]'
                     f' create draft with message:{repr(update.message.text)}')

    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=text,
                                   reply_markup=keyboard,
                                   disable_web_page_preview=True,
                                   parse_mode=ParseMode('HTML'))


def __keyboard_repos(cursor):
    print(cursor)
    if cursor == 'start':
        repos_info = github.get_repos()
    else:
        repos_info = github.get_repos(cursor)
    repos = repos_info['edges']
    page_info = repos_info['pageInfo']

    buttons = [[InlineKeyboardButton(repo['node']['name'], callback_data='repo_' + repo['node']['name'])] for repo in repos]
    buttons.append([])

    if page_info['hasPreviousPage']:
        buttons[-1].append(InlineKeyboardButton('⬅️', callback_data=f'''repos_before: "{page_info['startCursor']}"'''))
    buttons[-1].append(InlineKeyboardButton('↩️ Выйти', callback_data='quite'))
    if page_info['hasNextPage']:
        buttons[-1].append(InlineKeyboardButton('➡️', callback_data=f'''repos_after: "{page_info['endCursor']}"'''))

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
    title, _, assigned, _ = __parse_text(update.callback_query.message.text)
    _, _, _, comment = __parse_text(update.callback_query.message.text_html)

    link_to_msg = __get_link_to_telegram_message(update)

    github_comment = comment.replace('<span class="tg-spoiler">', '').replace('</span>', '')
    github_comment += ans['issue_open'].format(update.callback_query.from_user.full_name, link_to_msg)
    try:
        r = github.open_issue(repo_name, title, github_comment)
    except GithubIssueDisabledError:
        await context.bot.answer_callback_query(update.callback_query.id, 'У этого репозитория отключены Issue.')
        text = __join_to_message_text(title, 'No repo', assigned, comment, '⚠️')
        logging.warning(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}]'
                        f'[{update.callback_query.message.id}] Try to open issue, but issue for {repo_name} disabled')
        return InlineKeyboardMarkup([[InlineKeyboardButton('⚠️ Select repo to create', callback_data='repos_start')]]), text

    if r.status_code == 201:
        response = r.json()
        title = ans['link'].format(response['html_url'], title)
        repo_link = response['repository_url'].replace('api.github.com/repos', 'github.com')
        repo_name = ans['link'].format(repo_link, repo_name)
        text = __join_to_message_text(title, repo_name, assigned, comment, '🗄')
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data='quite'),
                                          InlineKeyboardButton('👤', callback_data='assign_1'),
                                          InlineKeyboardButton('❌', callback_data='close')]])
        logging.info(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}]'
                     f'[{update.callback_query.message.id}] Succeeded open Issue: {response["html_url"]}')

        threading.Thread(target=add_to_scrum, args=(github.headers, response['node_id'])).start()

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

    logging.info(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}]'
                 f'[{update.callback_query.message.id}] Succeeded closed Issue:' +
                 ans["link"].format(github.get_issue_human_link(clean_repo_name, issue_number_str), "issue"))
    text = f'Issue {title} closed by {update.callback_query.from_user.full_name}'
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('🔄 Reopen', callback_data='reopen')]])
    return keyboard, text


def __reopen_issue(update):
    issue_url = update.callback_query.message.parse_entities(MessageEntityType.TEXT_LINK).popitem()[0].url
    repo, number_srt = issue_url.split('/')[-3], issue_url.split('/')[-1]
    r, status_code = github.reopen_issue(repo, number_srt)
    if status_code != 200:
        return None, __get_problem(repo, number_srt, r)

    title = ans['link'].format(github.get_issue_human_link(repo, number_srt), r['title'])
    repo_name = ans['link'].format(r['repository_url'], repo).replace('api.github.com/repos', 'github.com')
    assigned = 'No assigned'
    if len(r['assignees']) != 0:
        assigned = ans['link'].format(r['assignees'][0]['html_url'], r['assignees'][0]['login'])

    text = __join_to_message_text(title, repo_name, assigned, '')
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Настроить', callback_data='setup')]])
    return keyboard, text


def __create_base_message_text(text):
    if len(text.split('\n')) == 1:
        issue_title = text
        comment = ''
    else:
        issue_title = text.split('\n')[0]
        comment = '\n'.join(text.split('\n')[1:])

    repo_name = 'No repo'
    assigned = 'No assigned'
    answer = f'🏷 {issue_title}\n⚠️ {repo_name}\n👤 {assigned}'
    answer = answer + f'\n📜 {comment}' if comment != '' else answer
    return answer


def __join_to_message_text(title, repo_name, assigned, comment, flag='🗄'):
    answer = f'🏷 {title}\n{flag} {repo_name}\n👤 {assigned}'
    answer = answer + f'\n📜 {comment}' if comment != '' else answer
    return answer


def __parse_text(text):
    st = text.split('\n')
    if len(st) == 3:
        return st[0].replace('🏷 ', ''), st[1].replace('🗄 ', '').replace('⚠️ ', ''), st[2].replace('👤 ', ''), ''
    else:
        comment = '\n'.join(st[3:]).replace('📜 ', '')
        return st[0].replace('🏷 ', ''), st[1].replace('🗄 ', '').replace('⚠️ ', ''), st[2].replace('👤 ', ''), comment


def __get_problem(clean_repo_name, issue_number_str, r):
    text = f'Problem with ' \
           f'{ans["link"].format(github.get_issue_human_link(clean_repo_name, issue_number_str), "issue")}:\n' \
           f'{r["message"]}'
    logging.warning(github.get_issue_human_link(clean_repo_name, issue_number_str))
    return text


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
