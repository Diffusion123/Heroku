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
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

async def bypass(_, message):
    args = message.text.split()
    link = args[1] if len(args) > 1 else ''
    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: Invalid URL")
    if "kayoanime.com" in link:
        await kayoanime(link, message)
    elif "cinevood.mom" in link:
        await cinevood(link, message)
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
    
async def cinevood(link, message):
    reply = await sendMessage(message, "Processing To get Latest Links")    
    soup = soup_res(link)
    links = soup.find_all('a', href=re.compile(r'https://.*\/file/*'))
    result_list = []

    for link in links:
        url_link = link['href']
        span_tag = link.find_previous('span')
        span_text = span_tag.text.strip()

        if re.match(r'https://(.*gdtot|.*filepress|.*gdflix).*\/*', url_link):
            new_url = get_redirected_url(url_link)
            result_list.append(f"{span_text}\n\n URL: {new_url}\n\n")
        elif re.match(r'https://linkbuzz.*\/', url_link):
            soup_link = soup_res(url_link)
            links1 = soup_link.find_all('a', href=re.compile(r'https://(.*gdtot|.*filepress|.*gdflix|zipylink|sharegdrive|dropgalaxy).*\/*'))

            for link1 in links1:
                url_link1 = link1['href']
                span_tag1 = link1.find_previous('span')
                span_text1 = span_tag1.text.strip()

                if re.match(r'https://(.*gdtot|.*filepress|.*gdflix).*\/*', url_link1):
                    new_url1 = get_redirected_url(url_link1)
                    result_list.append(f"{span_text}\n\n{span_text1} -- {new_url1}\n\n")
                else:
                    result_list.append(f"{span_text1} -- {url_link1}\n\n")
        else:
            result_list.append(f"{span_text}\nURL: {url_link}\n")

    final_result = "".join(result_list)
    await editMessage(reply, final_result)


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
        await editMessage(reply, result)

bot.add_handler(MessageHandler(scraper, filters=command(BotCommands.ScraperCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(bypass, filters=command(BotCommands.ByPassCommand) & CustomFilters.sudo))
