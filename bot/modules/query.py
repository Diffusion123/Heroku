import re
import requests
import urllib.parse
from asyncio import sleep
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, quote

from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage, deleteMessage
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.telegram_helper.button_build import ButtonMaker

async def query(_, message):
    if "-animedao" in message.text:
        await anidao_search(message)

def soup_res(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

async def anidao_search(message):
    s = quote(message.split(' ', 1)[1].rsplit(' ', 1)[0])
    search_url = f"https://animedao.bz/search.html?keyword={s}"
    soup = soup_res(search_url)
    links = soup.find_all('a', href=re.compile(r'.*anime/.*'))
    for link in links:
        t = link['href']
        new_url = f"https://animedao.bz{t}"
        await animedao(new_url, message)

async def animedao(link, message):
    soup = soup_res(link)
    links = soup.find_all('a', {'class': "episode_well_link"}, href=re.compile(r'.*watch-online.*'))
    urls = []
    for sub in links:
        l_sub = sub['href']
        part = link.split('/')[2]
        mid = f"https://{part}"
        anime = mid + l_sub
        urls.append(anime)
        
    for final in reversed(urls):
        await animedao_files(final, message)

async def animedao_files(link, message):
    reply = await sendMessage(message, "Searching for the results")
    soup = soup_res(link)
    links = soup.find_all('a', {'data-video': re.compile(r'.*(awish|dood|alions).*')})
    result = ""
    episode_title = soup.find('h2', class_='page_title').text
    result += f"\n{episode_title}\n"
    for url in links:
        t = url['data-video']
        if re.search(r'awish', t):
            result += f"Awish : <a href='{t}'>Watch Online</a> \n"
        elif re.search(r'dood', t):
            r = t.replace("/e/", "/d/")
            result += f"DooD : <a href='{t}'>Watch Online</a> \nDownload Link: <a href='{r}'> Click Here</a>\n"
        elif re.search(r'alions', t):
            result += f"Alions : <a href='{t}'>Watch Online</a>\n\n"
        await editMessage(reply, result)
        if len(result) > 4000:
            sent = await sendMessage(reply, result)

bot.add_handler(MessageHandler(query, filters=command(BotCommands.QueryCommand) & CustomFilters.sudo))
