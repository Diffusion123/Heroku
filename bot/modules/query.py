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

async def query_search(_, message):
    btns = ButtonMaker()
    btns.ibutton('Back', f'wzmlx {user_id} stats home')
    if key == "home":
        btns = ButtonMaker()
        btns.ibutton('Bot Stats', f'wzmlx {user_id} stats stbot')
        btns.ibutton('OS Stats', f'wzmlx {user_id} stats stsys')
        btns.ibutton('Repo Stats', f'wzmlx {user_id} stats strepo')
        btns.ibutton('Bot Limits', f'wzmlx {user_id} stats botlimits')
        msg = "⌬ <b><i>Bot & OS Statistics!</i></b>"
    btns.ibutton('Close', f'wzmlx {user_id} close')
    return msg, btns.build_menu(2)
    
async def search_anime(query, message):
    reply = await sendMessage(message, "Searching.....")
    base_url = "https://www9.gogoanimes.fi/search.html?keyword="
    search_url = f"{base_url}{query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(search_url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=re.compile(r'.*/category/.*'))

    unique_links = set()  # Use a set to store unique links

    for r in links:
        anime_href = r['href']
        anime_link = f"https://www9.gogoanimes.fi{anime_href}"
        result = ""
        result += f"{anime_link}\n"
        await editMessage(reply, anime_link)


bot.add_handler(MessageHandler(query_search, filters=command(BotCommands.QueryCommand) & CustomFilters.sudo))
