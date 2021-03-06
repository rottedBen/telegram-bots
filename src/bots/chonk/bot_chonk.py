import locale
import sys
import os
from gevent import monkey
monkey.patch_all()  # REALLY IMPORTANT: ALLOWS ZERORPC AND TG TO WORK TOGETHER

BASE_PATH = os.environ.get('BASE_PATH')
sys.path.insert(1, BASE_PATH + '/telegram-bots/src')

from twython import Twython, TwythonError
from graphqlclient import GraphQLClient
import time
from datetime import datetime
import pprint
import os.path
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

import libraries.graphs_util as graphs_util
import libraries.general_end_functions as general_end_functions
import libraries.commands_util as commands_util
import libraries.scrap_websites_util as scrap_websites_util
import libraries.util as util
from libraries.uniswap import Uniswap
from libraries.common_values import *
from web3 import Web3
import zerorpc


# ZERORPC
zerorpc_client_data_aggregator = zerorpc.Client()
zerorpc_client_data_aggregator.connect("tcp://127.0.0.1:4243")
pprint.pprint(zerorpc_client_data_aggregator.hello("coucou"))

# web3
infura_url = os.environ.get('INFURA_URL')
pprint.pprint(infura_url)
w3 = Web3(Web3.HTTPProvider(infura_url))
uni_wrapper = Uniswap(web3=w3)

button_list_price = [[InlineKeyboardButton('refresh', callback_data='refresh_price')]]
reply_markup_price = InlineKeyboardMarkup(button_list_price)


# log_file
charts_path = BASE_PATH + 'log_files/chart_bot/'

locale.setlocale(locale.LC_ALL, 'en_US')

graphql_client_uni = GraphQLClient('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2')
graphql_client_eth = GraphQLClient('https://api.thegraph.com/subgraphs/name/blocklytics/ethereum-blocks')


APP_KEY = os.environ.get('TWITTER_API_KEY')
APP_SECRET = os.environ.get('TWITTER_API_KEY_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
ACCESS_SECRET_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')


TELEGRAM_KEY = os.environ.get('CHONK_TELEGRAM_KEY')
contract = "0x84679bc467DC6c2c40ab04538813AfF3796351f1".lower()
name = "CHONK"
pair_contract = "0x7835a44f91b9d196076cb2b38280bbc4bf237924"
ticker = 'CHONK'
decimals = 1000000000000000000  # that's 18


twitter = Twython(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_SECRET_TOKEN)


# button refresh: h:int-d:int-t:token
def get_candlestick(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    query_received = update.message.text.split(' ')

    time_type, k_hours, k_days, tokens = commands_util.check_query(query_received, ticker)
    t_to = int(time.time())
    t_from = t_to - (k_days * 3600 * 24) - (k_hours * 3600)

    banner_txt = util.get_banner_txt(zerorpc_client_data_aggregator)

    if isinstance(tokens, list):
        for token in tokens:
            (message, path, reply_markup_chart) = general_end_functions.send_candlestick_pyplot(token, charts_path, k_days, k_hours, t_from, t_to, banner_txt)
            util.create_and_send_vote(token, "chart", update.message.from_user.name, zerorpc_client_data_aggregator)
            context.bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'), caption=message, parse_mode="html", reply_markup=reply_markup_chart)
    else:
        (message, path, reply_markup_chart) = general_end_functions.send_candlestick_pyplot(tokens, charts_path, k_days, k_hours, t_from, t_to, banner_txt)
        util.create_and_send_vote(tokens, "chart", update.message.from_user.name, zerorpc_client_data_aggregator)
        context.bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'), caption=message, parse_mode="html", reply_markup=reply_markup_chart)


def get_price_token(update: Update, context: CallbackContext):
    message = general_end_functions.get_price(contract, pair_contract, graphql_client_eth, graphql_client_uni, name, decimals)
    chat_id = update.message.chat_id
    util.create_and_send_vote(name, "price", update.message.from_user.name, zerorpc_client_data_aggregator)
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode='html', reply_markup=reply_markup_price, disable_web_page_preview=True)


def refresh_chart(update: Update, context: CallbackContext):
    print("refreshing chart")
    query = update.callback_query.data

    k_hours = int(re.search(r'\d+', query.split('h:')[1]).group())
    k_days = int(re.search(r'\d+', query.split('d:')[1]).group())
    token = query.split('t:')[1]

    t_to = int(time.time())
    t_from = t_to - (k_days * 3600 * 24) - (k_hours * 3600)

    banner_txt = util.get_banner_txt(zerorpc_client_data_aggregator)

    chat_id = update.callback_query.message.chat_id
    message_id = update.callback_query.message.message_id

    (message, path, reply_markup_chart) = general_end_functions.send_candlestick_pyplot(token, charts_path, k_days, k_hours, t_from, t_to, banner_txt)
    context.bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'), caption=message, parse_mode="html", reply_markup=reply_markup_chart)
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)


def refresh_price(update: Update, context: CallbackContext):
    print("refreshing price")
    message = general_end_functions.get_price(contract, pair_contract, graphql_client_eth, graphql_client_uni,
                                              name, decimals)
    update.callback_query.edit_message_text(text=message, parse_mode='html', reply_markup=reply_markup_price, disable_web_page_preview=True)


def get_help(update: Update, context: CallbackContext):
    general_end_functions.get_help(update, context)


def get_twitter(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    res = scrap_websites_util.get_last_tweets(twitter, ticker)
    context.bot.send_message(chat_id=chat_id, text=res, parse_mode='html', disable_web_page_preview=True)


def delete_message(update: Update, context: CallbackContext):
    print("deleting chart")
    chat_id = update.callback_query.message.chat_id
    message_id = update.callback_query.message.message_id
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)


def get_latest_actions(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    query_received = update.message.text.split(' ')
    if len(query_received) == 1:
        latest_actions_pretty = general_end_functions.get_last_actions_token_in_eth_pair(name, uni_wrapper, graphql_client_uni)
        context.bot.send_message(chat_id=chat_id, text=latest_actions_pretty, disable_web_page_preview=True, parse_mode='html')
    elif len(query_received) == 2:
        token_ticker = query_received[1]
        latest_actions_pretty = general_end_functions.get_last_actions_token_in_eth_pair(token_ticker, uni_wrapper, graphql_client_uni)
        context.bot.send_message(chat_id=chat_id, text=latest_actions_pretty, disable_web_page_preview=True, parse_mode='html')
    else:
        context.bot.send_message(chat_id=chat_id, text="Please use the format /last_actions TOKEN_TICKER")


def get_trending(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    res = zerorpc_client_data_aggregator.view_trending()
    context.bot.send_message(chat_id=chat_id, text=res)


def main():
    updater = Updater(TELEGRAM_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('chart', get_candlestick))
    dp.add_handler(CommandHandler('price', get_price_token))
    dp.add_handler(CommandHandler('trending', get_trending))
    dp.add_handler(CallbackQueryHandler(refresh_chart, pattern='refresh_chart(.*)'))
    dp.add_handler(CallbackQueryHandler(refresh_price, pattern='refresh_price'))
    dp.add_handler(CallbackQueryHandler(delete_message, pattern='delete_message'))
    dp.add_handler(CommandHandler('help', get_help))
    dp.add_handler(CommandHandler('twitter', get_twitter))
    dp.add_handler(CommandHandler('last_actions', get_latest_actions))
    dp.add_handler(CommandHandler('trending', get_trending))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

commands = """
chart - Display a chart of the price.
price - Get the current price.
help - How to use the bot.
twitter - Get the last tweets with the token marker.
trending - See which coins are trending in dextrends
"""
