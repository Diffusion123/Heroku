import re
import requests
from asyncio import sleep
from bs4 import BeautifulSoup

from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage, deleteMessage
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.telegram_helper.button_build import ButtonMaker

def soup_res(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error making request to {url}: {e}")
        return None

async def query_link(_, message):
    args = message.text.split()
    word = args[1] if len(args) > 1 else ''
    reply = await sendMessage(message, "Searching for the results")
    search_url = f"https://animedao.bz/search.html?keyword={word}"
    soup = soup_res(search_url)
    if soup:
        links = soup.find_all('a', href=re.compile(r'.*anime/.*'))
        for link in links:
            t = link['href']
            new_url = f"https://animedao.bz{t}"
            await animedao(new_url, reply)

async def animedao(link, reply):
    if re.search(r'.*episode.*', link):
        await animedao_files(link, reply)
    else:
        soup = soup_res(link)
        if soup:
            links = soup.find_all('a', {'class': "episode_well_link"}, href=re.compile(r'.*watch-online.*'))
            for sub in links:
                l_sub = sub['href']
                part = link.split('/')[2]
                mid = f"https://{part}"
                final = mid + l_sub
                await animedao_files(final, reply)

async def animedao_files(link, reply):
    soup = soup_res(link)
    if soup:
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
                result += f"Alions : <a href='{t}'>Watch Online</a>\n"
                
        if result:
            await editMessage(reply, result)
            if len(result) > 4000:
                sent = await sendMessage(reply, result)

bot.add_handler(MessageHandler(query_link, filters=command(BotCommands.QueryCommand) & CustomFilters.sudo))
