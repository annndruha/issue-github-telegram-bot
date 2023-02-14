# Marakulin Andrey https://github.com/Annndruha
# 2023
import json
import logging

import requests


class Github:
    def __init__(self, organization_nickname, token):
        self.issue_url = 'https://api.github.com/repos/' + organization_nickname + '/{}/issues'
        self.org_repos_url = f'https://api.github.com/orgs/{organization_nickname}/repos'

        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    # def get_issue(self, number):
    #     url = '{}/{}'.format(self.url, number)
    #     response = requests.get(url, auth=self.auth)
    #     logging.info('Get issue: {}'.format(response))
    #     return response.json(), response.status_code
    #
    # def comment_issue(self, number, text):
    #     url = '{}/{}/comments'.format(self.url, number)
    #     payload = {'body': text}
    #     response = requests.post(url, json=payload, auth=self.auth)
    #     logging.info('Comment issue: {}'.format(response))
    #     return response.status_code
    #
    # def label_issue(self, number, label):
    #     url = '{}/{}/labels'.format(self.url, number)
    #     payload = [label.strip()]
    #     response = requests.post(url, json=payload, auth=self.auth)
    #     logging.info('Label issue: {}'.format(response))
    #     return response.status_code
    #

    def open_issue(self, repo, title, comment):
        payload = {'title': title, 'body': comment}
        r = requests.post(self.issue_url.format(repo), headers=self.headers, json=payload)
        logging.info('Open issue: {}'.format(r))
        return r

    def get_repos(self, page):
        data = {'sort': 'updated', 'per_page': 9, 'page': page}
        r = requests.get(self.org_repos_url, headers=self.headers, params=data)
        return r.json()

    def get_all_repos(self):
        data = {'sort': 'updated'}
        r = requests.get(self.org_repos_url, headers=self.headers, params=data)
        repos = r.json()
        return repos

    def close_issue(self, repo, number_str, comment=''):
        url = self.issue_url.format(repo) + '/' + number_str
        payload = {'state': 'closed', 'body': comment}
        response = requests.patch(url, headers=self.headers, json=payload)
        logging.info('Close issue: {}'.format(response))
        return response.status_code

    def get_issue(self, repo, number_str):
        url = self.issue_url.format(repo) + '/' + number_str
        r = requests.get(url, headers=self.headers)
        return r.json()

    # def get_comments(self, number):
    #     url = '{}/{}/comments'.format(self.url, number)
    #     response = requests.get(url, auth=self.auth)
    #     return response.json()
