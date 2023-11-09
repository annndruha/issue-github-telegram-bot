# Marakulin Andrey https://github.com/Annndruha
# 2023

from dataclasses import dataclass


@dataclass
class Answers:
    start = '🤖 I\'m a <a href="https://github.com/Annndruha/issue-github-telegram-bot">bot</a>' \
            ' for creating a GitHub issue in <a href="https://github.com/{}">your organization</a> repositories' \
            ' directly from this chat. \nMore info in /help'
    help = 'For create an issue, mention me or call /issue and enter the title of the issue. ' \
           'If you want to provide a description, break the line after title and write a ' \
           'description. See more in markdown guide: /md_guide\n\n**Examples how to call me:**'
    help_example = '/issue Just only title'
    help_example2 = '/issue Issue title\nText description of issue\n'
    help_example3 = '{} Issue title\nCall via mention, and long description with some code example:\n' \
                    '```python\nimport bug\nbug.fix()```'
    no_title = 'After the mention, you need to enter the title of the issue. More in /help'
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
                        '\n`inline_code_block`' \
                        '\n\n```python' \
                        '\n# code block' \
                        '\nprint("Hello, issue bot!")' \
                        '\n```' \
                        '\n\n[link](github.com)' \
                        '\n![image_link](link.to/some_image.png)'
