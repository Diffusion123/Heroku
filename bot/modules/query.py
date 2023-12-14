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

def last_episode(url):
    soup = soup_res(url)
    return soup.find('a', class_='active')['ep_end']

def generate_episode_urls(base_url, format, num_episodes):
    episode_urls = []
    for episode in range(1, num_episodes + 1):
        episode_url = f"{format}{episode}"
        episode_urls.append(episode_url)
    return episode_urls

def get_links(episode_url):
    soup = soup_res(episode_url)
    links = soup.find_all('a', {'data-video': re.compile(r'https://dood.*\/.*')})
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()
        text_part = title_text.replace("Watch ", "").replace(" at Gogoanime", "")
    else:
        text_part = "Title not available"
    for c in links:
        url_link = c['data-video']
        r = url_link.replace("/e/", "/d/")
        return f"{text_part}\nWatch Online:- <a href='{url_link}'>1080P Dood-HD</a>  <a href='{r}'>Download Link</a>\n\n"
     
def soup_res(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

async def gogoanimes(link, reply):
    new_url = link.split("/")[4]
    m_url = link.split("/")[2]
    each_url = f"https://{m_url}/{new_url}-episode-"
    num_episodes = int(last_episode(link))
    episode_urls = generate_episode_urls(link, each_url, num_episodes)
    t = ""
    for episode_url in episode_urls:
        t += get_links(episode_url)
        await editMessage(reply, t)
        if len(t) > 4000:
            sent = await sendMessage(reply, t)
            t = ""
            
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
        unique_links.add(anime_link)  # Add each unique link to the set

    for sorted in unique_links:
        await gogoanimes(sorted, reply)
        
bot.add_handler(MessageHandler(query_search, filters=command(BotCommands.QueryCommand) & CustomFilters.sudo))
