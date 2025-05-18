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
import functools
import io
import json
import re
import pytz
import time
import typing
from urllib.parse import urlparse

import pyrogram
import pyroboard
from pyrogram import types

from db import DataBase


config = json.loads(open("config.json", "r", encoding="utf-8").read())
db = DataBase()

init_ts = time.perf_counter()

lesson_types = {
    "subject": ["📚", "предмет"],
    "ea": ["🧩", "факультатив"]
}

regions = {
    "CHEL_OBL": {
        "name": "Челябинская область",
        "url": "https://sgo.edu-74.ru"
    },
    "ALTAI_KRAI": {
        "name": "Алтайский край",
        "url": "https://netschool.edu22.info"
    },
    "AMUR_OBL": {
        "name": "Амурская область",
        "url": "https://region.obramur.ru"
    },
    "KALUG_OBL": {
        "name": "Калужская область",
        "url": "https://edu.admoblkaluga.ru:444"
    },
    "KOSTROMS_OBL": {
        "name": "Костромская область",
        "url": "https://netschool.eduportal44.ru"
    },
    "KAMCH_KRAI": {
        "name": "Камчатский край",
        "url": "https://school.sgo41.ru"
    },
    "KRASNOD_KRAI": {
        "name": "Краснодарский край",
        "url": "https://sgo.rso23.ru"
    },
    "LENINGRAD_OBL": {
        "name": "Ленинградская область",
        "url": "https://e-school.obr.lenreg.ru"
    },
    "ZABAIKAL_KRAI": {
        "name": "Забайкальский край",
        "url": "https://region.zabedu.ru"
    },
    "PRIMORSK_KRAI": {
        "name": "Приморский край",
        "url": "https://sgo.prim-edu.ru"
    },
    "RESP_BUR": {
        "name": "Республика Бурятия",
        "url": "https://deti.obr03.ru"
    },
    "RESP_MARI_EL": {
        "name": "Республика Марий Эл",
        "url": "https://sgo.mari-el.gov.ru"
    },
    "RESP_MORD": {
        "name": "Республика Мордовия",
        "url": "https://sgo.e-mordovia.ru"
    },
    "RESP_SAHA": {
        "name": "Республика Саха Якутия",
        "url": "https://sgo.e-yakutia.ru"
    },
    "RESP_KOMI": {
        "name": "Республика Коми",
        "url": "https://giseo.rkomi.ru"
    },
    "SAMARSK_OBL": {
        "name": "Самарская область",
        "url": "https://asurso.ru"
    },
    "SAHALINSK_OBL": {
        "name": "Сахалинская область",
        "url": "https://netcity.admsakhalin.ru:11111"
    },
    "TVERSK_OBL": {
        "name": "Тверская область",
        "url": "https://sgo.tvobr.ru"
    },
    "TOMSK_OBL": {
        "name": "Томская область",
        "url": "https://sgo.tomedu.ru"
    },
    "YLANOVSK_OBL": {
        "name": "Ульяновская область",
        "url": "https://sgo.cit73.ru"
    },
    "CHERNOG": {
        "name": "Черноголовка",
        "url": "https://journal.nschg.ru"
    },
    "CHUV_RESP": {
        "name": "Чувашская Республика",
        "url": "https://net-school.cap.ru"
    },
    "YAMAL": {
        "name": "Ямало-Ненецкий Автономный Округ",
        "url": "https://sgo.yanao.ru"
    }
}


def init_db():
    db.save(
        "CREATE TABLE IF NOT EXISTS accounts( " \
            "id INTEGER PRIMARY KEY, " \
            "ns_id INTEGER DEFAULT 0, " \
            "ns_url TEXT DEFAULT '', " \
            "ns_school_id INTEGER DEFAULT 0, " \
            "ns_login TEXT DEFAULT '', " \
            "ns_password TEXT DEFAULT ''"
        ")"
    )
    db.save(
        "CREATE TABLE IF NOT EXISTS users( " \
            "id INTEGER PRIMARY KEY, " \
            "status INTEGER DEFAULT 0, " \
            "set_mailing_schedule INTEGER DEFAULT 0, " \
            "mailing_schedule_time TEXT DEFAULT '07:00', " \
            "last_mail_send TEXT DEFAULT ''" \
        ")"
    )
    db.regUser(config['dev_id'], status=2)


def printMe():
    print(f"\033[36m          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █\033[0m")
    print(f"\033[36m          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄\033[0m")
    print(f"\033[36m                © Copyright 2024\033[0m")
    print(f"\033[36m            ✈ https://t.me/unneyon\033[0m", end="\n\n")
    print(f"\033[36m 🔒 Licensed under CC-BY-NC-ND 4.0 unless otherwise specified.\033[0m")
    print(f"\033[36m 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0\033[0m")
    print(f"\033[36m + attribution\033[0m")
    print(f"\033[36m + non-commercial\033[0m")
    print(f"\033[36m + no-derivatives\033[0m")


def checkConfig():
    all_items = ["token", "id", "dev_id", "commands", "app"]
    items = []
    for i in all_items:
        if not config.get(i):
            items.append(i)
    if len(items) != 0:
        error = f"\033[31mВ файле \033[36mconfig.json\033[31m отсутству{'e' if len(items) == 1 else 'ю'}т " \
                f"пол{'e' if len(items) == 1 else 'я'} \033[36m{', '.join(items)}\033[31m!\033[0m"
        exit(error)


async def sendBackup():
    from loader import client

    dbf = io.BytesIO(open("db.db", "rb").read())
    dbf.name = "db.db"
    dbf = pyrogram.types.InputMediaDocument(dbf)
    cfgf = io.BytesIO(open("config.json", "rb").read())
    cfgf.name = "config.json"
    cfgf = pyrogram.types.InputMediaDocument(cfgf, caption="#backup")

    await client.send_media_group(
        chat_id=(config['debug_chat'] if config['debug_chat'] != 0 else config['dev_id']),
        media=[dbf, cfgf],
        disable_notification=True
    )


async def sendSchedule():
    from loader import client
    import netschoolapi as nsapi

    now = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))
    day = now
    to_mail = db.recvs(
        "SELECT * FROM users WHERE set_mailing_schedule = ? AND mailing_schedule_time = ?",
        1, now.strftime("%H:%M")
    )

    for user in to_mail:
        user = db.getUser(user[0])
        if user[4] == day.strftime("%d.%m.%Y"):
            continue
        if not db.getNSUser(user[0]):
            await answer(
                client,
                "☹️ <b>Здесь должна была быть рассылка расписания, однако вы не авторизованы. " \
                "Рассылка будет отключена.</b>",
                reply=False,
                chat_id=user[0]
            )
            db.save("UPDATE users SET set_mailing_schedule = ? WHERE id = ?", 0, user[0])
            continue

        week = get_week(day)
        week = week if week != get_week(datetime.datetime.today()) else None

        try:
            ns = await db.getUserNS(user[0])
            nsUser = await ns.mysettings()
            d = await ns.diary(week[0] if week else None, week[1] if week else None)
            schedule = sorted(d.schedule, key=lambda x: x.day)
        except nsapi.errors.NetSchoolAPIError as e:
            continue

        need_day = None
        for i in schedule:
            if i.day.strftime("%d.%m.%Y") == day.strftime("%d.%m.%Y"):
                need_day = i
                break
        if (not need_day):
            out = "☹ <b>Рассылка: на этот день нет расписания, или я не смог его найти.</b>"
        else:
            lessons = []
            for index, lessn in enumerate(need_day.lessons):
                ltype = "subject"
                if lessn.is_ea_lesson:
                    ltype = "ea"
                hw, hw_desc, marks, debts = "", "", [], []
                out = f"{lesson_types[ltype][0]} <b>{lessn.number}. {lesson_types[ltype][1].title()}: {lessn.subject}</b>" \
                    f"\n🪑 <b>Кабинет:</b> <b><i>{lessn.room if lessn.room else 'не указан'}</i></b>" \
                    f"\n⏰ <b>Время проведения:</b> <b><i>{lessn.start.strftime('%H:%M')} — {lessn.end.strftime('%H:%M')}</i></b>"
                lessons.append(out)
            out = f"📆 <b>Рассылка расписания на {need_day.day.strftime('%d.%m.%Y')}:</b>\n\n\n" + "\n\n\n".join(lessons)

        await ns.full_logout()
        db.save("UPDATE users SET last_mail_send = ? WHERE id = ?", now.strftime("%d.%m.%Y"), user[0])
        return await answer(
            client, out, reply=False, chat_id=user[0]
        )


def getMenuKB(uid: int) -> types.InlineKeyboardMarkup:
    user = db.recvs("SELECT * FROM accounts WHERE id = ?", uid)
    if user:
        return types.ReplyKeyboardMarkup([
            [
                types.KeyboardButton(text="📕 Дневник"),
                types.KeyboardButton(text="💮 Оценки")
            ],
            [
                types.KeyboardButton(text="📢 Объявления"),
                types.KeyboardButton(text="✉️ Почта")
            ],
            [
                types.KeyboardButton(text="⚙️ Настройки")
            ]
        ], is_persistent=True, resize_keyboard=True, placeholder="Выберите действие")
    else:
        return types.ReplyKeyboardMarkup([
            [types.KeyboardButton(text="❤️ Войти в аккаунт")]
        ], is_persistent=True, resize_keyboard=True, placeholder="Авторизуйтесь")


def check_url(url: str) -> bool:
    try:
        return bool(urlparse(url).netloc)
    except Exception:
        return False


def get_week(week: typing.Tuple[str, datetime.datetime]):
    if isinstance(week, str):
        monday = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    else:
        monday = week - datetime.timedelta(days=week.weekday())
    d1, d6 = None, None
    if week == "next":
        d1, d6 = (monday + datetime.timedelta(days=7)), ((monday + datetime.timedelta(days=7)) + datetime.timedelta(days=5))
    elif week == "prev":
        d1, d6 = (monday - datetime.timedelta(days=7)), (monday - datetime.timedelta(days=7)) + datetime.timedelta(days=5)
    else:
        d1, d6 = monday, (monday + datetime.timedelta(days=5))
    return [
        datetime.datetime.strptime(d1.strftime("%d.%m.%Y"), "%d.%m.%Y"),
        datetime.datetime.strptime(d6.strftime("%d.%m.%Y"), "%d.%m.%Y")
    ]


def censor(ret: str) -> str:
    ret = ret.replace(config['token'], f'{config["token"].split(":")[0]}:{"*"*26}').replace(str(config['app']['id']), "*"*len(str(config['app']['id']))).replace(config['app']['hash'], "*"*len(config['app']['hash']))

    return ret

    
async def resolveByUsername(client, username):
    try:
        r = await client.invoke(
        pyrogram.raw.functions.contacts.ResolveUsername(username=username)
    )
    except:
        r = None
    try:
        c = await client.resolve_peer(username)
    except:
        c = None

    if r and r.users:
        for i in r.users:
            if i.username == username:
                return i.id
    elif c:
        return c.user_id
    return 0

async def getIdByText(client, text):
    url = re.findall(r't\.me/([a-zA-Z0-9_\.]+)', text)
    if len(url) > 0:
        return await resolveByUsername(client, url[0])
    tag = re.findall(r'@([a-zA-Z0-9_\.]+)', text)
    if len(tag) > 0:
        return await resolveByUsername(client, tag[0])

    domain = await resolveByUsername(client, text)
    return domain

async def getID(message):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id

    args = get_args(message)
    text = ""
    if len(args) != 0:
        text = args[0]
    if str(text).isdigit():
        return int(text)

    return await getIdByText(message._client, text)


def pluralForm(count, variants):
    count = abs(count)
    if count % 10 == 1 and count % 100 != 11:
        var = 0
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        var = 1
    else:
        var = 2
    return f"{count} {variants[var]}"


def split_list(input_list: typing.List, chunk_size: int):
    return [input_list[i:i+chunk_size] for i in range(0, len(input_list), chunk_size)]


def get_args(message):
    text = message.text or message.caption
    text = text.split(maxsplit=1)[1:]
    if len(text) == 0:
        return []
    return text[0].split()


def get_raw_args(message):
    text = message.text or message.caption
    text = text.split(maxsplit=1)[1:]
    if len(text) == 0:
        return ""
    return text[0]


def remove_html(text: str, keep_emojis: bool = False) -> str:
    return str(
        re.sub(
            r"(<\/?a.*?>|<\/?b>|<\/?i>|<\/?u>|<\/?strong>|<\/?em>|<\/?code>|<\/?strike>|<\/?del>|<\/?pre.*?>|<\/?emoji.*?>)",
            "",
            text,
        )
    )


def run_sync(func, *args, **kwargs):
    return asyncio.get_event_loop().run_in_executor(
        None,
        functools.partial(func, *args, **kwargs),
    )

def run_async(loop: asyncio.AbstractEventLoop, coro: typing.Awaitable) -> typing.Any:
    return asyncio.run_coroutine_threadsafe(coro, loop).result()


async def answer(
    message: typing.Union[pyrogram.types.Message, pyrogram.Client],
    response: str = "",
    reply: bool = True, reply_to: int = None,
    chat_id: int = 0,
    message_id: int = 0,
    message_thread_id: int = 0,
    photo: typing.Union[str, typing.BinaryIO] = None,
    video: typing.Union[str, typing.BinaryIO] = None,
    animation: typing.Union[str, typing.BinaryIO] = None,
    document: typing.Union[str, typing.BinaryIO] = None,
    sticker: typing.Union[str, typing.BinaryIO] = None,
    video_note: typing.Union[str, typing.BinaryIO] = None,
    voice: typing.Union[str, typing.BinaryIO] = None,
    media: typing.List[typing.Union[
        "pyrogram.types.InputMediaAnimation",
        "pyrogram.types.InputMediaAudio",
        "pyrogram.types.InputMediaDocument",
        "pyrogram.types.InputMediaPhoto",
        "pyrogram.types.InputMediaVideo"
    ]] = None,
    **kwargs
) -> typing.List[pyrogram.types.Message]:
    response = censor(response) if response else ""
    if isinstance(message, list):
        message = message[0]
    msgs, responses, have_media = [], [], bool(photo or video or animation or document or sticker or video_note or voice or media)
    if len(response) > (1024 if have_media else 4096):
        for x in range(0, len(response), 1024 if have_media else 4096):
            responses.append(response[x:x+(1024 if have_media else 4096)])
    else:
        responses = [response]

    if isinstance(message, pyrogram.Client):
        client = message
        if not reply_to:
            reply = False
            reply_to = None
    elif isinstance(message, pyrogram.types.Message):
        client = message._client
        if (reply) and (not reply_to):
            reply_to = message.id
        chat_id = chat_id if chat_id != 0 else message.chat.id
        message_thread_id = message_thread_id if message_thread_id != 0 else message.message_thread_id
    elif isinstance(message, pyrogram.types.CallbackQuery):
        client = message._client
        if (reply) and (not reply_to):
            if message.message.reply_to_message:
                reply_to = message.message.reply_to_message.id
        chat_id = chat_id if chat_id != 0 else message.message.chat.id
        message_id = message_id if message_id != 0 else message.message.id
        message_thread_id = message_thread_id if message_thread_id != 0 else message.message.message_thread_id

    if not have_media:
        for resp in responses:
            msgs.append(await client.send_message(
                chat_id=chat_id, text=resp,
                reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                disable_notification=True,
                message_thread_id=message_thread_id,
                link_preview_options=pyrogram.types.LinkPreviewOptions(is_disabled=True),
                **kwargs
            ))
    else:
        # animation document poll sticker video_note voice
        if photo:
            msgs.append(await client.send_photo(
                chat_id=chat_id, photo=photo,
                caption=responses[0],
                message_thread_id=message_thread_id,
                reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                disable_notification=True,
                **kwargs
            ))
        elif video:
            msgs.append(await client.send_video(
                chat_id=chat_id, video=video,
                caption=responses[0],
                message_thread_id=message_thread_id,
                reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                disable_notification=True,
                **kwargs
            ))
        elif animation:
            msgs.append(await client.send_animation(
                chat_id=chat_id, animation=animation,
                caption=responses[0],
                message_thread_id=message_thread_id,
                reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                disable_notification=True,
                **kwargs
            ))
        elif document:
            msgs.append(await client.send_document(
                chat_id=chat_id, document=document,
                caption=responses[0],
                message_thread_id=message_thread_id,
                reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                disable_notification=True,
                **kwargs
            ))
        elif sticker:
            msgs.append(await client.send_sticker(
                chat_id=chat_id, sticker=sticker,
                message_thread_id=message_thread_id,
                reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                disable_notification=True,
                **kwargs
            ))
        elif video_note:
            msgs.append(await client.send_video_note(
                chat_id=chat_id, video_note=video_note,
                message_thread_id=message_thread_id,
                reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                disable_notification=True,
                **kwargs
            ))
        elif voice:
            msgs.append(await client.send_voice(
                chat_id=chat_id, voice=voice,
                caption=responses[0],
                message_thread_id=message_thread_id,
                reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                disable_notification=True,
                **kwargs
            ))
        elif media:
            msgs.append(await client.send_media_group(
                chat_id=chat_id, media=media,
                message_thread_id=message_thread_id,
                reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                disable_notification=True,
                **kwargs
            ))

        if len(responses) > 1:
            for resp in responses[1:]:
                msgs.append(await client.send_message(
                    chat_id=message.chat.id if chat_id == 0 else chat_id,
                    text=resp,
                    reply_parameters=pyrogram.types.ReplyParameters(message_id=reply_to),
                    disable_notification=True,
                    link_preview_options=pyrogram.types.LinkPreviewOptions(is_disabled=True),
                    message_thread_id=(message_thread_id if message_thread_id != 0 else (message.message_thread_id if (isinstance(message, pyrogram.types.Message) and message.message_thread_id) else None)),
                    **kwargs
                ))

    return msgs


async def edit(
    message: typing.Union[
        pyrogram.Client,
        pyrogram.types.Message,
        pyrogram.types.CallbackQuery,
        pyrogram.types.Update
    ],
    response: str = "",
    id: int = 0,
    chat_id: int = 0,
    media: typing.Union[
        "pyrogram.types.InputMediaPhoto",
        "pyrogram.types.InputMediaVideo",
        "pyrogram.types.InputMediaAudio",
        "pyrogram.types.InputMediaDocument"
    ] = None,
    **kwargs
) -> pyrogram.types.Message:
    if isinstance(message, list):
        message = message[0]
        client = message._client
    elif isinstance(message, pyrogram.Client):
        client = message
    elif isinstance(message, pyrogram.types.Update) or isinstance(message, pyrogram.types.CallbackQuery) or isinstance(message, pyrogram.types.Message):
        client = message._client
    response = censor(response)

    if hasattr(message, "inline_message_id") and message.inline_message_id:
        await client.edit_inline_text(
            inline_message_id=message.inline_message_id,
            text=response,
            link_preview_options=pyrogram.types.LinkPreviewOptions(is_disabled=True),
            **kwargs
        )
    else:
        if media:
            return await client.edit_message_media(
                chat_id=message.chat.id if (chat_id == 0 and isinstance(message, pyrogram.types.Update)) else chat_id,
                message_id=message.id if (id == 0 and isinstance(message, pyrogram.types.Update)) else id,
                media=media,
                **kwargs
            )
        else:
            return await client.edit_message_text(
                chat_id=message.chat.id if (chat_id == 0 and isinstance(message, pyrogram.types.Update)) else chat_id,
                message_id=message.id if (id == 0 and isinstance(message, pyrogram.types.Update)) else id,
                text=response,
                link_preview_options=pyrogram.types.LinkPreviewOptions(is_disabled=True),
                **kwargs
            )