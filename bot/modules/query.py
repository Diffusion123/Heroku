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
from bot.modules.scraper import soup_res, gogoanimes
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage, deleteMessage
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

async def query_search(_, message):
    text = message.text.split('\n')
    input_list = text[0].split(' ')

    arg_base = {'word': '', 
                '-g':'',
    }
    args = arg_parser(input_list[1:], arg_base)
    cmd = input_list[0].split('@')[0]

    word = args['word']
    gogoanimes = args['-g']

    if gogoanimes:
        await search_anime(cmd)
    
async def search_anime(query):
    base_url = "https://www9.gogoanimes.fi/search.html?keyword="
    search_url = f"{base_url}{query}"
    soup = soup_res(search_url)
    links = soup.find_all('a', href=re.compile(r'.*/category/.*'))
    for r in links:
        anime_href = r['href']
        anime_link = f"https://www9.gogoanimes.fi{anime_href}"
        await sendMessage(anime_link)
        
def arg_parser(items, arg_base):
    if not items:
        return arg_base
    bool_arg_set = {'-g', '-e', '-z', '-s', '-j', '-d'}
    t = len(items)
    i = 0
    arg_start = -1

    while i + 1 <= t:
        part = items[i].strip()
        if part in arg_base:
            if arg_start == -1:
                arg_start = i
            if i + 1 == t and part in bool_arg_set or part in ['-s', '-j']:
                arg_base[part] = True
            else:
                sub_list = []
                for j in range(i + 1, t):
                    item = items[j].strip()
                    if item in arg_base:
                        if part in bool_arg_set and not sub_list:
                            arg_base[part] = True
                        break
                    sub_list.append(item.strip())
                    i += 1
                if sub_list:
                    arg_base[part] = " ".join(sub_list)
        i += 1

    link = []
    if items[0].strip() not in arg_base:
        if arg_start == -1:
            link.extend(item.strip() for item in items)
        else:
            link.extend(items[r].strip() for r in range(arg_start))
        if link:
            arg_base['link'] = " ".join(link)
    return arg_base


bot.add_handler(MessageHandler(query_search, filters=command(BotCommands.QueryCommand) & CustomFilters.sudo))
