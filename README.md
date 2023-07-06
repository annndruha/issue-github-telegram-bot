## Bot for creation GitHub issue from Telegram chat
Only for GitHub organizations repos issues (not for personal repos issues)

#### Setup

1. You need to create telegram bot via [BotFather](https://t.me/BotFather) and get bot token
2. Use your personal GitHub account or create another account, get [GitHub token](https://github.com/settings/tokens)
3. Next set the docker environment secrets:
   * `BOT_TOKEN` - From step 1
   * `BOT_NICKNAME` - From step 1
   * `GH_ACCOUNT_TOKEN` - From step 2
4. and environment variables
   * `GH_ORGANIZATION_NICKNAME` - Organization nickname for manage issue
   * `DOCKER_CONTAINER_NAME` - Name of docker container
   * `GH_SCRUM_STATE` - Set to 0 if you doesn't want to automatically add new issue to scrum board, else read Scrum setup
   * `GH_SCRUM_ID` - Value doesn't matter if GH_SCRUM_STATE=0
   * `GH_SCRUM_FIELD_ID` - Value doesn't matter if GH_SCRUM_STATE=0
   * `GH_SCRUM_FIELD_DEFAULT_STATE` - Value doesn't matter if GH_SCRUM_STATE=0

5. Run Docker Example:
   ```commandline
   docker run -e BOT_TOKEN=value1
              -e BOT_NICKNAME=value2
              -e GH_ACCOUNT_TOKEN=value3
              -e GH_ORGANIZATION_NICKNAME=value4
              -e ...
   ```
6. Add to bot to group chat

#### Example

![image](https://user-images.githubusercontent.com/51162917/225610117-0a5689ec-1742-4c11-8938-de8d098b5092.png)

#### Scrum setup
If you want to automatically add new issue to scrum board set `GH_SCRUM_STATE=1`
and set:
* `GH_SCRUM_ID` - this is identifier of scrum board
* `GH_SCRUM_FIELD_ID` - this is identifier of field in scrum board (e.g. columns)
* `GH_SCRUM_FIELD_DEFAULT_STATE` - this is default field(column) state (e.g. backlog)

You can find this id's with only with GraphQL requests ([use Explorer](https://docs.github.com/ru/graphql/overview/explorer)):

```graphql
# This query return scrum project's id's (GH_SCRUM_ID). Bot only can add issue only to one project
{organization(login: "GH_ORGANIZATION_NICKNAME") {
    projectsV2(first: 100) {
      edges {
        node {
          title
          id
          public
}}}}}

# Use GH_SCRUM_ID for next request.
# Usually, if you want to set column automatically, you need results from ProjectV2SingleSelectField
# GH_SCRUM_FIELD_ID is id
# GH_SCRUM_FIELD_DEFAULT_STATE is options id

{node(id: "GH_SCRUM_ID") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field {
            id
            name
          }
          ... on ProjectV2IterationField {
            id
            name
            configuration {
              iterations {
                startDate
                id
              }
            }
          }
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
                id
                name
}}}}}}}
```
