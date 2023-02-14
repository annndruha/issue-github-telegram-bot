# Marakulin Andrey https://github.com/Annndruha
# 2023

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
    # def close_issue(self, number):
    #     url = '{}/{}'.format(self.url, number)
    #     payload = {'state': 'closed'}
    #     response = requests.patch(url, json=payload, auth=self.auth)
    #     logging.info('Close issue: {}'.format(response))
    #     return response.status_code

    def open_issue(self, repo, title):
        data = {'title': f'{title}'}
        r = requests.post(self.issue_url.format(repo), headers=self.headers, data=data)
        logging.info('Open issue: {}'.format(r))
        return r

    def get_repos(self, page):
        data = {'sort': 'updated', 'per_page': 9, 'page': page}
        r = requests.get(self.org_repos_url, headers=self.headers, params=data)
        repos = r.json()
        return repos

    def get_all_repos(self):
        data = {'sort': 'updated'}
        r = requests.get(self.org_repos_url, headers=self.headers, params=data)
        repos = r.json()
        return repos

    # def get_comments(self, number):
    #     url = '{}/{}/comments'.format(self.url, number)
    #     response = requests.get(url, auth=self.auth)
    #     return response.json()
