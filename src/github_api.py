# Marakulin Andrey https://github.com/Annndruha
# 2023

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class Github:
    """
    Class for proceed GraphQL query's
    """
    def __init__(self, settings):
        self.settings = settings

        self.transport = RequestsHTTPTransport(
            url='https://api.github.com/graphql',
            verify=True,
            retries=1,
            headers={'Authorization': f'Bearer {settings.GH_ACCOUNT_TOKEN}'}
        )

        self.client = Client(transport=self.transport)
        self.__read_queries()

    def __read_queries(self):
        with open('src/graphql/repositories.graphql') as f:
            self.q_get_repos = gql(f.read())
        with open('src/graphql/members.graphql') as f:
            self.q_get_members = gql(f.read())
        with open('src/graphql/issues.graphql') as f:
            self.q_issue_actions = gql(f.read())

    def open_issue(self, repo_id, title, body):
        params = {'repositoryId': repo_id, 'title': title, 'body': body}
        return self.client.execute(self.q_issue_actions, operation_name='CreateIssue', variable_values=params)

    def transfer_issue(self, new_repo_id, issue_id):
        params = {'repositoryId': new_repo_id, 'issueId': issue_id}
        return self.client.execute(self.q_issue_actions, operation_name='TransferIssue', variable_values=params)

    def get_repos(self, page_info):
        params = {'org': self.settings.GH_ORGANIZATION_NICKNAME}
        if page_info == 'rps_start':  # start page
            r = self.client.execute(self.q_get_repos, operation_name='GetReposInit', variable_values=params)
        elif page_info.startswith('rps_af'):  # next page
            params['cursor'] = page_info.split('_', 2)[2]
            r = self.client.execute(self.q_get_repos, operation_name='GetReposAfter', variable_values=params)
        else:  # previous page
            params['cursor'] = page_info.split('_', 2)[2]
            r = self.client.execute(self.q_get_repos, operation_name='GetReposBefore', variable_values=params)
        return r['organization']['repositories']

    def get_members(self, page_info):
        params = {'org': self.settings.GH_ORGANIZATION_NICKNAME}
        if page_info == 'members_start':  # start page
            r = self.client.execute(self.q_get_members, operation_name='GetMembersInit', variable_values=params)
        elif page_info.startswith('members_after'):  # next page
            params['cursor'] = page_info.split('_', 2)[2]
            r = self.client.execute(self.q_get_members, operation_name='GetMembersAfter', variable_values=params)
        else:  # previous page
            params['cursor'] = page_info.split('_', 2)[2]
            r = self.client.execute(self.q_get_members, operation_name='GetMembersBefore', variable_values=params)
        return r['organization']['membersWithRole']

    def close_issue(self, issue_id):
        params = {'issueId': issue_id}
        return self.client.execute(self.q_issue_actions, operation_name='CloseIssue', variable_values=params)

    def reopen_issue(self, issue_id):
        params = {'issueId': issue_id}
        return self.client.execute(self.q_issue_actions, operation_name='ReopenIssue', variable_values=params)

    def set_assignee(self, issue_id, member_id):
        params = {'issueId': issue_id, 'assigneeIds': [member_id]}
        return self.client.execute(self.q_issue_actions, operation_name='SetIssueAssign', variable_values=params)
