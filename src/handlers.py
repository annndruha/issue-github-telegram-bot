# Marakulin Andrey https://github.com/Annndruha
# 2023


import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ContextTypes

from src.answers import Answers
from src.errors_solver import errors_solver
from src.github_api import Github
from src.issue_message import TgIssueMessage
from src.log_formatter import log_formatter
from src.settings import Settings

ans = Answers()
settings = Settings()
github = Github(settings)
HTML = ParseMode('HTML')


@errors_solver
@log_formatter
async def handler_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans.start.format(settings.GH_ORGANIZATION_NICKNAME),
                                   disable_web_page_preview=True,
                                   parse_mode=HTML)


@errors_solver
@log_formatter
async def handler_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans.help.format(settings.BOT_NICKNAME),
                                   disable_web_page_preview=True,
                                   parse_mode=HTML)


@errors_solver
@log_formatter
async def handler_md_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans.markdown_guide_tg,
                                   disable_web_page_preview=True,
                                   parse_mode=HTML)
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   text=ans.markdown_guide_md,
                                   disable_web_page_preview=True, )


@errors_solver
@log_formatter
async def handler_message(update: Update, context: CallbackContext) -> None:
    """
    Receive a private user message or group-chat bot mention
    and reply with issue template (or no title warning message).
    """
    if update.message.text_html is not None:
        text_html = update.message.text_html
    elif update.message.caption_html is not None:
        text_html = update.message.caption_html
    else:
        return

    text_html = text_html.removeprefix('/issue').removeprefix(settings.BOT_NICKNAME).strip()

    if len(text_html) == 0:
        text_html = 'Draft issue'

    imessage = TgIssueMessage()
    imessage.from_user(text_html)
    keyboard = __get_keyboard_begin(update)

    await context.bot.send_message(chat_id=update.message.chat_id,
                                   message_thread_id=update.message.message_thread_id,
                                   reply_to_message_id=update.message.id,
                                   text=imessage.get_text(),
                                   reply_markup=keyboard,
                                   disable_web_page_preview=True,
                                   parse_mode=HTML)


@errors_solver
@log_formatter
async def handler_button(update: Update, context: CallbackContext) -> None:
    """
    This is keyboard callback browser.
    callback_data stored in buttons like this:

    'action_subaction_IDSTRING' - For members and repos keyboard pages
    'action_IDSTRING' - For all other cases
    """
    callback_data = update.callback_query.data
    action = callback_data.split('_', 1)[0]
    text = update.callback_query.message.text_html

    match action:
        case 'quite':
            keyboard = __get_keyboard_begin(update)
        case 'setup':
            issue_id = __search_issue_id_in_keyboard(update)
            keyboard = __get_keyboard_setup(issue_id)
        case 'members':
            keyboard = __get_keyboard_members(update)
        case 'rps':
            keyboard = __get_keyboard_repos(update)
        case 'repo':
            keyboard, text = __create_issue(update)
        case 'assign':
            keyboard, text = __set_assign(update)
        case 'close':
            keyboard, text = __close_issue(update)
        case 'reopen':
            keyboard, text = __reopen_issue(update)
        case _:
            keyboard, text = None, 'Probably bot updated, issue can\'t be changed.'
            logging.error('Old keyboard callback')

    await update.callback_query.edit_message_text(text=text,
                                                  reply_markup=keyboard,
                                                  disable_web_page_preview=True,
                                                  parse_mode=HTML)


def __get_keyboard_begin(update: Update) -> InlineKeyboardMarkup:
    """
    Return a first button.
    It may be a keyboard for issue template, for quite button while repo is not selected
    or for hide setup keyboard
    """
    if update.callback_query is None or update.callback_query.data == 'quite_start':
        return InlineKeyboardMarkup([[InlineKeyboardButton('⚠️ Select repo to create', callback_data='rps_start')]])
    else:
        issue_id = __search_issue_id_in_keyboard(update)
        return InlineKeyboardMarkup([[InlineKeyboardButton('Setup', callback_data=f'setup_{issue_id}')]])


def __get_keyboard_setup(issue_id: str) -> InlineKeyboardMarkup:
    """
    Setup keyboard for setup existed issue.
    return keyboard with 4 buttons: hide setup, change repo, change assign and close issue
    """
    return InlineKeyboardMarkup([[InlineKeyboardButton('↩️', callback_data=f'quite_{issue_id}'),
                                  InlineKeyboardButton('🗄 ', callback_data='rps_start'),
                                  InlineKeyboardButton('👤', callback_data='members_start'),
                                  InlineKeyboardButton('❌', callback_data=f'close_{issue_id}')]])


def __get_keyboard_reopen(issue_id: str) -> InlineKeyboardMarkup:
    """
    Return a keyboard with reopen button
    """
    return InlineKeyboardMarkup([[InlineKeyboardButton('🔄 Reopen', callback_data=f'reopen_{issue_id}')]])


def __get_keyboard_repos(update: Update) -> InlineKeyboardMarkup:
    """
    Get organization repositories and create a keyboard page
    with repositories and control buttons
    """
    repositories = github.get_repos(update.callback_query.data)
    issue_id = __search_issue_id_in_keyboard(update)

    buttons = []
    for repo in repositories['edges']:
        cb_data = f"repo_{repo['node']['id']}"
        buttons.append([InlineKeyboardButton(repo['node']['name'], callback_data=cb_data)])

    buttons.append([])
    if repositories['pageInfo']['hasPreviousPage']:
        cb_data = f"rps_be_{repositories['pageInfo']['startCursor']}"
        buttons[-1].append(InlineKeyboardButton('⬅️', callback_data=cb_data))

    cb_data = f'quite_{issue_id}' if issue_id is not None else 'quite_start'
    buttons[-1].append(InlineKeyboardButton('↩️ Back', callback_data=cb_data))

    if repositories['pageInfo']['hasNextPage']:
        cb_data = f"rps_af_{repositories['pageInfo']['endCursor']}"
        buttons[-1].append(InlineKeyboardButton('➡️', callback_data=cb_data))

    return InlineKeyboardMarkup(buttons)


def __get_keyboard_members(update: Update) -> InlineKeyboardMarkup:
    """
    Get organization members and create a keyboard page
    with members and control buttons
    """
    members = github.get_members(update.callback_query.data)
    issue_id = __search_issue_id_in_keyboard(update)

    buttons = []
    for member in members['edges']:
        bt_text = member['node']['login']
        if member['node']['name'] is not None:
            bt_text += f" | {member['node']['name']}"
        cb_data = f"assign_{member['node']['id']}"
        buttons.append([InlineKeyboardButton(bt_text, callback_data=cb_data)])

    buttons.append([])
    if members['pageInfo']['hasPreviousPage']:
        cb_data = f"members_before_{members['pageInfo']['startCursor']}"
        buttons[-1].append(InlineKeyboardButton('⬅️', callback_data=cb_data))

    cb_data = f"quite_{issue_id}"
    buttons[-1].append(InlineKeyboardButton('↩️ Back', callback_data=cb_data))

    if members['pageInfo']['hasNextPage']:
        cb_data = f"members_after_{members['pageInfo']['endCursor']}"
        buttons[-1].append(InlineKeyboardButton('➡️', callback_data=cb_data))

    return InlineKeyboardMarkup(buttons)


def __create_issue(update: Update):
    """
    When user select a repo for issue there are two thinks may happen:
    user want to create a new issue or change repository for existing issue
    """
    repo_id = update.callback_query.data.split('_', 1)[1]
    imessage = TgIssueMessage(bot_html=update.callback_query.message.text_html)
    issue_id = __search_issue_id_in_keyboard(update)

    if issue_id is None:
        imessage, issue_id = __create_new_issue(imessage, repo_id, update)
    else:
        imessage, issue_id = __transfer_exist_issue(imessage, repo_id, issue_id)
    return __get_keyboard_setup(issue_id), imessage.get_text()


def __create_new_issue(imessage: TgIssueMessage, repo_id: str, update: Update) -> (InlineKeyboardMarkup, str):
    """
    Open new issue for selected repo_id.
    Return updated bot message and created issue_id
    """
    text_md = update.effective_message.reply_to_message.text_markdown_v2
    text_md = text_md.split('\n', maxsplit=1)[1]
    text_md = text_md.replace('```\n', '\n```\n')

    r = github.open_issue(repo_id, imessage.issue_title, text_md)

    imessage.set_issue_url(r['createIssue']['issue']['url'])
    issue_id = r['createIssue']['issue']['id']
    logging.info(f"[Issue: {issue_id}] Succeeded open Issue: {r['createIssue']['issue']['url']}")
    return imessage, issue_id


def __transfer_exist_issue(imessage: TgIssueMessage, new_repo_id: str, issue_id: str) -> (InlineKeyboardMarkup, str):
    """
    Transfer exist issue to new_repo_id.
    Return updated bot message and updated issue_id
    """
    r = github.transfer_issue(new_repo_id, issue_id)

    imessage.set_issue_url(r['transferIssue']['issue']['url'])
    issue_id = r['transferIssue']['issue']['id']
    # Probably next 2 lines bot works by GitHub bug: https://github.com/orgs/community/discussions/60896
    if len(r['transferIssue']['issue']['assignees']['edges']) != 0:
        imessage.set_assigned(r['transferIssue']['issue']['assignees']['edges'][0]['node']['login'])
    logging.info(f"[Issue: {issue_id}] Succeeded transferred Issue: {r['transferIssue']['issue']['url']}")
    return imessage, issue_id


def __set_assign(update: Update) -> (InlineKeyboardMarkup, str):
    """
    Get button press with selected member.
    Change assign in GitHub and update bot message.
    """
    issue_id = __search_issue_id_in_keyboard(update)
    member_id = update.callback_query.data.split('_', 1)[1]
    r = github.set_assignee(issue_id, member_id)

    new_assigned = r['updateIssue']['issue']['assignees']['edges'][0]['node']['login']
    imessage = TgIssueMessage(bot_html=update.callback_query.message.text_html)
    imessage.set_assigned(new_assigned)
    logging.info(f'[Issue: {issue_id}] Set assign to [{new_assigned} {member_id}]')
    return __get_keyboard_setup(issue_id), imessage.get_text()


def __close_issue(update: Update):
    """
    Close issue and update bot message.
    """
    issue_id = __search_issue_id_in_keyboard(update)
    github.close_issue(issue_id)

    imessage = TgIssueMessage(bot_html=update.callback_query.message.text_html)
    text = imessage.get_close_message(update.callback_query.from_user.full_name)

    logging.info(f'[Issue: {issue_id}] Succeeded closed {imessage.issue_url}')
    return __get_keyboard_reopen(issue_id), text


def __reopen_issue(update: Update):
    """
    Reopen issue and recreate a bot issue message.
    Recreated message is up-to-date with GitHub.
    """
    issue_id = __search_issue_id_in_keyboard(update)
    r = github.reopen_issue(issue_id)

    issue_url = r['reopenIssue']['issue']['url']
    title = r['reopenIssue']['issue']['title']
    body = r['reopenIssue']['issue']['body'].split('\n> Issue open by')[0]
    login = None
    if len(r['reopenIssue']['issue']['assignees']['edges']) != 0:
        login = r['reopenIssue']['issue']['assignees']['edges'][0]['node']['login']

    imessage = TgIssueMessage()
    imessage.from_reopen(issue_url, title, login)
    logging.info(f'[Issue: {issue_id}] Succeeded Reopen Issue: {imessage.issue_url}')
    return __get_keyboard_begin(update), imessage.get_text()


def __search_issue_id_in_keyboard(update: Update) -> None | str:
    """
    The only reasonable place to store GraphQL issue_id is keyboard.
    But keyboard is may represent by different buttons.
    So, this function find a stored issue_id in different buttons.
    """
    issue_id = None
    for kb_row in update.callback_query.message.reply_markup.inline_keyboard:
        for kb_col in kb_row:
            if kb_col.callback_data.startswith(('quite_', 'close_', 'setup_', 'reopen_')) and \
                    kb_col.callback_data.split('_', 1)[1] != 'start':
                issue_id = kb_col.callback_data.split('_', 1)[1]
                return issue_id
    return issue_id
