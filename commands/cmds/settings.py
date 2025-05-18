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
import pytz

import pyrogram
import pyroboard
from pyrogram import types

import dispatch.fsm
import utils
from dispatch import filters
from dispatch.routing import Router


settings = Router("settings")
logger = logging.getLogger(__name__)


@settings.on_message(
    filters.command(commands=["settings", "настройки"])
    | filters.text("⚙️ Настройки", False)
)
async def setts(client: pyrogram.Client, message: types.Message):
    user = utils.db.getUser(message.from_user.id)
    kb = pyroboard.ReplyKeyboard(2)
    if utils.db.getNSUser(message.from_user.id):
        kb.add(
            types.KeyboardButton(text="🔔 Уведомления")
        )
    kb.row(types.KeyboardButton(text=("🚪 Выйти из аккаунта" if utils.db.getNSUser(message.from_user.id) else "❤️ Войти в аккаунт")))
    kb.row(types.KeyboardButton(text="◀️ Главное меню"))

    await utils.answer(
        message,
        f"👾 <b>Ниже Вы видите настройки, что доступны для изменения. Пожалуйста, выберите нужную:</b>",
        reply_markup=kb
    )



@settings.on_message(
    filters.command(commands=["notifsettings", "настройкиуведомлений"])
    | filters.text("🔔 Уведомления", False)
)
async def sets_notifications(client: pyrogram.Client, message: types.Message):
    await utils.answer(
        message, "👾 <b>Выберите настройку, которую хотите изменить.</b>",
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text="⏰ Рассылка расписания", callback_data="set_schedule_mailing")]
        ])
    )


@settings.on_callback_query(
    filters.startswith("set_schedule_mailing")
)
async def set_schedule_mailing(client: pyrogram.Client, query: types.CallbackQuery):
    user = utils.db.getUser(query.from_user.id)
    if user[2] == 1:
        return await utils.edit(
            query.message,
            f"⏰ <b>Рассылка расписания уже настроена на время {user[3]} (GMT+3, Московское время). Хотите отключить, или настроить другое время?</b>",
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text="Изменить время", callback_data="change_schedule_mailing")],
                [types.InlineKeyboardButton(text="Отключить", callback_data="disable_schedule_mailing")]
            ])
        )

    await utils.edit(
        query.message,
        f"⏰ <b>Пожалуйста, введите время (GMT+3, Московское время), в которое Вам будет удобнее всего получать " \
        f"расписание в этом чате в следующем формате: ЧЧ:ММ</b>\n<b>Например:</b> <code>07:25</code>" \
        f"\n\nДля отмены используйте /cancel",
    )
    await dispatch.fsm.set_state(client, "schedule_mailing_time", query.from_user.id, query.message.chat.id)


@settings.on_message(
    dispatch.fsm.StateFilter("schedule_mailing_time")
)
async def sets_notifications(client: pyrogram.Client, message: types.Message):
    time = message.text

    try: datetime.datetime.strptime(time, "%H:%M")
    except:
        return await utils.answer(
            message,
            f"😔 Вы ввели время в неправильном формате, пожалуйста, попробуйте снова!\n\n⏰ <b>Пожалуйста, введите время (GMT+3, Московское время), в которое Вам будет удобнее всего получать расписание в этом чате в следующем формате: ЧЧ:ММ</b>\n<b>Например:</b> <code>07:25</code>"
        )

    utils.db.save(
        "UPDATE users SET set_mailing_schedule = ?, mailing_schedule_time = ?" \
        ", last_mail_send = ? WHERE id = ?",
        1, time,
        (
            datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))-datetime.timedelta(days=1)
        ).strftime("%d.%m.%Y"),
        message.from_user.id
    )
    await utils.answer(
        message,
        f"⏰ <b>Рассылка расписания установлена на время {time} (GMT+3, Московское время)</b>"
    )


@settings.on_callback_query(
    filters.startswith("change_schedule_mailing")
)
async def change_schedule_mailing(client: pyrogram.Client, query: types.CallbackQuery):
    await utils.edit(
        query.message,
        f"⏰ <b>Пожалуйста, введите время (GMT+3, Московское время), в которое Вам будет удобнее всего получать " \
        f"расписание в этом чате в следующем формате: ЧЧ:ММ</b>\n<b>Например:</b> <code>07:25</code>" \
        f"\n\nДля отмены используйте /cancel",
    )
    await dispatch.fsm.set_state(client, "schedule_mailing_time", query.from_user.id, query.message.chat.id)


@settings.on_callback_query(
    filters.startswith("disable_schedule_mailing")
)
async def disable_schedule_mailing(client: pyrogram.Client, query: types.CallbackQuery):
    await utils.edit(
        query.message,
        f"🤔 <b>Вы уверены, что хотите отключить рассылку расписания?</b>",
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text="Да, отключить", callback_data="fdisable_schedule_mailing")]
        ])
    )


@settings.on_callback_query(
    filters.startswith("fdisable_schedule_mailing")
)
async def disable_schedule_mailing(client: pyrogram.Client, query: types.CallbackQuery):
    utils.db.save(
        "UPDATE users SET set_mailing_schedule = ? WHERE id = ?",
        0, query.from_user.id
    )

    await query.message.delete()
    await utils.answer(
        query.message,
        f"❌ <b>Рассылка была отключена.</b>",
        reply_markup=utils.getMenuKB(query.from_user.id) if query.message.chat.type == pyrogram.enums.chat_type.ChatType.PRIVATE else None
    )