## Bot for creation GitHub issue straight from organization Telegram group chat

#### Setup

1. You need to create bot via [BotFather](https://t.me/BotFather) and get bot token
2. Use your personal account or create another account, get [github token](https://github.com/settings/tokens)
3. Next set the docker enviroment variables:
  * `BOT_TOKEN` - From step 1
  * `BOT_NICKNAME` - From step 1
  * `GH_ACCOUNT_TOKEN` - From step 2
  * `GH_ORGANIZATION_NICKNAME` - Organization nickname for manage issue

4. Run Docker Example:
```commandline
docker run -e BOT_TOKEN=value1 -e BOT_NICKNAME=value2 -e GH_ACCOUNT_TOKEN=value3 -e GH_ORGANIZATION_NICKNAME=value4
```
5. Add to bot to group chat

#### Usage
Use bot with mention like:
```
@issueOrgnameBot Issue name
Description, short and long
description continue
```
Next manage issue with bot keyboard. Have fun!