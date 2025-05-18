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

import datetime
import logging
import io
import httpx

import pyrogram
from pyrogram import types

import netschoolapi as nsapi

import loader
import utils
from dispatch import filters
from dispatch.routing import Router


start = Router("start")
logger = logging.getLogger(__name__)


@start.on_message(pyrogram.filters.all)
async def all_messages(client: pyrogram.Client, message: types.Message):
    raise pyrogram.ContinuePropagation()


@start.on_message(
    filters.command(commands=["cancel", "отмена"])
    | filters.text("❌ Отмена")
)
async def cancelcmd(client: pyrogram.Client, message: types.Message):
    if await loader.cache.get(str(message.from_user.id)):
        await loader.cache.delete(str(message.from_user.id))
    await utils.answer(
        message,
        f"❌ <b>Команда отменена.</b>",
        reply_markup=types.ReplyKeyboardRemove()
    )


@start.on_start()
async def startcmd(client: pyrogram.Client, message: types.Message):
    utils.init_db()
    user = utils.db.getUser(message.from_user.id)

    return await utils.answer(
        message=message,
        response=f"🎒 <b>Привет!</b>\n" \
                 f"Я — бот для работы с «Сетевым Городом». " \
                 f"Для работы со мной используйте клавиатуру ниже.\n\n" \
                 f"❤️‍🩹 <b>Помощь с ботом: <a href=\"https://teletype.in/@kamekuro/nsbot-guide\">Гайд</a></b>\n\n" \
                 f"📜 <b>Используя этого бота, Вы автоматически соглашаетесь с " \
                    f"<a href=\"https://teletype.in/@kamekuro/nsbot-eula\">Пользовательским " \
                    f"соглашением</a>.</b>\n" \
                 f"❗ <b>Бот не является собственностью ИрТех.</b>\n" \
                 f"⚙ <b>Исходный код:</b> https://github.com/kamekuro/netschoolbot\n" \
                 f"💻 <b>Developed by @kamekuro with 🫶</b>",
        disable_web_page_preview=True,
        reply_markup=utils.getMenuKB(user[0]) if message.chat.type == pyrogram.enums.chat_type.ChatType.PRIVATE else None
    )


@start.on_message(
    filters.command(commands=["start"])
    & filters.deeplink_startswith(deeplinks=["auth"])
)
async def auth_start(client: pyrogram.Client, message: types.Message):
    from .auth import auth_cmd
    await auth_cmd(client, message)

@start.on_message(
    filters.command(commands=["start"])
    & filters.deeplink_startswith(deeplinks=["deauth"])
)
async def auth_start(client: pyrogram.Client, message: types.Message):
    from .auth import deauth
    await deauth(client, message)



# Redirect from inline diary

@start.on_message(
    filters.command(commands=["start"])
    & filters.deeplink_startswith(deeplinks=["dfi_"])
)
async def auth_start(client: pyrogram.Client, message: types.Message):
    args = utils.get_raw_args(message)
    day = datetime.datetime.strptime(args.split("_")[1], "%dT%mT%Y")
    message.text = day.strftime("%d.%m.%Y")

    from .diary import get_diary_custom_date
    await get_diary_custom_date(client, message)