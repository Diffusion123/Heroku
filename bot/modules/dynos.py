import aiohttp
import asyncio
import subprocess import run as srun, check_output
try: import heroku3
except ModuleNotFoundError: srun("pip install heroku3", capture_output=True, shell=True)
import heroku3

from bot import bot, LOGGER, config_dict
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, editMessage, editReplyMarkup, sendFile, deleteMessage, delete_all_messages
from .helper.telegram_helper.filters import CustomFilters

async def dynos(client, message):
    url = f'https://api.heroku.com/apps/{HEROKU_APP_NAME}/dynos'

    headers = {
        'Accept': 'application/vnd.heroku+json; version=3',
        'Authorization': f'Bearer {HEROKU_API_KEY}',
        'Content-Type': 'application/json',
    }
    
    details = await sendMessage(message, '<i>Fetching Heroku Credentials ...</i>')
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            dynos = await response.json()
            
            for dyno in dynos:
                dyno_id = dyno['id']
                restart_url = f'https://api.heroku.com/apps/{HEROKU_APP_NAME}/dynos/{dyno_id}'
                
                async with aiohttp.ClientSession(headers={'Authorization': f'Bearer {HEROKU_API_ID}'}) as session:
                    async with session.delete(restart_url) as response:
                        return await editMessage(details, "Dynos Restarted Successfully to 0 hours")
          
bot.add_handler(MessageHandler(dynos, filters=command(BotCommands.DynosCommand) & CustomFilters.authorized & ~CustomFilters.blacklisted))
