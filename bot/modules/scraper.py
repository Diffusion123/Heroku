import base64
import json
import urllib.parse
import requests
from asyncio import sleep
import re 
from urllib.parse import unquote, urlparse
from bs4 import BeautifulSoup
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage, deleteMessage
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

async def bypass(_, message):
    args = message.text.split()
    link = args[1] if len(args) > 1 else ''
    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: Invalid URL")
    if "kayoanime.com" in link:
        await kayoanime(link, message)
    elif "linkbuzz.click" in link:
        await linkbuzz(link, message)
    elif "www9.gogoanimes.fi" in link:
        await gogoanimes(link, message)
    else:
        return

def get_redirected_url(url):
    response = requests.head(url, allow_redirects=True)
    return response.url

def soup_res(link):
    response = requests.get(link)
    return BeautifulSoup(response.text, 'html.parser')

async def kayoanime(link, message):
    reply = await sendMessage(message, "Getting Links........")
    soup = soup_res(link)
    links = soup.find_all('a', href=re.compile(r'https://drive.google.com/.*'))
    result = ""
    for l in links:
        url_link = l['href']
        title = l.get_text()  # This gets the text within the <a> tag
        result += f"{title}  ---  <a href='{url_link}'>Gdrive link</a>\n\n"
    await editMessage(reply, result)
   
async def linkbuzz(link, message):
    reply = await sendMessage(message, "Requesting linkbuzz.click for links")
    soup = soup_res(link)
    links = soup.find_all('a',  href=re.compile(r'https:(.*gdtot.*|.*filepress.*|.*gdflix).*/\.*'))
    result = ""
    for c in links:
        url_link = c['href']
        title = c.get_text()
        if re.match(r'https:(.*gdtot.*|.*filepress.*|.*gdflix).*/\.*', url_link):
            new_url = get_redirected_url(url_link)
            result += f"\n\n{title} ---- <a href='{new_url}'>Download Link</a>\n\n"
            await sendMessage(reply, result)
            await deleteMessage(reply)

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
    for c in links:
        url_link = c['data-video']
        return f"{title_text}\n1080P - {url_link}\n\n"
        
async def gogoanimes(link, message):
    reply = sendMessage(message, "Getting Links from Gogoanimes")
    new_url = link.split("/")[4]
    m_url = link.split("/")[2]
    each_url = f"https://{m_url}/{new_url}-episode-"
    num_episodes = int(last_episode(link))
    episode_urls = generate_episode_urls(link, each_url, num_episodes)
    result = ""
    for episode_url in episode_urls:
        result += get_links(episode_url)
        await sendMessage(reply, result)
        await deleteMessage(reply)
        
def func(link, payload, auth_header):
    headers = {
        "Authorization": auth_header,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; M2006C3LI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36",
        "Referer": link
    }
    encrypted_response = requests.post(link, data=payload, headers=headers)  # Corrected variable name
    decoded_data = base64.b64decode(encrypted_response.text[::-1][24:-20]).decode("utf-8")
    return json.loads(decoded_data)

def get_readable_file_size(file_size):
    file_size = int(file_size)
    if file_size < 1024:
        return f"{file_size} Bytes"
    elif 1024 <= file_size < 1024**2:
        return f"{file_size / 1024:.2f} KB"
    elif 1024**2 <= file_size < 1024**3:
        return f"{file_size / (1024**2):.2f} MB"
    elif 1024**3 <= file_size < 1024**4:
        return f"{file_size / (1024**3):.2f} GB"

async def scraper(_, message):  # Added 'message' parameter
    args = message.text.split()
    link = args[1] if len(args) > 1 else ''
    reply = await sendMessage(message, "Extracting Index...")    
    link = f"{link}/" if link[-1] != '/' else link
    auth_header = f"Basic {base64.b64encode('username:password'.encode()).decode().strip()}"
    payload = {"page_token": "", "page_index": 0}  # Assuming next_page_token is not needed here
    decrypted_response = func(link, payload, auth_header)  # Corrected function call
    if "data" in decrypted_response and "files" in decrypted_response["data"]:
        size = [get_readable_file_size(file["size"]) for file in decrypted_response["data"]["files"] if file["mimeType"] != "application/vnd.google-apps.folder"]
        result = '\n'.join([f"\nName: {urllib.parse.unquote(file['name'])}  [{s}]\n <a href='https://drive.google.com/file/d/{urllib.parse.quote(file['id'])}'>Gdrive link</a>   <a href='{link}{urllib.parse.quote(file['name'])}'>Index link</a>" for file, s in zip(decrypted_response["data"]["files"], size) if file["mimeType"] != "application/vnd.google-apps.folder"])
        await sendMessage(reply, result)
        await deleteMessage(reply)


bot.add_handler(MessageHandler(scraper, filters=command(BotCommands.ScraperCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(bypass, filters=command(BotCommands.ByPassCommand) & CustomFilters.sudo))
