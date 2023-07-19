# Marakulin Andrey https://github.com/Annndruha
# 2023

from dataclasses import dataclass


@dataclass
class Answers:
    start = '🤖 I\'m a <a href="https://github.com/Annndruha/issue-github-telegram-bot">bot</a>' \
            ' for creating a GitHub issue in <a href="https://github.com/{}">your organization</a> repositories' \
            ' directly from this chat. \nMore info in /help'
    help = 'For create an issue, mention me and enter the title of the issue.' \
           '\nIf you want to provide a description, after the title break the line and write a ' \
           'description. Below is an example of a message to create an issue:' \
           '\n\n{} Issue title\nDescription of issue\nSee more by calling the bot command: /md_guide'
    no_title = 'After the mention, you need to enter the title of the issue. More in /help'
    # issue_open = '\n> Issue open by {} via {}'
    # assign_change = '\n> Assign changed from {} to @{} by {}.'
    # issue_close = '\n> Issue closed by {}.'
    # issue_reopen = '\n> Issue reopened by {}.'
    markdown_guide_tg = 'Supported Telegram styling which will be properly converted to GitHub Markdown:' \
                        '\n\n<i>italic</i>' \
                        '\n<b>bold</b>' \
                        '\n<s>strike</s>' \
                        '\n<code>monospace_code</code>' \
                        '\n<a href="https://github.com">link</a>'
    markdown_guide_md = '# Markdown syntax ' \
                        '\n### Third level header' \
                        '\n\n* list_item' \
                        '\n  * sub_list_item' \
                        '\n\n- [ ] Empty checkbox' \
                        '\n- [x] Done checkbox' \
                        '\n\n$latex = \\frac{e^5}{\\pi}$' \
                        '\n**bold**' \
                        '\n*italic*' \
                        '\n`inline_code_block `' \
                        '\n\n```python' \
                        '\n# code block' \
                        '\nprint("Hello, issue bot!")' \
                        '\n```' \
                        '\n\n[link](github.com)'\
                        '\n![image_link](link.to/some_image.png)'
