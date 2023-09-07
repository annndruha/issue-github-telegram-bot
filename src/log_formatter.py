# Marakulin Andrey https://github.com/Annndruha
# 2023

import functools
import logging

from telegram import Update
from telegram.ext import ContextTypes


def log_formatter(func):
    """
    Every time for bot event print an actor and handler name. Optional print a message id and callback_data
    """

    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        actor_handler = f'[{update.effective_user.id} {update.effective_user.full_name}] [{func.__name__}]'
        if update.callback_query is not None:
            logging.info(f'{actor_handler} [callback {update.callback_query.message.id}]: {update.callback_query.data}')
        elif update.message is not None:
            if update.message.text is not None:
                logging.info(f'{actor_handler} [text]: {repr(update.message.text)}')
            elif update.message.caption is not None:
                logging.info(f'{actor_handler} [caption]: {repr(update.message.caption)}')
            else:
                logging.info(f'{actor_handler} [UNKNOWN MESSAGE TYPE]')
        else:
            logging.info(f'{actor_handler} [UNKNOWN UPDATE TYPE]')

        await func(update, context)

    return wrapper
