# Marakulin Andrey https://github.com/Annndruha
# 2023
import logging

import requests


class Github:
    def __init__(self, organization_nickname, token):
        self.organization_nickname = organization_nickname
        self.issue_url = 'https://api.github.com/repos/' + organization_nickname + '/{}/issues'
        self.graphql_url = 'https://api.github.com/graphql'
        self.org_repos_url = f'https://api.github.com/orgs/{organization_nickname}/repos'
        self.org_members_url = f'https://api.github.com/orgs/{organization_nickname}/members'

        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def open_issue(self, repo, title, comment):
        payload = {'title': title, 'body': comment, 'projects': f'{self.organization_nickname}/7'}
        r = requests.post(self.issue_url.format(repo), headers=self.headers, json=payload)
        if 'Issues are disabled for this repo' in r.text:
            raise GithubIssueDisabledError
        return r

    def get_repos(self, page):
        data = {'sort': 'pushed', 'per_page': 9, 'page': page}
        r = requests.get(self.org_repos_url, headers=self.headers, params=data)
        return r.json()

    def close_issue(self, repo, number_str, comment=''):
        url = self.issue_url.format(repo) + '/' + number_str
        payload = {'state': 'closed', 'body': comment}
        r = requests.patch(url, headers=self.headers, json=payload)
        return r

    def reopen_issue(self, repo, number_str):
        url = self.issue_url.format(repo) + '/' + number_str
        payload = {'state': 'open'}
        r = requests.patch(url, headers=self.headers, json=payload)
        return r.json(), r.status_code

    def get_issue(self, repo, number_str):
        url = self.issue_url.format(repo) + '/' + number_str
        r = requests.get(url, headers=self.headers)
        return r.json(), r.status_code

    def get_issue_human_link(self, repo, number_str):
        url = self.issue_url.format(repo) + '/' + number_str
        return url.replace('api.github.com/repos', 'github.com')

    def get_members(self, page):
        data = {'sort': 'full_name', 'per_page': 9, 'page': page}
        r = requests.get(self.org_members_url, headers=self.headers, params=data)
        return r.json()

    def set_assignee(self, repo, number_str, member_login, comment):
        url = self.issue_url.format(repo) + '/' + number_str
        payload = {'assignees': [member_login], 'body': comment}
        r = requests.patch(url, headers=self.headers, json=payload)
        return r

    def add_to_scrum(self, node_id):
        try:
            PROJECT_ID = 'PVT_kwDOBaPiZM4AFiz-'
            add_item_to_scrum = {'query': 'mutation{ addProjectV2ItemById(input: {projectId: "%s" contentId: "%s"}) { '
                                          'item { id } } }' % (PROJECT_ID, node_id)}
            r = requests.post(url=self.graphql_url, json=add_item_to_scrum, headers=self.headers)

            if 'errors' not in r.json():
                logging.info(f'Node {node_id} successfully added to scrum Твой ФФ!')
            else:
                logging.warning(f'Node {node_id} not added to scrum. Reason: {r.json()["errors"]}')

            FIELD_ID = 'PVTSSF_lADOBaPiZM4AFiz-zgDMeOc'
            BACKLOG_OPTION_ID = '4a4a1bb5'
            set_item_status_to_scrum = {'query': 'mutation {updateProjectV2ItemFieldValue(input: '
                                                 '{projectId: "%s", itemId: "%s", fieldId: '
                                                 '"%s",value: {singleSelectOptionId: "%s"}}) '
                                                 '{projectV2Item{id}}}' % (PROJECT_ID, node_id,
                                                                           FIELD_ID, BACKLOG_OPTION_ID)}

            r = requests.post(url=self.graphql_url, json=set_item_status_to_scrum, headers=self.headers)
            if 'errors' not in r.json():
                logging.info(f'Node {node_id} successfully set backlog status.')
            else:
                logging.warning(f'Node {node_id} not set status. Reason: {r.json()["errors"]}')
        except Exception as err:
            logging.error(f'Scrum adding FAILED: {err.args}')


class GithubIssueDisabledError(Exception):
    pass
