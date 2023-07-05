## Bot for creation GitHub issue from Telegram chat
Only for GitHub organizations (not for personal accounts)

#### Setup

1. You need to create telegram bot via [BotFather](https://t.me/BotFather) and get bot token
2. Use your personal GitHub account or create another account, get [GitHub token](https://github.com/settings/tokens)
3. Next set the docker environment secrets:
   * `BOT_TOKEN` - From step 1
   * `BOT_NICKNAME` - From step 1
   * `GH_ACCOUNT_TOKEN` - From step 2
4. and environment variables
   * `GH_ORGANIZATION_NICKNAME` - Organization nickname for manage issue
   * `DOCKER_CONTAINER_NAME` - Name docker for container

5. Run Docker Example:
   ```commandline
   docker run -e BOT_TOKEN=value1 -e BOT_NICKNAME=value2 -e GH_ACCOUNT_TOKEN=value3 -e GH_ORGANIZATION_NICKNAME=value4
   ```
6. Add to bot to group chat

#### Example

![image](https://user-images.githubusercontent.com/51162917/225610117-0a5689ec-1742-4c11-8938-de8d098b5092.png)
