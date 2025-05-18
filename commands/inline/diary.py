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
import httpx
import logging

import pyrogram
import pyroboard
from pyrogram import types

import netschoolapi as nsapi

import utils
from dispatch import filters
from dispatch.routing import Router


diary = Router("idiary")
logger = logging.getLogger(__name__)


# Choosing date

@diary.on_callback_query(
    filters.startswith("idiary:")
)
async def get_diary_from_inline(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[1]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True, cache_time=0
        )

    await query.answer(
        "🕓 Подождите…", True, cache_time=0
    )

    weekdays = {
        0: "ПН", 1: "ВТ", 2: "СР",
        3: "ЧТ", 4: "ПТ", 5: "СБ",
        6: "ВС",
    }
    user = utils.db.getUser(query.from_user.id)

    if not utils.db.getNSUser(query.from_user.id):
        return await utils.edit(
            query,
            f"🤨 <b>Вы не авторизованы!</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
                )]
            ])
        )

    try:
        ns = await utils.db.getUserNS(query.from_user.id)
        d = await ns.diary()
        schedule = sorted(d.schedule, key=lambda x: x.day)
        await ns.full_logout()
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(
            query, e,
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
                )]
            ])
        )

    if len(schedule) == 0:
        return await utils.edit(
            query,
            "☹ <b>Не удалось найти расписание на эту неделю.</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
                )]
            ])
        )

    kb = pyroboard.InlineKeyboard(row_width=2)
    buttons = []
    for i in schedule:
        buttons.append(types.InlineKeyboardButton(
            callback_data=f"idiary_d:{i.day.strftime('%d.%m.%Y')}:this:{query.from_user.id}",
            text=f"{weekdays[i.day.weekday()]} {i.day.strftime('%d.%m.%Y')}"
        ))
    kb.add(*buttons)
    kb.row(
        types.InlineKeyboardButton(callback_data=f"idiary_w:prev:{query.from_user.id}", text="← Пред. неделя"),
        types.InlineKeyboardButton(callback_data=f"idiary_w:next:{query.from_user.id}", text="→ След. неделя")
    )
    kb.row(
        types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}")
    )

    await utils.edit(query, "📆 <b>Выбери день</b>", reply_markup=kb)



# Change week

@diary.on_callback_query(
    filters.startswith("idiary_w:")
)
async def get_week_inline(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[2]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True, cache_time=0
        )

    await query.answer(
        "🕓 Подождите…", True, cache_time=0
    )

    week = query.data.split(":")[1]
    need_week = utils.get_week(week)
    user = utils.db.getUser(query.from_user.id)
    weekdays = {
        0: "ПН", 1: "ВТ", 2: "СР",
        3: "ЧТ", 4: "ПТ", 5: "СБ",
        6: "ВС",
    }

    if not utils.db.getNSUser(query.from_user.id):
        return await utils.edit(
            query,
            f"🤨 <b>Вы не авторизованы!</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
                )]
            ])
        )

    try:
        ns = await utils.db.getUserNS(query.from_user.id)
        d = await ns.diary(start=need_week[0], end=need_week[1])
        schedule = sorted(d.schedule, key=lambda x: x.day)
        await ns.full_logout()
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(
            query, e,
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
                )]
            ])
        )

    if len(schedule) == 0:
        return await utils.edit(
            query,
            "☹ <b>Не удалось найти расписание на эту неделю.</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
                )]
            ])
        )

    kb = pyroboard.InlineKeyboard(row_width=2)
    buttons = []
    for i in schedule:
        buttons.append(types.InlineKeyboardButton(
            callback_data=f"idiary_d:{i.day.strftime('%d.%m.%Y')}:{week}:{query.from_user.id}",
            text=f"{weekdays[i.day.weekday()]} {i.day.strftime('%d.%m.%Y')}"
        ))
    kb.add(*buttons)
    week_kbs = [
        types.InlineKeyboardButton(
            callback_data=f"idiary_w:prev:{query.from_user.id}", text="← Пред. неделя"
        ),
        types.InlineKeyboardButton(
            callback_data=f"idiary_w:next:{query.from_user.id}", text="→ След. неделя"
        )
    ]
    if week in ["prev", "next"]:
        week_kbs = [types.InlineKeyboardButton(
            callback_data=f"idiary_w:this:{query.from_user.id}",
            text=f"{'→' if week == 'prev' else '←'} Нынешн. неделя"
        )]
    kb.row(*week_kbs)
    kb.row(
        types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}")
    )

    await utils.edit(query, "📆 <b>Выбери день</b>", reply_markup=kb)



# Get the info about the day

@diary.on_callback_query(
    filters.startswith("idiary_d:")
)
async def get_day_inline(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[3]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True, cache_time=0
        )

    await query.answer(
        "🕓 Подождите…", True, cache_time=0
    )

    if not utils.db.getNSUser(query.from_user.id):
        return await utils.edit(
            query,
            f"🤨 <b>Вы не авторизованы!</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
                )]
            ])
        )

    day = datetime.datetime.strptime(query.data.split(":")[1], "%d.%m.%Y")
    week = query.data.split(":")[2]
    need_week = utils.get_week(week) if week != "not_week" else utils.get_week(day)
    user = utils.db.getUser(query.from_user.id)
    weekdays = {
        0: "ПН", 1: "ВТ", 2: "СР",
        3: "ЧТ", 4: "ПТ", 5: "СБ",
        6: "ВС",
    }


    try:
        ns = await utils.db.getUserNS(query.from_user.id)
        d = await ns.diary(start=need_week[0], end=need_week[1])
        nsUser = await ns.mysettings()
        schedule = d.schedule
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(
            query, e,
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
                )]
            ])
        )

    d = None
    logger.error(schedule)
    for i in schedule:
        if i.day.strftime("%d.%m.%Y") == day.strftime("%d.%m.%Y"):
            d = i
    if not d:
        await ns.full_logout()
        return await utils.edit(
            query,
            f"☹ <b>Не удалось найти расписание для этого дня</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад", callback_data=f"idiary_w:{week}:{query.from_user.id}"
                )]
            ])
        )

    ltypes = {
        "subject": ["📚", "предмет"],
        "ea": ["🧩", "факультатив"]
    }

    lessons = []
    for lessn in d.lessons:
        ltype = "subject"
        if lessn.is_ea_lesson: ltype = "ea"
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
                except:
                    hw = ass.content
            if ass.is_duty:
                debts.append(f"{ass.type}" + (f": {ass.content}" if ass.content else ""))
        out = f"{ltypes[ltype][0]} <b>{lessn.number}. {ltypes[ltype][1].title()}: {lessn.subject}</b>" \
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
    out = f"📆 <b>{day.strftime('%d.%m.%Y')}</b>\n\n\n" + "\n\n\n".join(lessons)

    await ns.full_logout()
    logger.error(out)

    kb = pyroboard.InlineKeyboard(1)

    if len(out) <= 4096:
        kb.row(types.InlineKeyboardButton(
            text="🔙 Назад", callback_data=f"idiary_w:{week}:{query.from_user.id}")
        )
        await utils.edit(
            query, out, reply_markup=kb
        )
    else:
        strday = day.strftime("%dT%mT%Y")
        kb.row(*[
            types.InlineKeyboardButton(
                text="✏️ Написать боту",
                url=f"https://t.me/{client.me.username}?start=dfi_{strday}"
            ),
            types.InlineKeyboardButton(
                text="🔙 Назад", callback_data=f"idiary_w:{week}:{query.from_user.id}"
            )
        ])
        return await utils.edit(
            query,
            f"☹ <b>Ответ слишком большой, используйте команду в лс с ботом.</b>\n"  \
            f"Вы также можете посмотреть дневник на другой день",
            reply_markup=kb
        )