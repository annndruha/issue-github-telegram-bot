# Marakulin Andrey https://github.com/Annndruha
# 2023
import logging

import requests


class Github:
    def __init__(self, organization_nickname, token):
        self.organization_nickname = organization_nickname
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
        payload = {'title': title, 'body': comment, 'projects': f'{self.organization_nickname}/7'}
        r = requests.post(self.issue_url.format(repo), headers=self.headers, json=payload)
        if 'Issues are disabled for this repo' in r.text:
            raise GithubIssueDisabledError
        return r

    def get_repos(self, cursor=None):
        GRAPH_QL_URL = 'https://api.github.com/graphql'
        # data = {'sort': 'pushed', 'per_page': 9, 'page': page}
        # r = requests.get(self.org_repos_url, headers=self.headers, params=data)
        # return r.json()
        if cursor is None:
            GET_REPOS = {'query': """{
              repos: search(
                query: "org:%s archived:false fork:true is:public sort:updated"
                type: REPOSITORY
                first: 9
              ) {
                repositoryCount
                pageInfo {
                  hasNextPage
                  endCursor
                  hasPreviousPage
                  startCursor
                }
                edges {
                  node {
                    ... on Repository {
                      name
                      url
                    }
                  }
                }
              }
            }""" % self.organization_nickname}
        else:
            first_or_last = 'first' if 'first' in cursor else 'last'
            GET_REPOS = {'query': """{
              repos: search(
                query: "org:%s archived:false fork:true is:public sort:updated"
                type: REPOSITORY
                %s: 9
                %s
              ) {
                repositoryCount
                pageInfo {
                  hasNextPage
                  endCursor
                  hasPreviousPage
                  startCursor
                }
                edges {
                  node {
                    ... on Repository {
                      name
                      url
                    }
                  }
                }
              }
            }""" % (self.organization_nickname, first_or_last, cursor)}
        r = requests.post(url=GRAPH_QL_URL, json=GET_REPOS, headers=self.headers)
        resp = r.json()
        return resp['data']['repos']

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


def add_to_scrum(headers, issue_id):
    try:
        GRAPH_QL_URL = 'https://api.github.com/graphql'
        PROJECT_ID = 'PVT_kwDOBaPiZM4AFiz-'
        FIELD_ID = 'PVTSSF_lADOBaPiZM4AFiz-zgDMeOc'
        BACKLOG_OPTION_ID = '4a4a1bb5'

        add_item_to_scrum = {'query': 'mutation{ addProjectV2ItemById(input: {projectId: "%s" contentId: "%s"}) { '
                                      'item { id } } }' % (PROJECT_ID, issue_id)}
        with requests.session() as session:
            r = session.post(url=GRAPH_QL_URL, json=add_item_to_scrum, headers=headers)

            if 'errors' in r.json():
                logging.warning(f'Node {issue_id} not added to scrum. Reason: {r.json()["errors"]}')
                return
            logging.info(f'Node {issue_id} successfully added to scrum Твой ФФ!')

            project_node_id = r.json()['data']['addProjectV2ItemById']['item']['id']
            set_item_status_to_scrum = {'query': 'mutation {updateProjectV2ItemFieldValue(input: '
                                                 '{projectId: "%s", itemId: "%s", fieldId: '
                                                 '"%s",value: {singleSelectOptionId: "%s"}}) '
                                                 '{projectV2Item{id}}}' % (PROJECT_ID, project_node_id,
                                                                           FIELD_ID, BACKLOG_OPTION_ID)}

            r = session.post(url=GRAPH_QL_URL, json=set_item_status_to_scrum, headers=headers)
            if 'errors' in r.json():
                logging.warning(f'Node {issue_id} not set status. Reason: {r.json()["errors"]}')
            else:
                logging.info(f'Node {issue_id} successfully set backlog status.')
    except Exception as err:
        logging.error(f'Scrum adding FAILED: {err.args}')


class GithubIssueDisabledError(Exception):
    pass
