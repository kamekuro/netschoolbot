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
import pytz

import pyrogram
import pyroboard
from pyrogram import types

import netschoolapi as nsapi

import dispatch.fsm
import utils
from dispatch import filters
from dispatch.routing import Router


mail = Router("mail")
logger = logging.getLogger(__name__)


@mail.on_message(
    filters.command(["mail", "почта"])
    | filters.text("✉️ Почта", False)
)
async def get_mail(client: pyrogram.Client, message: types.Message):
    user = utils.db.recvs("SELECT * FROM accounts WHERE id = ?", message.from_user.id)
    if not user:
        return await utils.answer(
            message,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )
    await utils.answer(
        message,
        f"✉️ <b>Выберите тип сообщений:</b>",
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(
                text="Входящие", callback_data=f"gmail:inbox"
            )],
            [types.InlineKeyboardButton(
                text="Отправленные", callback_data=f"gmail:sent"
            )]
        ])
    )


@mail.on_callback_query(
    filters.startswith("gmail:")
)
async def get_messages(client: pyrogram.Client, query: types.CallbackQuery):
    user = utils.db.recvs("SELECT * FROM accounts WHERE id = ?", query.from_user.id)
    if not user:
        return await utils.edit(
            query.message,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )
    mail_type = query.data.split(":")[1]
    page = 1
    if mail_type == "go_to_types":
        return await utils.edit(
            query.message,
            f"<b>Выберите тип сообщений</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="Входящие", callback_data=f"gmail:inbox"
                )],
                [types.InlineKeyboardButton(
                    text="Отправленные", callback_data=f"gmail:sent"
                )]
            ])
        )

    try:
        ns = await utils.db.getUserNS(query.from_user.id)
        mail_resp, pg = await ns.get_mail(mail_type), 1
        while len(mail_resp.rows) < mail_resp.total:
            pg += 1
            mr = await ns.get_mail(mail_type, pg)
            for x in mr.rows: mail_resp.rows.append(x)
        await ns.full_logout()
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(
            query.message, e
        )

    if not mail_resp.rows:
        return await utils.edit(
            query.message,
            "☹ <b>Нет сообщений указанного типа.</b>",
            reply_markup=types.InlineKeyboardMarkup([[
                types.InlineKeyboardButton(text="🔙 Назад", callback_data="gmail:go_to_types")
            ]])
        )

    msgs = utils.split_list(mail_resp.rows, 8)
    kb = pyroboard.InlineKeyboard(1)
    kb.add(*[
        types.InlineKeyboardButton(
            text=f"{i+1}. {x.message_subject}",
            callback_data=f"get_msg:{x.id}:{mail_type}:{page}"
        ) for i, x in enumerate(msgs[page-1])
    ])
    if len(msgs) > 1:
        kb.paginate(len(msgs), page, f"getmsgspage:{mail_type}:{{number}}")
    kb.row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="gmail:go_to_types"))

    out = f"🤔 <b>Выберите сообщение. Вот краткая информация " \
          f"(тема и {'автор' if mail_type == 'inbox' else 'получатель'}) о каждом сообщении в списке:</b>"
    for i, x in enumerate(msgs[page-1]):
        out += f"\n    <b>{i+1}. {x.author if x.author else x.to_names}</b>: " \
               f"<i>{x.message_subject}</i>"

    await utils.edit(
        query.message, out,
        reply_markup=kb
    )

@mail.on_callback_query(
    filters.startswith("getmsgspage:")
)
async def get_messages_by_page(client: pyrogram.Client, query: types.CallbackQuery):
    user = utils.db.recvs("SELECT * FROM accounts WHERE id = ?", query.from_user.id)
    if not user:
        return await utils.edit(
            query.message,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )
    mail_type = query.data.split(":")[1]
    page = int(query.data.split(":")[2])

    try:
        ns = await utils.db.getUserNS(query.from_user.id)
        mail_resp, pg = await ns.get_mail(mail_type), 1
        while len(mail_resp.rows) < mail_resp.total:
            pg += 1
            mr = await ns.get_mail(mail_type, pg)
            for x in mr.rows: mail_resp.rows.append(x)
        await ns.full_logout()
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(
            query.message, e
        )

    if not mail_resp.rows:
        return await utils.edit(
            query.message,
            "☹ <b>Нет сообщений указанного типа.</b>",
            reply_markup=types.InlineKeyboardMarkup([[
                types.InlineKeyboardButton(text="🔙 Назад", callback_data="gmail:go_to_types")
            ]])
        )

    msgs = utils.split_list(mail_resp.rows, 8)
    page = page if page <= len(msgs) else 1
    kb = pyroboard.InlineKeyboard(1)
    kb.add(*[
        types.InlineKeyboardButton(
            text=f"{8*(page-1)+i+1}. {x.message_subject}",
            callback_data=f"get_msg:{x.id}:{mail_type}:{page}"
        ) for i, x in enumerate(msgs[page-1])
    ])
    if len(msgs) > 1:
        kb.paginate(len(msgs), page, f"getmsgspage:{mail_type}:{{number}}")
    kb.row(types.InlineKeyboardButton(text="🔙 Назад", callback_data="gmail:go_to_types"))

    out = f"🤔 <b>Выберите сообщение. Вот краткая информация " \
          f"(тема и {'автор' if mail_type == 'inbox' else 'получатель'}) о каждом сообщении в списке:</b>"
    for i, x in enumerate(msgs[page-1]):
        out += f"\n    <b>{8*(page-1)+i+1}. {x.author if x.author else x.to_names}</b>: " \
               f"<i>{x.message_subject}</i>"

    await utils.edit(
        query.message, out,
        reply_markup=kb
    )


@mail.on_callback_query(
    filters.startswith("get_msg:")
)
async def get_message(client: pyrogram.Client, query: types.CallbackQuery):
    user = utils.db.recvs("SELECT * FROM accounts WHERE id = ?", query.from_user.id)
    if not user:
        return await utils.edit(
            query.message,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )
    msg_id = int(query.data.split(":")[1])
    mail_type = query.data.split(":")[2]
    page = int(query.data.split(":")[3])

    try:
        ns = await utils.db.getUserNS(query.from_user.id)
        msg_info = await ns.get_message(msg_id)
        await ns.full_logout()
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(
            query.message, e
        )

    if mail_type == "inbox": out = f"✉️ <b>Письмо от <i>{msg_info.author.name}</i></b>"
    else: out = f"✉️ <b>Письмо для <i>{msg_info.to_names}</i></b>"
    if msg_info.date:
        out += f"\n📅 <b>Дата отправки:</b> {msg_info.date.strftime('%d.%m.%Y %H:%M')}"
    if msg_info.message_subject:
        out += f"\n🔎 <b>Тема сообщения:</b> {msg_info.message_subject}"
    if msg_info.text:
        out += f"\n\n💬 <b>Текст сообщения:</b>\n<blockquote expandable>{msg_info.text}</blockquote>"

    kb = pyroboard.InlineKeyboard(1)
    kb.row(types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"getmsgspage:{mail_type}:{page}"))

    await utils.edit(
        query.message, out,
        reply_markup=kb
    )