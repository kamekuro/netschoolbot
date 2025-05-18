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
from loader import cache


diary = Router("diary")
logger = logging.getLogger(__name__)


async def genDiary(day: datetime.datetime, week: list, user: list, msg: types.Message):
    try:
        ns = await utils.db.getUserNS(user[0])
        nsUser = await ns.mysettings()
        d = await ns.diary(week[0] if week else None, week[1] if week else None)
        schedule = sorted(d.schedule, key=lambda x: x.day)
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(
            msg, e
        )

    need_day = None
    for i in schedule:
        if i.day.strftime("%d.%m.%Y") == day.strftime("%d.%m.%Y"):
            need_day = i
            break
    if (not need_day):
        await ns.full_logout()
        kb = pyroboard.InlineKeyboard(1)
        if day.strftime("%d.%m.%Y") == datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y"):
            kb.row(types.InlineKeyboardButton(
                text="➡️ Завтра", callback_data=f"d_tmrrw:{user[0]}"
            ))
        elif day.strftime("%d.%m.%Y") == (datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))+datetime.timedelta(days=1)).strftime("%d.%m.%Y"):
            kb.row(types.InlineKeyboardButton(
                text="⬅️ Сегодня", callback_data=f"d_tdy:{user[0]}"
            ))
        kb.row(types.InlineKeyboardButton(
            text="📆 Узнать расписание на другой день", callback_data=f"chday:{user[0]}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="◀️ Главное меню", callback_data=f"mmenu:{user[0]}"
        ))
        return await utils.edit(
            msg, "☹ <b>Не удалось найти расписание на этот день.</b>",
            reply_markup=kb
        )

    lessons = []
    attachments = {}
    for index, lessn in enumerate(need_day.lessons):
        ltype = "ea" if lessn.is_ea_lesson else "subject"
        hw, hw_desc, marks, debts = "", "", [], []
        for ass in lessn.assignments:
            if ass.mark:
                marks.append(str(ass.mark))
            if ass.type == "Домашнее задание":
                try:
                    homework: dict = await ns.request(
                        "GET", f"student/diary/assigns/{ass.id}",
                        params={
                            "studentId": nsUser.user_settings.user_id
                        }
                    )
                    hw = homework['assignmentName']
                    if homework.get("description"):
                        hw_desc = homework['description']
                    if homework.get("attachments"):
                        atts = attachments.get(str(index), [])
                        for attach in homework['attachments']:
                            attachs = await ns.request(
                                "POST", f"student/diary/get-attachments?studentId={nsUser.user_settings.user_id}",
                                json={"assignId": [ass.id]}
                            )
                            docname = '.'.join(attach['originalFileName'].split(".")[:-1])
                            ext = attach['originalFileName'].split(".")[-1]
                            file = io.BytesIO()
                            await ns.download_attachment(attach['id'], file)
                            file.name = docname + "." + ext
                            atts.append({
                                "bytes": file, "name": lessn.subject,
                                "docname": docname, "ext": ext
                            })
                        if len(atts) > 0: attachments[str(index)] = atts
                except:
                    hw = ass.content
            if ass.is_duty:
                debts.append(f"{ass.type}" + (f": {ass.content}" if ass.content else ""))
        out = f"{utils.lesson_types[ltype][0]} <b>{lessn.number}. {utils.lesson_types[ltype][1].title()}: {lessn.subject}</b>" \
              f"\n🪑 <b>Кабинет:</b> <b><i>{lessn.room if lessn.room else 'не указан'}</i></b>" \
              f"\n⏰ <b>Время проведения:</b> <b><i>{lessn.start.strftime('%H:%M')} — {lessn.end.strftime('%H:%M')}</i></b>"
        if hw:
            out += f"\n📝 <b>Домашнее задание:</b> {hw}"
        if hw_desc:
            out += f"\n❕ <b>Подробности от учителя</b>:\n<blockquote expandable>{hw_desc}</blockquote>"
        if marks:
            out += f"\n💮 <b>Оценк{'а' if len(marks) == 1 else 'и'}:</b> {', '.join(marks)}"
        if len(debts) > 0:
            out += f"\n❗ <b><u>За этот урок у Вас сто{'и' if len(debts) == 1 else 'я'}т «точк{'а' if len(debts) == 1 else 'и'}» за:</b></u>"
            for debt in debts:
                out += f"\n  ▪️ <b>{debt}</b>"
        lessons.append(out)
    out = f"📆 <b>{need_day.day.strftime('%d.%m.%Y')}</b>\n\n\n" + "\n\n\n".join(lessons)

    await ns.full_logout()

    return {
        "out": out,
        "lessons": lessons,
        "attachments": attachments
    }



@diary.on_message(
    filters.command(["diary", "дневник"])
    | filters.text("📕 Дневник", False)
)
async def diary_cmd(client: pyrogram.Client, message: types.Message):
    msg = await utils.answer(message, "🕓 Подождите…")
    user = utils.db.getNSUser(message.from_user.id)
    if not user:
        return await utils.edit(
            msg,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )

    today = datetime.datetime.today()
    dd = await genDiary(today, None, utils.db.getUser(message.from_user.id), msg)
    if type(dd) != dict: return

    kb = pyroboard.InlineKeyboard(1)

    msgs_to_del = []
    if (not dd['attachments']) and (len(dd['out']) < 4096):
        kb.row(types.InlineKeyboardButton(
            text="➡️ Завтра",
            callback_data=f"d_tmrrw:{message.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="📆 Узнать расписание на другой день",
            callback_data=f"chday:{message.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="◀️ Главное меню",
            callback_data=f"mmenu:{message.from_user.id}"
        ))
        await utils.edit(
            msg, dd['out'],
            reply_markup=kb
        )
    else:
        await (msg if type(msg) == types.Message else msg[0]).delete()
        for index, lesson in enumerate(dd['lessons']):
            out = f"📆 <b>{today.strftime('%d.%m.%Y')}</b>\n\n{lesson}"
            att = dd['attachments'].get(str(index), [])
            msg = (await utils.answer(
                message, out, reply=False,
                media=[types.InputMediaDocument(x['bytes'], caption=out) for x in att]
            ))[0]
            msgs_to_del.append((msg if type(msg) == types.Message else msg[0]).id)
        await cache.set(f"diary_{message.from_user.id}", {"msgs_to_del": msgs_to_del})
        kb.row(types.InlineKeyboardButton(
            text="➡️ Завтра",
            callback_data=f"d_tmrrw:{message.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="📆 Узнать расписание на другой день",
            callback_data=f"chday:{message.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="◀️ Главное меню",
            callback_data=f"mmenu:{message.from_user.id}"
        ))
        await utils.answer(
            message,
            f"<b>Управление кнопками здесь:</b>",
            reply_markup=kb
        )



@diary.on_callback_query(
    filters.startswith("d_tmrrw:")
)
async def get_diary_tomorrow(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[1]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True
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

    await query.answer("🕓 Подождите…", True)

    user = utils.db.getNSUser(query.from_user.id)
    if not user:
        return await utils.edit(
            msg,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )

    day = datetime.datetime.today() + datetime.timedelta(days=1)
    week = utils.get_week(day)
    week = week if week != utils.get_week(datetime.datetime.today()) else None
    dd = await genDiary(day, week, utils.db.getUser(query.from_user.id), query.message)
    if type(dd) != dict: return

    kb = pyroboard.InlineKeyboard(1)

    msgs_to_del = []
    if (not dd['attachments']) and (len(dd['out']) < 4096):
        kb.row(types.InlineKeyboardButton(
            text="⬅️ Сегодня",
            callback_data=f"d_tdy:{query.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="📆 Узнать расписание на другой день",
            callback_data=f"chday:{query.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="◀️ Главное меню",
            callback_data=f"mmenu:{query.from_user.id}"
        ))
        await utils.edit(
            query.message, dd['out'],
            reply_markup=kb
        )
    else:
        await query.message.delete()
        for index, lesson in enumerate(dd['lessons']):
            out = f"📆 <b>{day.strftime('%d.%m.%Y')}</b>\n\n{lesson}"
            att = dd['attachments'].get(str(index), [])
            msg = (await utils.answer(
                query.message, out, reply=False,
                media=[types.InputMediaDocument(x['bytes'], caption=out) for x in att]
            ))[0]
            msgs_to_del.append((msg if type(msg) == types.Message else msg[0]).id)
        await cache.set(f"diary_{query.from_user.id}", {"msgs_to_del": msgs_to_del})
        kb.row(types.InlineKeyboardButton(
            text="⬅️ Сегодня",
            callback_data=f"d_tdy:{query.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="📆 Узнать расписание на другой день",
            callback_data=f"chday:{query.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="◀️ Главное меню",
            callback_data=f"mmenu:{query.from_user.id}"
        ))
        await utils.answer(
            query.message,
            f"<b>Управление кнопками здесь:</b>",
            reply_markup=kb
        )



@diary.on_callback_query(
    filters.startswith("d_tdy:")
)
async def get_diary_tomorrow(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[1]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True
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

    await query.answer("🕓 Подождите…", True)

    user = utils.db.getNSUser(query.from_user.id)
    if not user:
        return await utils.edit(
            query.message,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )

    day = datetime.datetime.today()
    week = utils.get_week(day)
    week = week if week != utils.get_week(datetime.datetime.today()) else None
    dd = await genDiary(day, week, utils.db.getUser(query.from_user.id), query.message)
    if type(dd) != dict: return

    kb = pyroboard.InlineKeyboard(1)

    msgs_to_del = []
    if (not dd['attachments']) and (len(dd['out']) < 4096):
        kb.row(types.InlineKeyboardButton(
            text="➡️ Завтра",
            callback_data=f"d_tmrrw:{query.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="📆 Узнать расписание на другой день",
            callback_data=f"chday:{query.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="◀️ Главное меню",
            callback_data=f"mmenu:{query.from_user.id}"
        ))
        await utils.edit(
            query.message, dd['out'],
            reply_markup=kb
        )
    else:
        await query.message.delete()
        for index, lesson in enumerate(dd['lessons']):
            out = f"📆 <b>{day.strftime('%d.%m.%Y')}</b>\n\n{lesson}"
            att = dd['attachments'].get(str(index), [])
            msg = (await utils.answer(
                query.message, out, reply=False,
                media=[types.InputMediaDocument(x['bytes'], caption=out) for x in att]
            ))[0]
            msgs_to_del.append((msg if type(msg) == types.Message else msg[0]).id)
        await cache.set(f"diary_{query.from_user.id}", {"msgs_to_del": msgs_to_del})
        kb.row(types.InlineKeyboardButton(
            text="➡️ Завтра",
            callback_data=f"d_tmrrw:{query.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="📆 Узнать расписание на другой день",
            callback_data=f"chday:{query.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="◀️ Главное меню",
            callback_data=f"mmenu:{query.from_user.id}"
        ))
        await utils.answer(
            query.message,
            f"<b>Управление кнопками здесь:</b>",
            reply_markup=kb
        )



@diary.on_callback_query(
    filters.startswith("chday:")
)
async def get_custom_day_to_get_diary(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[1]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True
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

    await query.answer("🕓 Подождите…", True)

    user = utils.db.getNSUser(query.from_user.id)
    if not user:
        return await utils.edit(
            query.message,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )

    await utils.edit(
        query.message,
        f"📆 <b>Укажите дату, чтобы получить дневник на нужный день, в формате ДД.ММ.ГГГГ " \
        f"(например: 01.01.2024):</b>"
    )
    await dispatch.fsm.set_state(
        client, "diary:get_custom_date",
        query.from_user.id, query.message.chat.id
    )



@diary.on_message(
    dispatch.fsm.StateFilter("diary:get_custom_date")
)
async def get_diary_custom_date(client: pyrogram.Client, message: types.Message):
    msg = await utils.answer(message, "🕓 Подождите…")
    date = message.text

    try:
        day = datetime.datetime.strptime(date, "%d.%m.%Y")
    except:
        await dispatch.fsm.set_state(
            client, "diary:get_custom_date",
            message.from_user.id, message.chat.id
        )
        return await utils.edit(
            msg,
            f"😔 <b>Извините, но Вы ввели дату в неверном формате.</b>\n" \
            f"Вы можете снова попробовать ввести дату, чтобы получить дневник на этот день, " \
            f"или использовать команду /cancel для отмены.\n\n" \
            f"📆 <b>Чтобы получить дневник на определённую дату, укажите её в формате ДД.ММ.ГГГГ " \
            f"(например: 01.01.2024):</b>"
        )

    user = utils.db.getNSUser(message.from_user.id)
    if not user:
        return await utils.edit(
            msg,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )

    week = utils.get_week(day)
    week = week if week != utils.get_week(datetime.datetime.today()) else None
    dd = await genDiary(day, week, utils.db.getUser(message.from_user.id), message)
    if type(dd) != dict: return

    kb = pyroboard.InlineKeyboard(1)

    msgs_to_del = []
    if (not dd['attachments']) and (len(dd['out']) < 4096):
        kb.row(types.InlineKeyboardButton(
            text="📆 Узнать расписание на другой день",
            callback_data=f"chday:{message.from_user.id}:ndl"
        ))
        kb.row(types.InlineKeyboardButton(
            text="◀️ Главное меню",
            callback_data=f"mmenu:{message.from_user.id}:ndl"
        ))
        await utils.edit(
            msg, dd['out'],
            reply_markup=kb
        )
    else:
        await (msg if type(msg) == types.Message else msg[0]).delete()
        for index, lesson in enumerate(dd['lessons']):
            out = f"📆 <b>{day.strftime('%d.%m.%Y')}</b>\n\n{lesson}"
            att = dd['attachments'].get(str(index), [])
            msg = (await utils.answer(
                message, out, reply=False,
                media=[types.InputMediaDocument(x['bytes'], caption=out) for x in att]
            ))[0]
            msgs_to_del.append((msg if type(msg) == types.Message else msg[0]).id)
        await cache.set(f"diary_{message.from_user.id}", {"msgs_to_del": msgs_to_del})
        kb.row(types.InlineKeyboardButton(
            text="📆 Узнать расписание на другой день",
            callback_data=f"chday:{message.from_user.id}"
        ))
        kb.row(types.InlineKeyboardButton(
            text="◀️ Главное меню",
            callback_data=f"mmenu:{message.from_user.id}"
        ))
        await utils.answer(
            message,
            f"<b>Управление кнопками здесь:</b>",
            reply_markup=kb
        )