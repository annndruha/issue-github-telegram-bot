# Marakulin Andrey https://github.com/Annndruha
# 2023
import logging

import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.requests import log as requests_logger
requests_logger.setLevel(logging.WARNING)


class Github:
    def __init__(self, organization_nickname, token):
        self.organization_nickname = organization_nickname
        self.issue_url = 'https://api.github.com/repos/' + organization_nickname + '/{}/issues'
        self.org_repos_url = f'https://api.github.com/orgs/{organization_nickname}/repos'
        self.org_members_url = f'https://api.github.com/orgs/{organization_nickname}/members'

        self.session = requests.Session()

        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        self.transport = RequestsHTTPTransport(
            url='https://api.github.com/graphql',
            verify=True,
            retries=3,
            headers=self.headers
        )

        with open('src/graphql/schema.github.graphql') as f:
            schema_str = f.read()

        self.client = Client(transport=self.transport, schema=schema_str)
        self.__read_queries()

    def __read_queries(self):
        with open('src/graphql/get_repos.graphql') as f:
            self.q_get_repos = gql(f.read())
        with open('src/graphql/add_to_scrum.graphql') as f:
            self.q_add_to_scrum = gql(f.read())

    def open_issue(self, repo, title, comment):
        payload = {'title': title, 'body': comment, 'projects': f'{self.organization_nickname}/7'}
        r = self.session.post(self.issue_url.format(repo), headers=self.headers, json=payload)
        if 'Issues are disabled for this repo' in r.text:
            raise GithubIssueDisabledError
        return r

    def old_get_repos(self, page=1):
        data = {'sort': 'pushed', 'per_page': 9, 'page': page}
        r = self.session.get(self.org_repos_url, headers=self.headers, params=data)
        return r.json()

    def get_repos(self, page_info):
        params = {'gh_query': f'org:{self.organization_nickname} archived:false fork:true is:public sort:updated'}
        if page_info == 'repos_start':
            r = self.client.execute(self.q_get_repos, operation_name='getReposInit', variable_values=params)
        elif page_info.startswith('repos_after'):
            params['cursor'] = page_info.split('_')[2]
            r = self.client.execute(self.q_get_repos, operation_name='getReposAfter', variable_values=params)
        else:  # repos_before
            params['cursor'] = page_info.split('_')[2]
            r = self.client.execute(self.q_get_repos, operation_name='getReposBefore', variable_values=params)
        return r['repos']

    def close_issue(self, issue_url, comment=''):
        url = issue_url.replace('https://github.com', 'https://api.github.com/repos')
        payload = {'state': 'closed', 'body': comment}
        r = self.session.patch(url, headers=self.headers, json=payload)
        return r

    def reopen_issue(self, issue_url, comment=''):
        url = issue_url.replace('https://github.com', 'https://api.github.com/repos')
        payload = {'state': 'open', 'body': comment}
        r = self.session.patch(url, headers=self.headers, json=payload)
        return r.json(), r.status_code

    def get_issue(self, issue_url):
        url = issue_url.replace('https://github.com', 'https://api.github.com/repos')
        r = self.session.get(url, headers=self.headers)
        return r.json(), r.status_code

    def get_members(self, page):
        data = {'sort': 'full_name', 'per_page': 9, 'page': page}
        r = self.session.get(self.org_members_url, headers=self.headers, params=data)
        return r.json()

    def set_assignee(self, issue_url, member_login, comment):
        url = issue_url.replace('https://github.com', 'https://api.github.com/repos')
        payload = {'assignees': [member_login], 'body': comment}
        r = self.session.patch(url, headers=self.headers, json=payload)
        return r

    def add_to_scrum(self, node_id):
        try:
            params = {'projectId': 'PVT_kwDOBaPiZM4AFiz-',
                      'contentId': node_id}
            r = self.client.execute(self.q_add_to_scrum, operation_name='addToScrum', variable_values=params)
    
            item_id = r['addProjectV2ItemById']['item']['id']
            logging.info(f'Node {node_id} successfully added to scrum with contentId= {item_id}')
    
            params = {'projectId': 'PVT_kwDOBaPiZM4AFiz-',
                      'itemId': item_id,
                      'fieldId': 'PVTSSF_lADOBaPiZM4AFiz-zgDMeOc',
                      'value': '4a4a1bb5'}  # BACKLOG_OPTION_ID
            r = self.client.execute(self.q_add_to_scrum, operation_name='setScrumStatus', variable_values=params)
            if 'errors' in r:
                logging.warning(f'''itemId={item_id} not set status. Reason: {r['errors']}''')
        except Exception as err:
            logging.error(f'Scrum adding FAILED: {err.args}')


class GithubIssueDisabledError(Exception):
    pass
