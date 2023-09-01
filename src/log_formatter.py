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
        if update.callback_query is None:
            logging.info(f'[{update.message.from_user.id} {update.message.from_user.full_name}] '
                         f'[{func.__name__}]: {repr(update.message.text)}')
        else:
            logging.info(f'[{update.callback_query.from_user.id} {update.callback_query.from_user.full_name}] '
                         f'[{update.callback_query.message.id}] [{func.__name__}] '
                         f'callback_data: {update.callback_query.data}')
        await func(update, context)

    return wrapper
