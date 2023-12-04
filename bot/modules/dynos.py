#!/usr/bin/env python3
import requests
import urllib.parse
import json
import base64

from time import time
from uuid import uuid4
from asyncio import sleep
from subprocess import run as srun
from re import search as re_search
from urllib.parse import unquote
try:
    import heroku3
except ModuleNotFoundError:
    srun("pip install heroku3", capture_output=True, shell=True)

from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import bot, config_dict, DATABASE_URL
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage

async def restart_dynos(_, message):
    reply = await sendMessage(message, "Restarting Dynos...")
    api_key = config_dict["HEROKU_API_KEY"]
    app_name = config_dict["HEROKU_APP_NAME"]

    # Form the URL for restarting dynos
    url = f'https://api.heroku.com/apps/{app_name}/dynos'

    # Headers with authorization and content type
    headers = {
        'Accept': 'application/vnd.heroku+json; version=3',
        'Authorization': f'Bearer {api_key}'
    }

    # Get a list of dynos
    response = requests.get(url, headers=headers)

    # Restart each dyno
    for dyno in response.json():
        dyno_id = dyno['id']
        restart_url = f'https://api.heroku.com/apps/{app_name}/dynos/{dyno_id}'
        requests.delete(restart_url, headers=headers)
    await editMessage(reply, "Dynos Restarted!")

async def func(link, payload, auth_header):
    headers = {"Authorization": auth_header, "Referer": link}
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

async def index(_, message):  # Added 'message' parameter
    args = message.text.split()
    link = args[1] if len(args) > 1 else ''
    reply = await sendMessage(message, "Extracting Index...")    
    link = f"{link}/" if link[-1] != '/' else link
    auth_header = f"Basic {base64.b64encode('username:password'.encode()).decode().strip()}"
    payload = {"page_token": "", "page_index": 0}  # Assuming next_page_token is not needed here
    decrypted_response = await func(link, payload, auth_header)  # Corrected function call
    if "data" in decrypted_response and "files" in decrypted_response["data"]:
        size = [get_readable_file_size(file["size"]) for file in decrypted_response["data"]["files"] if file["mimeType"] != "application/vnd.google-apps.folder"]
        result = '\n'.join([f"\nName: {urllib.parse.unquote(file['name'])}  [{s}]\n <a href='https://drive.google.com/file/d/{urllib.parse.quote(file['id'])}'>Gdrive link</a>   <a href='{link}{urllib.parse.quote(file['name'])}'>Index link</a>" for file, s in zip(decrypted_response["data"]["files"], size) if file["mimeType"] != "application/vnd.google-apps.folder"])
        await editMessage(reply, result)

bot.add_handler(MessageHandler(restart_dynos, filters=command(BotCommands.DynosCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(index, filters=command(BotCommands.IndexCommand) & CustomFilters.sudo))
