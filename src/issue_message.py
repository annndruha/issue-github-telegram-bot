# Marakulin Andrey https://github.com/Annndruha
# 2023
# This class used for prepare telegram message and parsing back
import logging
import re

from telegram.constants import ChatType

from src.settings import Settings

settings = Settings()


class TgIssueMessage:
    def __init__(self, bot_html=None):
        self.issue_title = None
        self.issue_url = None
        self.repo_name = None
        self.repo_url = None
        self.assigned = None
        self.assigned_url = None

        if bot_html is not None:
            self.from_bot_html(bot_html)

    def from_bot_html(self, text):
        """
        Parse bot issue-message
        """
        st = text.split('\n')
        self.issue_url, self.issue_title = self.__extract_href(st[0].removeprefix('🏷'))
        self.repo_url, self.repo_name = self.__extract_href(st[1].removeprefix('🗄').removeprefix('⚠️ '))
        self.assigned_url, self.assigned = self.__extract_href(st[2].removeprefix('👤'))

    def from_reopen(self, issue_url, title, login=None):
        """
        Parse bot reopen-message
        """
        self.set_issue_url(issue_url)
        self.issue_title = title
        self.set_assigned(login)

    def from_user(self, text):
        """
        Parse user message
        """
        text = text.split('\n', maxsplit=1)[0].strip()
        text = text.removeprefix('/issue').removeprefix(settings.BOT_NICKNAME).strip()
        if len(text) == 0:
            text = 'Empty title'
        self.issue_title = text

    @staticmethod
    def __extract_href(raw_text):
        match = re.search(r'href=[\'"]?([^\'" >]+)', raw_text)
        if match:
            url = match.group(1)
            match = re.search(r'>(.*?)</a>', raw_text)
            text = match.group(1) if match else None
            return url.strip(), text.strip()
        return None, raw_text.strip()

    @staticmethod
    def get_link_to_telegram_message(update):
        base = f'> Issue open by {update.callback_query.from_user.full_name} via '
        if update.callback_query.message.chat.type == ChatType.SUPERGROUP:
            # There are some telegram problem with main topic, message_thread_id of main topic is strange number,
            # while others topics id are fine
            return base + f"[telegram message.]({update.callback_query.message.link})\n\n"
        elif update.callback_query.message.chat.type == ChatType.GROUP:
            return base + 'group-chat message.\n\n'
        elif update.callback_query.message.chat.type == ChatType.PRIVATE:
            return base + 'personal telegram message.\n\n'
        else:
            logging.warning(f"Chat {update.callback_query.message.chat_id} not a supergroup, can't create a msg link.")
            return base + 'telegram message.\n\n'

    @staticmethod
    def get_github_body(update):
        link_to_msg = TgIssueMessage.get_link_to_telegram_message(update)
        if update.effective_message.reply_to_message.text_markdown_v2 is not None:
            text = update.effective_message.reply_to_message.text_markdown_v2
        elif update.effective_message.reply_to_message.caption_html is not None:
            text = update.effective_message.reply_to_message.text_markdown_v2
        else:
            return link_to_msg

        if len(text.split('\n')) == 1:
            return link_to_msg

        title, body = text.split('\n', maxsplit=1)

        if len(body.strip()) == 0:
            return link_to_msg

        body = body.replace('```\n', '\n```\n')  # Format code block correctly
        if body.endswith('```'):  # If "```" at end of text, line above not works correctly
            body = body[:-3] + '\n```'
        for char in "\\`*_{}[]<>()#+-.!|":  # Anti-escape markdown
            body = body.replace('\\' + char, char)
        return link_to_msg + body

    def get_close_message(self, closer_name):
        return f'Issue <a href="{self.issue_url}">{self.issue_title}</a> closed by {closer_name}'

    def set_issue_url(self, issue_url):
        self.issue_url = issue_url
        self.repo_name = issue_url.split('/')[-3]
        self.repo_url = issue_url.split('/issues/')[0]

    def set_assigned(self, assigned):
        if assigned is not None:
            self.assigned = assigned
            self.assigned_url = f'https://github.com/{assigned}'

    def get_text(self):
        text = ''
        if self.issue_url:
            text += f'🏷 <a href="{self.issue_url}">{self.issue_title}</a>'
        else:
            text += '🏷 ' + self.issue_title
        if self.repo_url:
            text += f'\n🗄 <a href="{self.repo_url}">{self.repo_name}</a>'
        else:
            text += '\n⚠️ No repo'
        if self.assigned_url:
            text += f'\n👤 <a href="{self.assigned_url}">{self.assigned}</a>'
        else:
            text += '\n👤 No assigned'
        return text
