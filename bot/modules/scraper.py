import base64
import json
import urllib.parse
import requests
from asyncio import sleep
from re import search as re_search
from urllib.parse import unquote, urlparse

from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

def scraper(_, message):
    args = message.text.split()
    link = args[1] if len(args) > 1 else ''
    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: Invalid URL")
    else:
        return index_link(link, message)

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

def index_link(link, message):  # Added 'message' parameter
    reply = sendMessage(message, "Extracting Index...")    
    link = f"{link}/" if link[-1] != '/' else link
    auth_header = f"Basic {base64.b64encode('username:password'.encode()).decode().strip()}"
    payload = {"page_token": "", "page_index": 0}  # Assuming next_page_token is not needed here
    decrypted_response = func(link, payload, auth_header)  # Corrected function call
    if "data" in decrypted_response and "files" in decrypted_response["data"]:
        size = [get_readable_file_size(file["size"]) for file in decrypted_response["data"]["files"] if file["mimeType"] != "application/vnd.google-apps.folder"]
        result = '\n'.join([f"\nName: {urllib.parse.unquote(file['name'])}  [{s}]\n <a href='https://drive.google.com/file/d/{urllib.parse.quote(file['id'])}'>Gdrive link</a>   <a href='{link}{urllib.parse.quote(file['name'])}'>Index link</a>" for file, s in zip(decrypted_response["data"]["files"], size) if file["mimeType"] != "application/vnd.google-apps.folder"])
        editMessage(reply, result)

bot.add_handler(MessageHandler(scraper, filters=command(BotCommands.ScraperCommand) & CustomFilters.sudo))
