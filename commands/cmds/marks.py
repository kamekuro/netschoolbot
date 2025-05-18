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
import httpx

import pyrogram
import pyroboard
from pyrogram import types

import netschoolapi as nsapi

import utils
from dispatch import filters
from dispatch.routing import Router


marks = Router("marks")
logger = logging.getLogger(__name__)


@marks.on_message(
    filters.command(commands=["marks", "оценки"])
    | filters.text("💮 Оценки", False)
)
async def get_marks(client: pyrogram.Client, message: types.Message):
    user = utils.db.recvs("SELECT * FROM accounts WHERE id = ?", message.from_user.id)
    if not user:
        return await utils.answer(
            message,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )

    await utils.answer(
        message,
        f"<b>📢 Выберите тип отчета</b>",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton(callback_data="marks:by_d", text="Средний балл (БЕТА)")
        ]])
    )



@marks.on_callback_query(
    filters.startswith("marks:by_d")
)
async def get_marks_by_diary(client: pyrogram.Client, query: types.CallbackQuery):
    user = utils.db.recvs("SELECT * FROM accounts WHERE id = ?", query.from_user.id)
    if not user:
        return await utils.edit(
            query.message,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )

    try:
        ns = await utils.db.getUserNS(query.from_user.id)
    except nsapi.errors.NetSchoolAPIError as e:
        return await utils.edit(
            query.message, e
        )

    kb = pyroboard.InlineKeyboard(1)
    per = (await ns.request("GET", "v2/reports/studenttotal"))['filterSources'][2]
    for i in per['items']:
        if str(i['value']) == "-1":
            continue
        kb.row(types.InlineKeyboardButton(
            text=i['title'],
            callback_data=f"marks_by_d:{i['value']}"
        ))

    await ns.full_logout()
    await utils.edit(
        query.message,
        f"<b>Выберите учебный период</b>",
        reply_markup=kb
    )


@marks.on_callback_query(
    filters.startswith("marks_by_d:")
)
async def getAverageMarksByDiary(client: pyrogram.Client, query: types.CallbackQuery):
    filter_id = query.data.split(":")[1]

    user = utils.db.recvs("SELECT * FROM accounts WHERE id = ?", query.from_user.id)
    if not user:
        return await utils.edit(
            query.message,
            f"🤨 <b>Вы не авторизованы!</b>\n" \
            f"Используйте команду /auth и авторизуйтесь."
        )

    await utils.edit(
        query.message,
        f"<b><u>⚠ ВНИМАНИЕ!</u>\n" \
        f"Это — неофициальный отчёт из Сетевого Города, который берётся путём просматривания всех оценок в дневнике.\n\nПолучение оценок может занять время, пожалуйста, подождите.</b>"
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
            msg, e
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

    kb = pyroboard.InlineKeyboard(1)
    kb.add(types.InlineKeyboardButton(
        text="🔙 Назад", callback_data=f"marks:by_d"
    ))

    if len(msg) > 4096:
        await query.message.delete()
        await utils.answer(
            query.message, msg,
            reply_markup=kb
        )
    else:
        await utils.edit(
            query.message, msg,
            reply_markup=kb
        )