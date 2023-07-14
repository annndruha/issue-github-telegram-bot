# Marakulin Andrey https://github.com/Annndruha
# 2023

from dataclasses import dataclass


@dataclass
class Answers:
    issue_open = '\n> Issue open by {} via {}'
    assign_change = '\n> Assign changed from {} to @{} by {}.'
    issue_close = '\n> Issue closed by {}.'
    issue_reopen = '\n> Issue reopened by {}.'
    no_title = 'After the mention, you need to enter the title of the issue. More in /help'
    help = 'To create an issue, mention me and after the mention enter the title of the issue.' \
           '\nIf you want to provide a description, after the title of the issue, break the line and write a ' \
           'description. Below is an example of a message to create an issue:\n\n' \
           '{} This is issue title\n' \
           'And start with this line is description' \
           '\nAnother line of description.\nSee more by calling the bot command: /md_guide'
    start = '🤖 I\'m <a href="https://github.com/Annndruha/issue-github-telegram-bot">bot</a>' \
            ' for create issue in GitHub <a href="https://github.com/{}">organization</a>' \
            '\nMore info in /help'
    markdown_guide_tg = '''
    Native Telegram styling are converted to Markdown in GitHub:
<i>italic</i>
<b>bold</b>
<u>underline</u>
<s>strike</s>
<code>monospace_code</code>
<span class="tg-spoiler">spoiler</span> (GitHub not supported)
<a href="https://github.com">link</a>
'''
    markdown_guide_md = '''
## This is Markdown syntax 
### Third level header
* list_item
* list_item
  * sub_list_item
- [ ] Empty checkbox
- [x] Done checkbox
$latex = \\frac{e^5}{\\pi}$
**bold**
*italic*
`inline_code_block`

|      markdown_table | version |
|--------------------:|---------|
|              Python | 3.11    |
| python-telegram-bot | 20.1    |

```python
# code block
print('Hello, issue bot!')
```
[md_link](github.com/annndruha/issue-github-telegram-bot)
    '''
