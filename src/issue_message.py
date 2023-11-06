# Marakulin Andrey https://github.com/Annndruha
# 2023
# This class used for prepare telegram message and parsing back
import logging
import re

from telegram.constants import ChatType


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
        self.issue_title = text.split('\n', maxsplit=1)[0].strip()

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
    def __get_link_to_telegram_message(update):
        if update.callback_query.message.chat.type == ChatType.SUPERGROUP:
            message_thread_id = update.callback_query.message.message_thread_id
            message_thread_id = 1 if message_thread_id is None else message_thread_id  # If 'None' set '1'
            chat_id = str(update.callback_query.message.chat_id)
            message_id = update.callback_query.message.message_id
            return f"""<a href="https://t.me/c/{chat_id[4:]}/{message_thread_id}/{message_id}">telegram message.</a>"""
        elif update.callback_query.message.chat.type == ChatType.GROUP:
            return 'group-chat message.'
        elif update.callback_query.message.chat.type == ChatType.PRIVATE:
            return 'personal telegram message.'
        else:
            logging.warning(f"Chat {update.callback_query.message.chat_id} not a supergroup, can't create a msg link.")
            return 'telegram message.'

    # def get_gh_body(self, update):
    #     link_to_msg = self.__get_link_to_telegram_message(update)
    #
    #     text = self.body
    #     matches = re.findall(r'(<code>)([\s\S]*?)(</code>)', text)
    #     for m in matches:
    #         s = ''.join(m)
    #         if '\n' in s:
    #             text = text.replace(s, s.replace('<code>', '```\n').replace('</code>', '\n```\n'))
    #         else:
    #             text = text.replace(s, s.replace('<code>', '`').replace('</code>', '`'))
    #
    #     return text + f'\n> Issue open by {update.callback_query.from_user.full_name} via {link_to_msg}'

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
