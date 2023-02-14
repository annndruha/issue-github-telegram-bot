## Bot for creation GitHub issue straight from organization Telegram group chat

#### Setup

* You need to create bot via [BotFather](https://t.me/BotFather) and get bot token
* Use your personal account or create another account, get [github token](https://github.com/settings/tokens)
* Next set the docker enviroment variables:
  * `BOT_TOKEN` - From step 1
  * `BOT_NICKNAME` - From step 1
  * `GITHUB_ACCOUNT_TOKEN` - From step 2
  * `GITHUB_ORGANIZATION_NICKNAME` - Organization nickname for manage issue
* Add to bot to group chat

#### Usage
Use bot with mention like:
```
@issueOrgnameBot Issue name
Description, short and long
description continue
```
Next manage issue with bot keyboard. Have fun!