import locale
import sys
import os

BASE_PATH = os.environ.get('BASE_PATH')
sys.path.insert(1, BASE_PATH + '/telegram-bots/src')

from graphqlclient import GraphQLClient
import time
from datetime import datetime
import pprint
import os.path
import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext

import libraries.general_end_functions as general_end_functions
import libraries.commands_util as commands_util

# log_file
charts_path = BASE_PATH + 'log_files/chart_bot/'

locale.setlocale(locale.LC_ALL, 'en_US')

button_list_price = [[InlineKeyboardButton('refresh', callback_data='refresh_price')]]
reply_markup_price = InlineKeyboardMarkup(button_list_price)

graphql_client_uni = GraphQLClient('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2')
graphql_client_eth = GraphQLClient('https://api.thegraph.com/subgraphs/name/blocklytics/ethereum-blocks')

TELEGRAM_KEY = os.environ.get('FXSWAP_TELEGRAM_KEY')
contract = "0xe33586055d39b7d2d17be6f2ae0671447e98c72b"
name = "fxswap"
pair_contract = "0x2df4fb7be16693e4116da90d79712e031b35f599"
ticker = 'FXSWAP'
decimals = 1000000000000000000  # that's 18


def get_candlestick(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    query_received = update.message.text.split(' ')

    time_type, k_hours, k_days, tokens = commands_util.check_query(query_received, ticker)
    t_to = int(time.time())
    t_from = t_to - (k_days * 3600 * 24) - (k_hours * 3600)

    if isinstance(tokens, list):
        for token in tokens:
            general_end_functions.send_candlestick_pyplot(context, token, charts_path, k_days, k_hours, t_from, t_to,
                                                          chat_id)
    else:
        general_end_functions.send_candlestick_pyplot(context, tokens, charts_path, k_days, k_hours, t_from, t_to,
                                                      chat_id)


def get_price_token(update: Update, context: CallbackContext):
    message = general_end_functions.get_price(contract, pair_contract, graphql_client_eth, graphql_client_uni, name,
                                              decimals)
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode='html', reply_markup=reply_markup_price)


def refresh_chart(update: Update, context: CallbackContext):
    print("refreshing chart")
    query = update.callback_query.data

    k_hours = int(re.search(r'\d+', query.split('h:')[1]).group())
    k_days = int(re.search(r'\d+', query.split('d:')[1]).group())
    token = query.split('t:')[1]

    t_to = int(time.time())
    t_from = t_to - (k_days * 3600 * 24) - (k_hours * 3600)

    chat_id = update.callback_query.message.chat_id
    message_id = update.callback_query.message.message_id
    pprint.pprint(chat_id)

    (message, path, reply_markup_chart) = general_end_functions.send_candlestick_pyplot(token, charts_path, k_days,
                                                                                        k_hours, t_from, t_to)
    context.bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'), caption=message, parse_mode="html",
                           reply_markup=reply_markup_chart)
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)


def refresh_price(update: Update, context: CallbackContext):
    print("refreshing price")
    message = general_end_functions.get_price(contract, pair_contract, graphql_client_eth, graphql_client_uni,
                                              name, decimals)
    update.callback_query.edit_message_text(text=message, parse_mode='html', reply_markup=reply_markup_price)


def get_help(update: Update, context: CallbackContext):
    general_end_functions.get_help(update, context)


def main():
    updater = Updater(TELEGRAM_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('chart', get_candlestick))
    dp.add_handler(CommandHandler('price', get_price_token))
    dp.add_handler(CommandHandler('help', get_help))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

commands = """
chart - Display price chart of FxSwap.
price - Get current price of FxSwap.
help - How to use the bot
"""