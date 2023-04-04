import re
import logging


def extract_href(raw_text):
    match = re.search(r'href=[\'"]?([^\'" >]+)', raw_text)
    if match:
        url = match.group(1)
        match = re.search(r'>(.*?)</a>', raw_text)
        text = match.group(1) if match else None
        return url, text
    return None, raw_text


def replacements(text):
    for _ in range(4):
        text = text.replace('<span class="tg-spoiler">', '').replace('</span>', '')
        text = text.replace('&quot;', '"').replace("&#x27;", "'")
        text = text.replace('\n</b>', '</b>\n').replace('\n</i>', '</i>\n').replace('\n</u>', '</u>\n')
        text = text.replace('\n</s>', '</s>\n').replace('\n</code>', '</code>\n').replace('\n</a>', '</a>\n')
        text = text.replace('\n</pre>', '</pre>\n')
        text = text.replace('<pre>', '```').replace('</pre>', '\n```')
    return text


class TgIssueMessage:
    def __init__(self, text_html, from_user=False, from_reopen=False):
        self.issue_title = None
        self.issue_url = None
        self.repo_name = None
        self.repo_url = None
        self.assigned = None
        self.assigned_url = None
        self.comment = ''
        self.github_comment = None
        if from_user and from_reopen:
            raise ValueError('Recreate issue class possible with only one source: from bot, from_user or from_reopen')
        if from_user:
            self.__parse_text(text_html)
        elif from_reopen:
            self.__parse_reopen_text(text_html)
        else:
            self.__parse_bot_text(text_html)

    def __parse_text(self, text):
        text = replacements(text)
        if len(text.split('\n')) == 1:
            self.issue_title = text
            self.comment = ''
        else:
            self.issue_title = text.split('\n')[0]
            self.comment = '\n'.join(text.split('\n')[1:])

    def __parse_reopen_text(self, text):
        self.issue_url, self.issue_title = extract_href(text)
        self.set_issue_url(self.issue_url)

    def __parse_bot_text(self, text):
        text = replacements(text)
        st = text.split('\n')
        self.issue_url, self.issue_title = extract_href(st[0].replace('🏷 ', ''))
        self.repo_url, self.repo_name = extract_href(st[1].replace('🗄 ', '').replace('⚠️ ', ''))
        self.assigned_url, self.assigned = extract_href(st[2].replace('👤 ', ''))
        if len(st) > 3:
            self.comment = '\n'.join(st[3:])

    def is_created(self):
        return bool(self.issue_url)

    def get_close_message(self, closer_name):
        return f'Issue <a href="{self.issue_url}">{self.issue_title}</a> closed by {closer_name}'

    def get_problem_text(self, r):
        text = f'Problem with {self.issue_url}: {r["message"]}'
        logging.warning(text)
        return text

    def set_issue_url(self, issue_url):
        self.issue_url = issue_url
        self.repo_name = issue_url.split('/')[-3]
        self.repo_url = issue_url.split('/issues/')[0]

    def set_assigned(self, assigned):
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

        if self.comment:
            text += f'\n{self.comment}'

        return text
