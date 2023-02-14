# Marakulin Andrey https://github.com/Annndruha
# 2023

import logging
import time
import traceback

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes, CallbackContext

from src.settings import get_settings

settings = get_settings()


def handler(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await func(update, context)
        except (TelegramError, Exception) as err:
            logging.error(f'Exception {str(err.args)}, traceback:')
            traceback.print_tb(err.__traceback__)
            time.sleep(2)
    return wrapper


@handler
async def handler_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Start message', disable_web_page_preview=True, parse_mode=ParseMode('HTML'))
    # keyboard_base = [[InlineKeyboardButton(ans['about'], callback_data='to_about')]]
    # text, reply_markup = __change_message_by_auth(update, ans['hello'], keyboard_base)
    # await update.message.reply_text(text=text,
    #                                 reply_markup=reply_markup,
    #                                 disable_web_page_preview=True)


@handler
async def handler_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Help message', disable_web_page_preview=True, parse_mode=ParseMode('HTML'))


@handler
async def handler_button(update: Update, context: CallbackContext) -> None:
    pass
    # if update.callback_query.data == 'to_hello':
    #     keyboard_base = [[InlineKeyboardButton(ans['about'], callback_data='to_about')]]
    #     text, reply_markup = __change_message_by_auth(update, ans['hello'], keyboard_base)
    #
    # elif update.callback_query.data == 'to_about':
    #     keyboard_base = [[InlineKeyboardButton(ans['back'], callback_data='to_hello')]]
    #     text, reply_markup = __change_message_by_auth(update, ans['help'], keyboard_base)
    #
    # elif update.callback_query.data == 'to_auth':
    #     keyboard_base = [[InlineKeyboardButton(ans['back'], callback_data='to_hello')]]
    #     text, reply_markup = ans['val_need'], InlineKeyboardMarkup(keyboard_base)
    #
    # elif update.callback_query.data.startswith('print_'):
    #     await __print_settings_solver(update, context)
    #     return
    #
    # else:
    #     text, reply_markup = ans['unknown_keyboard_payload'], None
    #
    # await update.callback_query.edit_message_text(text=text,
    #                                               reply_markup=reply_markup,
    #                                               disable_web_page_preview=True,
    #                                               parse_mode=ParseMode('HTML'))


@handler
async def handler_message(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('message message', disable_web_page_preview=True, parse_mode=ParseMode('HTML'))
