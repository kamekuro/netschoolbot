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

import asyncio
import datetime
import logging
import io
import httpx

import pyrogram
from pyrogram import types

import netschoolapi as nsapi

import utils
from dispatch import filters
from dispatch.routing import Router


announcements = Router("announcements")
logger = logging.getLogger(__name__)


@announcements.on_message(
    filters.command(["announcements", "объявления"])
    | filters.text("📢 Объявления", False)
)
async def get_announcements(client: pyrogram.Client, message: types.Message):
    msg = await utils.answer(message, "🕓 <b>Подождите…</b>")

    user = utils.db.getNSUser(message.from_user.id)
    if not user:
        return await utils.edit(
            msg,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )

    try:
        ns = await utils.db.getUserNS(message.from_user.id)
        announces = await ns.announcements()
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(msg, e)

    if len(announces) == 0:
        return await utils.edit(msg, f"✅ <b>Нет никаких объявлений</b>")

    await msg[0].delete()
    for announce_index, announce in enumerate(announces):
        out = f"📢 <b>Объявление ({announce_index+1}/{len(announces)}) от: <i>{announce.author.full_name}</i></b>"
        out += f"\n📅 <b>Дата:</b> {announce.post_date.strftime('%d.%m.%Y %H:%M')}"
        if announce.name:
            out += f"\n🔎 <b>Тема:</b> {announce.name}"
        if announce.content:
            out += f"\n\n💬 <b>Текст:</b>\n<blockquote expandable>{announce.content}</blockquote>"

        media = []
        messages = []
        if announce.attachments:
            for index, attachment in enumerate(announce.attachments):
                file = io.BytesIO()
                await ns.download_attachment(attachment.id, file)
                file.name = attachment.name
                m = types.InputMediaDocument(file, caption=out[:1024] if index+1 == len(announce.attachments) else "")
                media.append(m)
            for x in utils.split_list(media, 10): messages.append(x)
            if len(out) > 1024:
                for x in range(0, len(out), 1024):
                    if x == 0: continue
                    messages.append(out[x:x+1024])
        else:
            for x in range(0, len(out), 1024):
                messages.append(out[x:x+1024])

        logger.error(messages)
        ann_msg = None
        if messages:
            for item_index, item in enumerate(messages):
                reply = None if not ann_msg else ann_msg[-1]
                if type(item) == str:
                    ann_msg = await utils.answer(
                        message, item,
                        reply=True if reply else False,
                        reply_to=reply[0].id if reply else None
                    )
                else:
                    ann_msg = await utils.answer(
                        message,
                        "" if item_index != len(messages)-1 else out,
                        reply=True if reply else False,
                        reply_to=reply[0].id if reply else None,
                        media=item
                    )
        '''else:
            await utils.answer(
                message, out,
                reply=False,
                disable_web_page_preview=True
            )'''
        await asyncio.sleep(1)

    await ns.full_logout()