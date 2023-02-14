# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging

import requests


class Github:
    def __init__(self, organization_nickname, token):
        self.issue_url = 'https://api.github.com/repos/' + organization_nickname + '/{}/issues'
        self.org_repos_url = f'https://api.github.com/orgs/{organization_nickname}/repos'
        self.org_members_url = f'https://api.github.com/orgs/{organization_nickname}/members'

        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def open_issue(self, repo, title, comment):
        payload = {'title': title, 'body': comment}
        r = requests.post(self.issue_url.format(repo), headers=self.headers, json=payload)
        logging.info('Open issue: {}'.format(r))
        return r

    def get_repos(self, page):
        data = {'sort': 'full_name', 'per_page': 9, 'page': page}
        r = requests.get(self.org_repos_url, headers=self.headers, params=data)
        return r.json()

    def close_issue(self, repo, number_str, comment=''):
        url = self.issue_url.format(repo) + '/' + number_str
        payload = {'state': 'closed', 'body': comment}
        r = requests.patch(url, headers=self.headers, json=payload)
        if r.status_code != 200:
            raise GithubApiError
        logging.info('Close issue: {}'.format(r))

    def get_issue(self, repo, number_str):
        url = self.issue_url.format(repo) + '/' + number_str
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            raise GithubApiError
        return r.json()

    def get_members(self, page):
        data = {'sort': 'full_name', 'per_page': 9, 'page': page}
        r = requests.get(self.org_members_url, headers=self.headers, params=data)
        return r.json()

    def set_assignee(self, repo, number_str, member_login, comment):
        url = self.issue_url.format(repo) + '/' + number_str
        payload = {'assignees': [member_login], 'body': comment}
        r = requests.patch(url, headers=self.headers, json=payload)
        logging.info('Set assignee issue: {}'.format(r))
        if r.status_code != 200:
            raise GithubApiError


class GithubApiError(Exception):
    pass
