#!/usr/bin/env python3
import requests
import aiohttp
import json
import asyncio
from subprocess import run as srun, check_output
try:
    import heroku3
except ModuleNotFoundError:
    srun("pip install heroku3", capture_output=True, shell=True)
import heroku3
from re import search as re_search
from shlex import split as ssplit
from aiofiles import open as aiopen
from aiofiles.os import remove as aioremove, path as aiopath, mkdir
from os import path as ospath, getcwd

from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import bot, config_dict, DATABASE_URL
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage

api_key = config_dict["HEROKU_API_KEY"]
app_name = config_dict["HEROKU_APP_NAME"]

def dynos(api_key, app_name):
    # Form the URL for restarting dynos
    url = f'https://api.heroku.com/apps/{app_name}/dynos'

    # Headers with authorization and content type
    headers = {
        'Accept': 'application/vnd.heroku+json; version=3',
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    # Get a list of dynos
    response = requests.get(url, headers=headers)

    # Restart each dyno
    for dyno in response.json():
        dyno_id = dyno.get('id')
        restart_url = f'https://api.heroku.com/apps/{app_name}/dynos/{dyno_id}'
        requests.delete(restart_url, headers=headers)
        sendmessage("Dynos Restarted")
        
bot.add_handler(MessageHandler(dynos, filters=command(BotCommands.DynosCommand) & CustomFilters.sudo))
