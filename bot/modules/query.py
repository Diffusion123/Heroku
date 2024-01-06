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
    elif "-kdrama" in message.text:
        await kdrama_search(message)
    elif "-hsongs" in message.text:
        await pagalhindi(message)
    else:
        await sendMessage(message, "<i>Provide Kdrama / Anime Name </i>")
             
def soup_res(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

async def anidao_search(message):
    blacklisted_words = ["Renai Flops", "Uncensored", "Princess Lover!", "Futoku no Guild", "Ishuzoku Reviewers", "Kandagawa Jet Girls", "Oniichan wa Oshimai", "Dokyuu", "Hentai", "HxEros"]
    message_lower = message.text.lower().strip()
    blacklisted_words_lower = [word.lower().strip() for word in blacklisted_words]

    for word in blacklisted_words_lower:
        if word in message_lower:
            await sendMessage(message, "Are You Stupid?, Learn Discipline To Search Content")
            break
    else:
        s = quote(message.text.split(' ', 1)[1].rsplit(' ', 1)[0])
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
        await animedao_ep_files(final, message)

async def animedao_ep_files(link, message):
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

async def kdrama_search(message):
    s = quote(message.text.split(' ', 1)[1].rsplit(' ', 1)[0])
    domain = "https://kissasian.cz"
    search = f"https://kissasian.cz/search.html?keyword={s}"
    soup = soup_res(search)
    list_kdrama = soup.find_all('a', href=re.compile(r'.*info.*'))
    for kdrama in list_kdrama:
        selected_kdrama = f"{domain}{kdrama['href']}"
        await kissasian(selected_kdrama, message)

async def kissasian(url, message):
    reply = await sendMessage(message, "<code> Getting Links</code>")
    soup = soup_res(url)
    urls = []
    ep_title = []
    result = ""
    ep_links = soup.find_all('a', href=re.compile(r'.*episode.*'))
    for ep in ep_links:
        new = f"https://kissasian.cz{ep['href']}"
        ep_name = ep['title']
        ep_title.append(ep_name)
        urls.append(new)

    for epi, reversed_url in zip(reversed(ep_title), reversed(urls)):
        soup = soup_res(reversed_url)
        links = soup.find_all('option', value=re.compile(r'.*play.php.*'))
        for r in links:
            t = r['value'].replace("play.php", "download")
            result += f"<b><code>{epi}</code></b>\n <a href='https:{t}'> Click Here To Download </a>\n"
            await editMessage(reply, result)
            if len(result) > 4000:
                sent = await sendMessage(reply, result)
                result = ""

async def pagalhindi(message):
    reply = await sendMessage(message, "<code> Searching Song links</code>")
    s = message.text.split(' ', 1)[1].rsplit(' ', 1)[0]
    result = ""
    for i in range(1990, 2025):
        year = i
        final_part = s + " " + str(year)

        second_part = final_part.replace(" ", "-")
        first_part = "https://pagalfree.com/album/"
        search_url = first_part + second_part + ".html"
        soup = soup_res(search_url)
        if soup:
            result += f"Detected: {s} ({year})\n\n"
        links = soup.find_all('a', href=re.compile(r'.*music.*'))
        for link in links:
            l_result = link['href']
            song = soup_res(l_result)
            s_links = song.find_all('a', href=re.compile(r'.*download.*'))

            for s_link in s_links:
                s_result = s_link['href']
                new_link = quote(s_result).replace("%3A",":")
                t = s_result.replace("128-", "").replace("120-", "").replace("192-", "").replace("320-", "").split('/')
                result += f"Name: {t[4]}\n <a href='{new_link}'>Download Link</a>\n\n"
                await editMessage(reply, result)
                if len(result) > 4000:
                    sent = await sendMessage(reply, result)
                    result = ""

bot.add_handler(MessageHandler(query, filters=command(BotCommands.QueryCommand) & CustomFilters.sudo))
