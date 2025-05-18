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


marks = Router("imarks")
logger = logging.getLogger(__name__)


# Choosing the type of the report

@marks.on_callback_query(
    filters.startswith("imarks:")
)
async def get_marks_from_inline(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[1]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True, cache_time=0
        )

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

    await utils.edit(
        query,
        f"<b>📢 Выберите тип отчета</b>",
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(
                text="Средний балл (БЕТА)", callback_data=f"i_marks:by_d:{query.from_user.id}"
            )],
            [types.InlineKeyboardButton(
                text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
            )]
        ])
    )



# Marks by diary

@marks.on_callback_query(
    filters.startswith("i_marks:by_d")
)
async def get_average_marks_by_diary_from_inline(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[2]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True, cache_time=0
        )

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
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(
            query, e,
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"
                )]
            ])
        )

    kb = pyroboard.InlineKeyboard(1)
    per = (await ns.request("GET", "v2/reports/studenttotal"))['filterSources'][2]
    for i in per['items']:
        if str(i['value']) == "-1":
            continue
        kb.row(types.InlineKeyboardButton(
            text=i['title'],
            callback_data=f"imarks_by_d:{i['value']}:{query.from_user.id}"
        ))
    kb.row(types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}"))

    await ns.full_logout()
    await utils.edit(
        query,
        f"<b>Выберите учебный период</b>",
        reply_markup=kb
    )


@marks.on_callback_query(
    filters.startswith("imarks_by_d:")
)
async def get_average_marks_by_diary_from_inline(client: pyrogram.Client, query: types.CallbackQuery):
    if query.from_user.id != int(query.data.split(":")[2]):
        return await query.answer(
            "⚠ Эта кнопка не для Вас!", True, cache_time=0
        )

    filter_id = query.data.split(":")[1]

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

    await utils.edit(
        query,
        f"<b><u>⚠ ВНИМАНИЕ!</u>\nЭто — неофициальный отчёт из Сетевого Города, который берётся путём просматривания всех оценок в дневнике.\n\nПолучение оценок может занять время, пожалуйста, подождите.</b>"
    )

    try:
        ns = await utils.db.getUserNS(query.from_user.id)

        per = await ns.request("GET", "v2/reports/studenttotal", need_json=False)
        p = per.json()['filterSources']
        await asyncio.sleep(3)
        sid, pclid, termid, term_title = {}, {}, {}, ""
        for i in p:
            if i['filterId'] == "SID":
                sid = {
                    "filterId": i['filterId'],
                    "filterValue": i['items'][0]['value'],
                    "filterText": i['items'][0]['title']
                }
                continue
            elif i['filterId'] == "PCLID":
                pclid = {
                    "filterId": i['filterId'],
                    "filterValue": i['items'][0]['value'],
                    "filterText": i['items'][0]['title']
                }
                continue
            elif i['filterId'] == "TERMID":
                for fs in i['items']:
                    if fs['value'] == filter_id:
                        item = fs; break
                termid = {
                    "filterId": i['filterId'],
                    "filterValue": item['value'],
                    "filterText": item['title']
                }
                term_title = item['title']
                continue

        data = {
            "selectedData": [sid, pclid, termid],
            "params": None
        }
        await asyncio.sleep(3)
        period = (await ns.request(
            "POST", "v2/reports/studenttotal/initfilters", json=data,
            headers={
                "Content-Type": "application/json; charset=utf-8"
            }
        ))[0]['range']
        p1 = datetime.datetime.strptime(period['start'], "%Y-%m-%dT%H:%M:%S")
        p2 = datetime.datetime.strptime(period['end'], "%Y-%m-%dT%H:%M:%S")
        schedule = sorted((await ns.diary(p1, p2)).schedule, key=lambda x: x.day)
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

    marks = {}
    marks_with_duties = {}
    for day in schedule:
        for lesson in day.lessons:
            if lesson.is_ea_lesson: continue
            if not marks.get(lesson.subject):
                marks[lesson.subject] = [] 
            if not marks_with_duties.get(lesson.subject):
                marks_with_duties[lesson.subject] = []
            for ass in lesson.assignments:
                if ass.mark:
                    marks[lesson.subject].append(ass.mark)
                    marks_with_duties[lesson.subject].append(ass.mark)
                elif ass.is_duty:
                    marks_with_duties[lesson.subject].append("★")

    outs = []
    all_subjects = []
    for subject in list(sorted(marks.keys())):
        ms = " ".join(list(map(str, marks_with_duties[subject])))
        if not marks[subject]:
            ms = f"<b><i>нет оценок</i></b>"
        if len(marks[subject]) > 0:
            try: average_score = round(sum(marks[subject]) / len(marks[subject]), 2)
            except ZeroDivisionError: average_score = 0
        else:
            average_score = "н/о"
        if type(average_score) != str:
            all_subjects.append(average_score)
        outs.append(f"{subject}: {ms} | <b>{average_score}</b>")

    try: average_score = round(sum(all_subjects) / len(all_subjects), 2)
    except ZeroDivisionError: average_score = 0
    out = "\n".join(outs)
    msg = f"💮 <b>Отчет об успеваемости ученика за {term_title}:</b>\n" \
          f"<blockquote expandable>{out}</blockquote>" \
          f"\n\n<b>Средний балл по всем предметам: {average_score}</b>"

    await utils.edit(
        query, msg,
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data=f"open_imenu:{query.from_user.id}")
        ]])
    )