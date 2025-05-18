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
import git
import logging
import time

import pyrogram
from pyrogram import types

import utils
import version
from dispatch import filters
from dispatch.routing import Router
from loader import cache


other = Router("other")
logger = logging.getLogger(__name__)


@other.on_message(
    filters.command(commands=["privacy", "eula"])
)
async def get_privacy(client: pyrogram.Client, message: types.Message):
    await utils.answer(
        message,
        f"📜 <b>Пользовательское соглашение доступно по ссылке: https://teletype.in/@kamekuro/nsbot-eula</b>"
    )


@other.on_message(
    filters.command(commands=["botinfo", "ботинфо"])
)
async def stats(client: pyrogram.Client, message: types.Message):
    try:
        hash_ = git.Repo().head.commit.hexsha
        build = f"<a href='https://github.com/kamekuro/netschoolbot/commit/{hash_}'>#{hash_[:7]}</a>"
    except:
        build = ""
    await utils.answer(
        message,
        f"ℹ️ <b>Информация о боте:</b>\n\n" \
        f"💫 <b>Версия:</b> <code>{'.'.join(list(map(str, list(version.__version__))))}</code> {build if build else ''}" \
        f"\n🌳 <b>Ветка:</b> <code>{version.branch}</code>\n" \
        f"🚀 <b>Прошло с момента перезагрузки:</b> {str(datetime.timedelta(seconds=round(time.perf_counter() - utils.init_ts)))}\n" \
        f"👤 <b>Всего зарегистрировано пользователей:</b> <code>{utils.db.recvs('SELECT COUNT(*) FROM users')[0][0]}</code>"
    )


@other.on_message(
    filters.command(commands=["uid", "id", "айди", "ид"])
)
async def get_uid(client: pyrogram.Client, message: types.Message):
    uid = await utils.getID(message)
    out = f"🆔 <b>ID пользователя:</b> <code>{uid}</code>"
    if uid < 1:
        uid = message.from_user.id
        out = f"🆔 <b>Ваш ID:</b> <code>{uid}</code>"

    await utils.answer(
        message, out
    )


@other.on_message(
    filters.command(commands=["menu", "меню"])
    | filters.text("◀️ Главное меню", False)
)
async def get_menu(client: pyrogram.Client, message: types.Message):
    await utils.answer(
        message,
        f"🗂 <b>Вы находитесь в Главном меню.</b>\n" \
        f"Пожалуйста, выберите нужную функцию ниже 👇",
        reply_markup=utils.getMenuKB(message.from_user.id) if message.chat.type == pyrogram.enums.chat_type.ChatType.PRIVATE else None
    )

@other.on_callback_query(
    filters.startswith("mmenu:")
)
async def get_menu_cb(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[1]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True
        )
    if (len(query.data.split(":")) > 2) and (query.data.split(":")[2] != "ndl"):
        msg_ids = [int(x) for x in query.data.split(":")[2].split(",")]
        await client.delete_messages(
            chat_id=query.message.chat.id,
            message_ids=msg_ids if msg_ids else None
        )
    if await cache.get(f"diary_{query.from_user.id}"):
        msg_ids = (await cache.get(f"diary_{query.from_user.id}"))['msgs_to_del']
        try:
            await client.delete_messages(
                chat_id=query.message.chat.id,
                message_ids=msg_ids if msg_ids else None
            )
        except:
            pass
        await cache.delete(f"diary_{query.from_user.id}")

    await query.message.delete()
    await utils.answer(
        query.message,
        f"🗂 <b>Вы находитесь в Главном меню.</b>\n" \
        f"Пожалуйста, выберите нужную функцию ниже 👇",
        reply_markup=utils.getMenuKB(query.from_user.id) if query.message.chat.type == pyrogram.enums.chat_type.ChatType.PRIVATE else None
    )


@other.on_message(
    filters.command(commands=["clearkeyboard", "clearkbd", "убратькнопки", "убратьклаву"])
)
async def clearkbd(client: pyrogram.Client, message: types.Message):
    await utils.answer(
        message,
        f"⌨ <b>Клавиатура убрана.</b>",
        reply_markup=types.ReplyKeyboardRemove()
    )


@other.on_message(
    filters.command(commands=["ping", "пинг"])
)
async def ping(client: pyrogram.Client, message: types.Message):
    ev = (datetime.datetime.now() - message.date).microseconds / 1000
    s = datetime.datetime.now()
    msg = await utils.answer(
        message, "⚡"
    )

    sapi = datetime.datetime.now()
    await client.get_chat(message.chat.id)
    eapi = round((datetime.datetime.now()-sapi).microseconds/1000, 2)

    kb = [
        [pyrogram.types.InlineKeyboardButton(text="Повторить", callback_data="ping")]
    ]
    kb = pyrogram.types.InlineKeyboardMarkup(kb)

    await utils.edit(
        msg,
        f"⚙ <b>Понг!</b>\n<b>Event latency: {int(ev)}ms | Handler took: " \
        f"{round((datetime.datetime.now()-s).microseconds/1000, 2)}ms | API: {eapi}ms</b>\n" \
        f"🚀 <b>Прошло с момента перезагрузки:</b> {str(datetime.timedelta(seconds=round(time.perf_counter() - utils.init_ts)))}",
        reply_markup=kb
    )

@other.on_callback_query(
    filters.startswith("ping")
)
async def ping_cb(client: pyrogram.Client, query: types.CallbackQuery):
    s = datetime.datetime.now()
    msg = await utils.edit(
        query.message, "⚡"
    )
    ev = (datetime.datetime.now() - msg.date).microseconds / 1000

    sapi = datetime.datetime.now()
    await client.get_chat(msg.chat.id)
    eapi = round((datetime.datetime.now()-sapi).microseconds/1000, 2)

    kb = [
        [pyrogram.types.InlineKeyboardButton(text="Повторить", callback_data="ping")]
    ]
    kb = pyrogram.types.InlineKeyboardMarkup(kb)

    await utils.edit(
        msg,
        f"⚙ <b>Понг!</b>\n<b>Event latency: {int(ev)}ms | Handler took: " \
        f"{round((datetime.datetime.now()-s).microseconds/1000, 2)}ms | API: {eapi}ms</b>\n" \
        f"🚀 <b>Прошло с момента перезагрузки:</b> {str(datetime.timedelta(seconds=round(time.perf_counter() - utils.init_ts)))}",
        reply_markup=kb
    )
