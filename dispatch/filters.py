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


logger = logging.getLogger(__name__)


AnyText = typing.Union[typing.Tuple[str, ...], typing.List[str], str] 

def AnyTextToList(t: "AnyText") -> typing.Union[typing.Tuple[str, ...], typing.List[str]]: 
    return (t,) if isinstance(t, str) else t


def private():
    async def func(
        flt, _,
        update: typing.Union[types.Message, types.CallbackQuery]
    ):
        chat = update.chat if isinstance(update, types.Message) else update.message.chat
        return bool(
            chat.type == pyrogram.enums.ChatType.PRIVATE
        )

    return filters.create(
        func,
        "PrivateFilter"
    )


def deeplink(deeplinks: AnyText):
    deeplinks: typing.Tuple[str] = [x.lower() for x in AnyTextToList(deeplinks)]

    async def func(
        flt, _,
        message: types.Message
    ):
        if not isinstance(message, types.Message):
            raise ValueError(f"TextFilter doesn't work with {type(message)}")

        deeplink = utils.get_raw_args(message)
        message.pattern = deeplink
        message.deeplink = deeplink
        return (deeplink in deeplinks)

    return filters.create(
        func,
        "StartDeeplinksFilter"
    )


def deeplink_startswith(deeplinks: AnyText):
    deeplinks: typing.Tuple[str] = [x.lower() for x in AnyTextToList(deeplinks)]

    async def func(
        flt, _,
        message: types.Message
    ):
        if not isinstance(message, types.Message):
            raise ValueError(f"TextFilter doesn't work with {type(message)}")

        deeplink = utils.get_raw_args(message)
        for x in deeplinks:
            if deeplink.startswith(x):
                message.pattern = x
                message.deeplink = deeplink
                return deeplink.startswith(x)
        return False

    return filters.create(
        func,
        "StartDeeplinksFilter"
    )


def text(pattern: AnyText, ignore_case: bool = True):
    pattern: typing.Tuple[str] = AnyTextToList(pattern)
    if ignore_case:
        pattern = [x.lower() for x in pattern]

    async def func(flt, _, update: types.Update):
        if isinstance(update, types.Message): 
            value = update.text or update.caption 
        elif isinstance(update, types.CallbackQuery): 
            value = update.data
        elif isinstance(update, types.InlineQuery):
            value = update.query 
        else:
            raise ValueError(f"TextFilter doesn't work with {type(update)}")

        if not value:
            return False

        if ignore_case:
            value = value.lower()
        return (value in pattern)
 
    return filters.create(
        func, "TextFilter",
        pattern=pattern,
        ignore_case=ignore_case
    )


def startswith(pattern: AnyText, ignore_case: bool = True):
    pattern: typing.Tuple[str] = AnyTextToList(pattern)
    if ignore_case:
        pattern = [x.lower() for x in pattern]

    async def func(flt, _, update: types.Update):
        if isinstance(update, types.Message):
            value = update.text or update.caption
        elif isinstance(update, types.CallbackQuery):
            value = update.data
        elif isinstance(update, types.InlineQuery):
            value = update.query
        else:
            raise ValueError(f"Regex filter doesn't work with {type(update)}")

        if not value:
            return False
 
        if ignore_case:
            value = value.lower()
        for x in pattern:
            if value.startswith(x):
                update.pattern = x
                return value.startswith(x)
        return False

    return filters.create(
        func, "StartswithFilter",
        pattern=pattern,
        ignore_case=ignore_case
    )


def status(status: int, can_use_in_chats: bool = True):
    async def func(flt, _, update: types.Update):
        if isinstance(update, types.Message):
            if not can_use_in_chats:
                if update.chat.type != pyrogram.enums.ChatType.PRIVATE:
                    return False
        uid = update.from_user.id
        user = utils.db.getUser(uid)
        if not user:
            user = utils.db.regUser(uid)

        out = f"👑 <b>Вам нужен {status} админ-статус для этого действия.</b>"

        if user[1] < status:
            if isinstance(update, types.Message):
                await utils.answer(update, out)
            elif isinstance(update, types.InlineQuery):
                pass
            else:
                await update.answer(utils.remove_html(out))
        return bool(user[1] >= status)

    return filters.create(
        func,
        "StatusFilter",
        status=status,
        can_use_in_chats=can_use_in_chats
    )


def command(
    commands: typing.Union[str, typing.List[str]],
    prefixes: typing.Union[str, typing.List[str]] = ["!", "/"],
    case_sensitive: bool = False
):
    command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

    async def func(flt, client: pyrogram.Client, message: types.Message):
        username = client.me.username or ""
        message.command = None
        text = (message.text or message.caption)
        try: media_gr = await client.get_media_group(message.chat.id, message.id)
        except: media_gr = [message]
        if message.id != media_gr[0].id:
            return False

        if not text:
            return False

        message.prefixes = list(flt.prefixes) if not isinstance(flt.prefixes, list) else flt.prefixes
        for prefix in flt.prefixes:
            if not text.startswith(prefix):
                continue
            without_prefix = text[len(prefix):]

            for cmd in flt.commands:
                if not re.match(rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)", without_prefix,
                                flags=re.IGNORECASE if not flt.case_sensitive else 0):
                    continue

                without_command = re.sub(rf"{cmd}(?:@?{username})?\s?", "", without_prefix, count=1,
                                         flags=re.IGNORECASE if not flt.case_sensitive else 0)

                message.command = [cmd] + [
                    re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                    for m in command_re.finditer(without_command)
                ]

                return True

        return False

    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}

    prefixes = [] if prefixes is None else prefixes
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {""}

    return filters.create(
        func,
        "CommandFilter",
        commands=commands,
        prefixes=prefixes,
        case_sensitive=case_sensitive
    )