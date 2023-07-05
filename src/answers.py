# Marakulin Andrey https://github.com/Annndruha
# 2023

ans = {
    'issue_open': '\n> Issue open by {} via {}',
    'assign_change': '\n> Assign changed from {} to @{} by {}.',
    'issue_close': '\n> Issue closed by {}.',
    'issue_reopen': '\n> Issue reopened by {}.',
    'help': 'Чтобы создать issue, упомяните меня и после упоминания введите название issue.'
            '\nЕсли вы хотите указать описание, после названия issue сделайте перенос строки'
            ' и напишите описание. Ниже пример сообщения для создания issue: \n\n'
            '{} Разобраться в синтаксисе Markdown\nВ этой issue мне необходимо прочитать про синтаксис Markdown.'
            '\nЯ могу это сделать вызвав команду бота: /md_guide',
    'start': '🤖 Я <a href="https://github.com/Annndruha/issue-github-telegram-bot">бот</a>'
             ' для создания issue в репозиториях '
             '<a href="https://github.com/{}">организации</a> в GitHub.'
             '\nЧтобы создать issue из личных сообщений, упомяните меня в вашем сообщении. Больше информации в /help',
    'markdown_guide_tg': '''
    Нативный стиль Telegram поддерживает следующее форматирование, которое преобразуется в Markdown в GitHub:
<i>italic</i>
<b>bold</b>
<u>underline</u>
<s>strike</s>
<code>monospace_code</code>
<span class="tg-spoiler">spoiler</span> (GitHub не поддерживает)
<a href="https://github.com">link</a>
''',
    'markdown_guide_md': '''
## А это синтаксис Markdown 
### Это раздел 3 уровня
* list_item
* list_item
  * sub_list_item
- [ ] Empty checkbox
- [x] Done checkbox
$latex = \\frac{e^5}{\pi}$
**bold**
*italic*
`inline_code_block`

|      markdown_table | version |
|--------------------:|---------|
|              Python | 3.11    |
| python-telegram-bot | 20.0    |

```python
# code block
print('Hello, issue bot!')
```
[md_link](github.com/annndruha/issue-github-telegram-bot)
![md_image_link](https://picsum.photos/200)
    '''
}
