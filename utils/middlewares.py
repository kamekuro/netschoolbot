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

import logging

import pyrogram
import pyrogram_patch
from pyrogram import types
from pyrogram_patch.middlewares.middleware_types import OnUpdateMiddleware, OnRawUpdateMiddleware, OnMessageMiddleware
from pyrogram_patch.middlewares import PatchHelper

import utils

logger = logging.getLogger(__name__)


class RegUser(OnMessageMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__()

    async def __call__(self, message: types.Message, client: pyrogram.Client, patch_helper: PatchHelper):
        uid = message.from_user.id
        aus = utils.db.getAllUsers()
        user = utils.db.getUser(uid)

        if not user:
            user = utils.db.regUser(uid)
            link = f"tg://user?id={message.from_user.id}"
            if message.from_user.username:
                link = f"https://t.me/{message.from_user.username}"
            await utils.answer(
                message,
                f"❤️ <b>Зарегистрировался новый <a href=\"{link}\">пользователь</a> [<code>{message.from_user.id}</code>]</b>",
                reply=False, chat_id=utils.config['debug_chat'],
                disable_web_page_preview=True
            )

        if user[1] < 0:
            return await patch_helper.skip_handler()

        return


class NoChats(OnMessageMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__()

    async def __call__(self, message: types.Message, client: pyrogram.Client, patch_helper: PatchHelper):
        if message.chat.id == utils.config['debug_chat']:
            return

        if message.chat.type in [pyrogram.enums.ChatType.GROUP, pyrogram.enums.ChatType.SUPERGROUP]:
            await utils.answer(
                message,
                "☹️ <b>Не знаю, для чего и зачем меня сюда добавили, но я не работаю в чатах..</b>",
                False
            )
            await client.leave_chat(message.chat.id)
        elif message.chat.type in [pyrogram.enums.ChatType.CHANNEL]:
            await client.leave_chat(message.chat.id)

        return (await patch_helper.skip_handler()) if message.chat.type in [
            pyrogram.enums.ChatType.GROUP,
            pyrogram.enums.ChatType.SUPERGROUP,
            pyrogram.enums.ChatType.CHANNEL
        ] else None
