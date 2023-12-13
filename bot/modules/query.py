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
from bot.helper.telegram_helper.button_build import ButtonMaker

def soup_res(link):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(link, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')

async def query_search(_, message):
    args = message.text.split()
    link = args[1] if len(args) > 1 else ''
    reply = await sendMessage(message, "Searching.....")
    base_url = "https://www9.gogoanimes.fi/search.html?keyword="
    search_url = f"{base_url}{link}"
    soup = soup_res(search_url)
    links = soup.find_all('a', href=re.compile(r'.*/category/.*'))
    
    unique_links = set()
    
    for r in links:
        anime_href = r['href']
        anime_link = f"https://www9.gogoanimes.fi{anime_href}"
        unique_links.add(anime_link)

    result = "\n".join(unique_links)
    await editMessage(reply, result)

bot.add_handler(MessageHandler(query_search, filters=command(BotCommands.QueryCommand) & CustomFilters.sudo))
