#!/usr/bin/env python3
import requests
from time import time
from uuid import uuid4
from asyncio import sleep
from subprocess import run as srun

try:
    import heroku3
except ModuleNotFoundError:
    srun("pip install heroku3", capture_output=True, shell=True)

import heroku3
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import bot, config_dict, DATABASE_URL
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage

asymc def restart_dynos(_, message):
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
    await editMessage(reply, "Dynos Restarted!",)
        
bot.add_handler(MessageHandler(restart_dynos, filters=command(BotCommands.DynosCommand) & CustomFilters.sudo))
