#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2024
#            ✈ https://t.me/kamekuro

# 🔒 Licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0
# + attribution
# + non-commercial
# + no-derivatives

# You CANNOT edit, distribute or redistribute and use for any purpose this file without direct permission from the author.
# All source code is provided for review only.

import apscheduler.schedulers.asyncio
from aiocache import Cache
from aiocache.serializers import JsonSerializer

import pyrogram
import pyrogram_patch

import version
import utils

client = pyrogram.Client(
    name="ns-bot",
    api_id=utils.config['app']['id'],
    api_hash=utils.config['app']['hash'],
    app_version=f"🎒 NetSchool Bot v{'.'.join(list(map(str, list(version.__version__))))}",
    bot_token=utils.config['token'],
    parse_mode=pyrogram.enums.ParseMode.HTML
)
patch = pyrogram_patch.patch(client)

scheduler = apscheduler.schedulers.asyncio.AsyncIOScheduler()
cache = Cache(Cache.MEMORY, serializer=JsonSerializer())