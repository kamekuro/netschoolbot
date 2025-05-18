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
import time

import pyrogram
from pyrogram import types

import utils
from dispatch import filters
from dispatch.routing import Router


other = Router("iother")
logger = logging.getLogger(__name__)



# Inline ping

@other.on_inline_query(
    filters.text(["ping", "пинг"])
)
async def inline_ping(client: pyrogram.Client, query: types.InlineQuery):
    s = datetime.datetime.now()

    sapi = datetime.datetime.now()
    await client.get_me()
    eapi = round((datetime.datetime.now()-sapi).microseconds/1000, 2)

    kb = [
        [pyrogram.types.InlineKeyboardButton(text="Повторить", callback_data="ping")]
    ]
    kb = pyrogram.types.InlineKeyboardMarkup(kb)

    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                title=f"🚀 Понг!",
                input_message_content=types.InputTextMessageContent(
                    f"⚙ <b>Понг!</b>\n" \
                    f"<b>Handler took: {round((datetime.datetime.now()-s).microseconds/1000, 2)}ms | " \
                    f"API: {eapi}ms</b>\n" \
                    f"🚀 <b>Прошло с момента перезагрузки:</b> {str(datetime.timedelta(seconds=round(time.perf_counter() - utils.init_ts)))}"
                ),
                description="",
                reply_markup=types.InlineKeyboardMarkup([[
                    types.InlineKeyboardButton(
                        text="Повторить", callback_data="iping"
                    )
                ]])
            )
        ],
        cache_time=0
    )


@other.on_callback_query(
    filters.startswith("iping")
)
async def ping_cb(client: pyrogram.Client, query: types.CallbackQuery):
    s = datetime.datetime.now()
    await utils.edit(
        query, "⚡"
    )

    sapi = datetime.datetime.now()
    await client.get_me()
    eapi = round((datetime.datetime.now()-sapi).microseconds/1000, 2)

    await utils.edit(
        query,
        f"⚙ <b>Понг!</b>\n<b>Handler took: {round((datetime.datetime.now()-s).microseconds/1000, 2)}ms" \
        f" | API: {eapi}ms</b>\n" \
        f"🚀 <b>Прошло с момента перезагрузки:</b> {str(datetime.timedelta(seconds=round(time.perf_counter() - utils.init_ts)))}",
        reply_markup=pyrogram.types.InlineKeyboardMarkup([[
            pyrogram.types.InlineKeyboardButton(text="Повторить", callback_data="iping")
        ]])
    )


# Inline menu

@other.on_inline_query()
async def get_inline_menu(client: pyrogram.Client, query: types.InlineQuery):
    user = utils.db.getUser(query.from_user.id)

    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                title=f"🎛 Главное меню",
                input_message_content=types.InputTextMessageContent("🎛 <b>Добро пожаловать в главное меню!</b>"),
                description="",
                reply_markup=types.InlineKeyboardMarkup([
                    [
                        types.InlineKeyboardButton(
                            text="📕 Дневник", callback_data=f"idiary:{query.from_user.id}"
                        ),
                        types.InlineKeyboardButton(
                            text="💮 Оценки", callback_data=f"imarks:{query.from_user.id}"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="🚪 Выйти из аккаунта",
                            url=f"https://t.me/{client.me.username}?start=deauth"
                        )
                    ]
                ]) if utils.db.getNSUser(query.from_user.id) else types.InlineKeyboardMarkup([[
                    types.InlineKeyboardButton(
                        text="❤ Войти в аккаунт",
                        url=f"https://t.me/{client.me.username}?start=auth"
                    )
                ]])
            )
        ],
        cache_time=0
    )


@other.on_callback_query(
    filters.startswith("open_imenu:")
)
async def open_menu_cb(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[1]):
        return await query.answer(
            "⚠ Эта кнопка не для тебя!", True, cache_time=0
        )

    user = utils.db.getUser(query.from_user.id)
    await utils.edit(
        query,
        f"🎛 <b>Добро пожаловать в главное меню!</b>",
        reply_markup=types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton(text="📕 Дневник", callback_data=f"idiary:{query.from_user.id}"),
                types.InlineKeyboardButton(text="💮 Оценки", callback_data=f"imarks:{query.from_user.id}")
            ],
            [types.InlineKeyboardButton(
                text="🚪 Выйти из аккаунта",
                url=f"https://t.me/{client.me.username}?start=deauth"
            )]
        ]) if utils.db.getNSUser(query.from_user.id) else types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton(
                text="❤ Войти в аккаунт",
                url=f"https://t.me/{client.me.username}?start=auth"
            )
        ]])
    )