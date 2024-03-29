# Bot for creation GitHub issue from Telegram chat

[![version](https://img.shields.io/github/v/release/annndruha/issue-github-telegram-bot)](https://github.com/annndruha/issue-github-telegram-bot/releases)
[![GitHub license](https://img.shields.io/github/license/annndruha/issue-github-telegram-bot.svg)](https://github.com/annndruha/issue-github-telegram-bot/blob/master/LICENSE)
[![python lint](https://github.com/annndruha/issue-github-telegram-bot/actions/workflows/linter.yml/badge.svg)](https://github.com/annndruha/issue-github-telegram-bot/actions/workflows/linter.yml/badge.svg)

Only for GitHub organizations repos issues (not for personal repos issues)

# Example usage:

In organization Telegram chat type `/issue` and write issue title (and optional description). Select repo and enjoy your issue!
![image](https://github.com/annndruha/issue-github-telegram-bot/assets/51162917/8eb3c8ee-b87b-4144-9846-6e9b8bce80b0)


# Setup

1. You need to create telegram bot via [BotFather](https://t.me/BotFather), get bot token and add it to group chat with access messages rights.
2. Use your personal GitHub account or create another account, get [GitHub token](https://github.com/settings/tokens).
Token scopes must include: `repo (full)`, `admin:org -> read:org`, `user -> read:user`. Add account to your GitHub orgainzation.

3. *[Option 1]*: Setup the GitHub runner Enviroment (see [deploy.yml](https://github.com/profcomff/issue-github-tgbot/blob/main/.github/workflows/deploy.yml)):

   secrets:
     * `BOT_TOKEN` - From step 1
     * `BOT_NICKNAME` - From step 1 (Must start with @)
     * `GH_ACCOUNT_TOKEN` - From step 2
   
   variables:
   * `GH_ORGANIZATION_NICKNAME` - Organization login (nickname) for manage issue

5. *[Option 2]*: Simple Docker run without GitHub runner:
   ```commandline
   docker run  --detach \
               --restart always \
               --env BOT_TOKEN='000000:token_value_from_botFather' \
               --env BOT_NICKNAME='@nickname_from_botFather' \
               --env GH_ACCOUNT_TOKEN='github_user_token' \
               --env GH_ORGANIZATION_NICKNAME='org_login' \
               ghcr.io/annndruha/issue-github-telegram-bot:latest
   ```
6. (Optional, but recommended):
   * Via [BotFather](https://t.me/BotFather) go to `Edit bot`/`Edit commands` and set this commands:
     ```
     start - Hello message
     help - Usage instruction
     md_guide - Markdown syntax instruction
     ```
   * After this in personal messages with bot you will see a `menu` button
