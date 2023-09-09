# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging
import traceback

from gql.transport.exceptions import (TransportAlreadyConnected,
                                      TransportError, TransportQueryError)
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes


def errors_solver(func):
    """
    This is decorator for telegram handlers that catches any type of exceptions.
    If exception is possible to solve, this handler send message with exception type.
    Else just log it.
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await func(update, context)
        except TelegramError as err:
            logging.error(f'TelegramError: {str(err.message)}')
        except TransportAlreadyConnected as err:
            logging.warning(f'TransportAlreadyConnected: {err.args}')
            await context.bot.answer_callback_query(callback_query_id=update.callback_query.id,
                                                    text='The previous request not done yet.\nPlease wait...')
        except TransportQueryError as err:
            logging.warning(f'Failed to proceed Issue: {err}')

            if 'type' not in err.errors[0]:
                text = err.errors[0]['message']
            else:
                match err.errors[0]['type']:
                    case 'NOT_FOUND':
                        text = 'Issue not found. Probably deleted.'
                        await update.callback_query.edit_message_text(text=text)
                    case 'FORBIDDEN':
                        text = 'Issue disabled for this repo'
                    case 'INSUFFICIENT_SCOPES':
                        text = err.errors[0]['message'].replace(
                            " Please modify your token's scopes at: https://github.com/settings/tokens.", "").replace(
                            "Your token has not been granted the required scopes to execute this query. ", "")
                    case _:
                        text = err.errors[0]['message']

            await context.bot.answer_callback_query(callback_query_id=update.callback_query.id, text=text)
        except TransportError as err:
            logging.warning(f'TransportError: {err.args}')
            await context.bot.answer_callback_query(callback_query_id=update.callback_query.id, text=err.args)
        except Exception as err:
            logging.error(err)
            traceback.print_tb(err.__traceback__)

    return wrapper
