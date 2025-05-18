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
import contextlib
import html
import logging
import os
import sys
from meval import meval

import pyrogram
from pyrogram import types
import pyrogram.errors

import loader
import utils
from dispatch import filters
from dispatch.routing import Router
from dispatch.logger import CustomException



admin = Router(name="admin")
logger = logging.getLogger(__name__)
locs = locals()

async def getattrs(client, message):
    e = locs
    e["client"] = client
    e["c"] = client
    e["message"] = message
    e["m"] = message
    e["reply"] = message.reply_to_message
    e["r"] = message.reply_to_message
    return {**e}



@admin.on_message(
    filters.command(commands=["eval", "e", "евал", "е"], prefixes=["!", "/", "~"])
    & filters.status(2)
)
async def eval(client: pyrogram.Client, message: types.Message):
    args = utils.get_raw_args(message)
    out = f"💻 <b>Код:</b>\n<pre language=\"python\">{html.escape(args)}</pre>\n\n"

    try:
        result = await meval(
            args,
            globals(),
            **await getattrs(client, message)
        )
    except Exception:
        exc = CustomException.from_exc_info(*sys.exc_info())
        full_err = '\n'.join(exc.full_stack.splitlines()[:-1])
        return await utils.answer(
            message,
            out + f"❌ <b>Ошибка</b>:\n<blockquote expandable>{str(full_err)}\n\n" \
                  f"🚫 {str(exc.full_stack.splitlines()[-1])}</blockquote>"
        )

    if callable(getattr(result, "stringify", None)):
        with contextlib.suppress(Exception):
            result = str(result.stringify())
    else:
        result = str(result)

    with contextlib.suppress(pyrogram.errors.exceptions.bad_request_400.MessageIdInvalid):
        msg = await utils.answer(
            message,
            out + f"✅ <b>Результат:</b>\n<pre language=\"python\">{utils.censor(result)}</pre>"
        )
        if not result:
            await asyncio.sleep(3)
            await msg[0].delete()



@admin.on_message(
    filters.command(commands=["terminal", "t", "терминал"], prefixes=["!", "/", "~"])
    & filters.status(2)
)
async def terminal(client: pyrogram.Client, message: types.Message):
    args = utils.get_raw_args(message)

    out, err = await (await asyncio.create_subprocess_shell(
        args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=os.path.abspath(os.path.dirname(os.path.abspath("main.py")))
    )).communicate()

    out_msg = f"⌨️ <b>Системная команда:</b>\n<pre language=\"shell\">{args}</pre>\n📼 <b>Вывод:</b>\n<pre language=\"shell\">{out.decode()}</pre>"
    if err.decode() != "":
        out_msg += f"\n\n❌ <b>Ошибки:</b>\n<pre language=\"shell\">{err.decode()}</pre>"

    await utils.answer(
        message,
        out_msg
    )



@admin.on_message(
    filters.command(commands=["status", "статус"], prefixes=["!", "/", "~"])
    & filters.status(2)
)
async def ch_status(client: pyrogram.Client, message: types.Message):
    args = utils.get_args(message)
    from_user = utils.db.regUser(message.from_user.id)
    uid = await utils.getID(message)
    status = None
    if uid < 1:
        return await utils.answer(
            message, "🤔 <b>Ты не указал пользователя.</b>"
        )
    user = utils.db.getUser(uid)
    if not user:
        user = utils.db.regUser(uid)

    if message.reply_to_message:
        if len(args) > 0 and (str(args[0])[1:] if str(args[0]).startswith("-") else str(args[0])).isdigit():
            status = int(args[0])
    else:
        if len(args) > 1 and (str(args[1])[1:] if str(args[1]).startswith("-") else str(args[1])).isdigit():
            status = int(args[1])

    if status is None:
        return await utils.answer(
            message,
            f"📂 <b>Текущий статус пользователя [<code>{user[0]}</code>]: [{utils.config['statuses'].get(f'{user[1]}')}]</b>"
        )
    if (status == 5) or (user[0] == message.from_user.id) or (user[1] >= from_user[1]):
        return await utils.answer(
            message,
            "⚠️ <b>Не.</b>"
        )

    old_status_str = utils.config['statuses'].get(f"{user[1]}")
    new_status_str = utils.config['statuses'].get(f"{status}")

    utils.db.save(f"UPDATE users SET status = {int(status)} WHERE id = {user[0]}")
    await utils.answer(
        message,
        f"📂✏ <b>Статус пользователя [<code>{user[0]}</code>] изменён:</b> [{old_status_str}] -> [{new_status_str}]"
    )

    name = message.from_user.first_name
    if message.from_user.last_name:
        name += f" {message.from_user.last_name}"
    name += f" [<code>{message.from_user.id}</code>]"
    await utils.answer(
        message,
        f"📂✏ <b>{name} изменил статус пользователя [<code>{user[0]}</code>]:</b> [" \
        f"{old_status_str}] -> [{new_status_str}]",
        False,
        utils.config['admin_chat'] if utils.config['admin_chat'] else utils.config['dev_id']
    )