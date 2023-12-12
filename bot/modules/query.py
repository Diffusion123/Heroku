import re 
import json
import base64
import requests
import urllib.parse
from asyncio import sleep
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse

from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage, deleteMessage
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

async def query_search(query, message):
    text = message.text.split('\n')
    input_list = text[0].split(' ')

    arg_base = {'link': '', 
                '-g':'',
    }

    args = arg_parser(input_list[1:], arg_base)
    cmd = input_list[0].split('@')[0]

    word          = args['word']
    gogoanimes   = args['-g']

    









bot.add_handler(MessageHandler(query_search, filters=command(BotCommands.QueryCommand) & CustomFilters.sudo))
