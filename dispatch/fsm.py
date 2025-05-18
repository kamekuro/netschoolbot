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

import re
import json
import typing
import logging
import traceback

import pyrogram
from pyrogram import filters, types, enums

import utils
from loader import cache


logger = logging.getLogger(__name__)


def StateFilter(state: str):
    async def func(flt, client: pyrogram.Client, update: typing.Union[types.Message, types.CallbackQuery]):
        conv: dict = await cache.get(str(update.from_user.id), {})
        if conv.get("name") != state:
            return False
        if conv.get("bot_id") != client.me.id:
            return False

        update.state_data = conv.get("data", {})
        if isinstance(update, types.Message):
            try: media_group = await client.get_media_group(update.chat.id, update.id)
            except: media_group = []
            if media_group:
                if update.id != media_group[0].id:
                    return False

        chat_id = conv.get("chat_id")
        if chat_id:
            if isinstance(update, types.Message):
                if chat_id != update.chat.id:
                    return False
            elif isinstance(update, types.CallbackQuery):
                if chat_id != update.message.chat.id:
                    return False

        await cache.delete(str(update.from_user.id))
        return True

    return filters.create(
        func,
        "StateFilter",
        state=state
    )


async def set_state(client: pyrogram.Client, name: str, user_id: int, chat_id: int = 0, data: dict = {}):
    conv = await cache.get(str(user_id), {})
    conv['name'] = name
    conv['bot_id'] = client.me.id
    conv['chat_id'] = chat_id if chat_id != 0 else None
    conv['data'] = data
    await cache.set(str(user_id), conv)