## Bot for creation GitHub issue from Telegram chat
Only for GitHub organizations repos issues (not for personal repos issues)

#### Example usage:

In organization Telegram chat mention bot and write issue title (and optional description)
![image](https://github.com/annndruha/issue-github-telegram-bot/assets/51162917/26d7e781-b1d8-40d7-9dd2-ca72afdb92d8)


#### Setup

1. You need to create telegram bot via [BotFather](https://t.me/BotFather) and get bot token
2. Use your personal GitHub account or create another account, get [GitHub token](https://github.com/settings/tokens).
Token scopes must include: `repo (full)`, `admin:org -> read:org`, `user -> read:user`, `project -> read:project`

3. Next set the docker environment secrets:
   * `BOT_TOKEN` - From step 1
   * `BOT_NICKNAME` - From step 1
   * `GH_ACCOUNT_TOKEN` - From step 2
4. and environment variables
   * `GH_ORGANIZATION_NICKNAME` - Organization login (nickname) for manage issue
   * `DOCKER_CONTAINER_NAME` - Name of docker container

5. Run Docker Example (Or use `deploy.yml`):
   ```commandline
   docker run  --detach \
               --restart always \
               --env BOT_TOKEN='some_token_from_botFather' \
               --env BOT_NICKNAME='nickname_from_botFather' \
               --env GH_ACCOUNT_TOKEN='github_user_token' \
               --env GH_ORGANIZATION_NICKNAME='org_login' \
               ghcr.io/annndruha/issue-github-telegram-bot:latest
   ```
6. Add to bot to group chat
