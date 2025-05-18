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

import httpx
import logging
import traceback

import pyrogram
import pyroboard
from pyrogram import types

import netschoolapi as nsapi

import utils
import dispatch.fsm
from dispatch import filters
from dispatch.routing import Router


auth = Router("auth")
logger = logging.getLogger(__name__)


# Logging out

@auth.on_message(
    filters.command(commands=["deauth", "logout", "выход", "логаут"])
    | filters.text("🚪 Выйти из аккаунта", False)
)
async def deauth(client: pyrogram.Client, message: types.Message):
    user = utils.db.getNSUser(message.from_user.id)
    if not user:
        return await utils.answer(
            message,
            f"🤨 <b>Вы итак не авторизованы!</b>",
            reply_markup=utils.getMenuKB(message.from_user.id) if message.chat.type == pyrogram.enums.chat_type.ChatType.PRIVATE else None
        )

    await utils.answer(
        message,
        f"🤔 <b>Вы уверены, что хотите выйти из аккаунта?</b>",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton(text="Да, уверен", callback_data=f"force_deauth")
        ]])
    )


@auth.on_callback_query(
    filters.startswith("force_deauth")
)
async def deauth_cb_force(client: pyrogram.Client, query: types.CallbackQuery):
    user = utils.db.getNSUser(query.from_user.id)
    if not user:
        await query.message.delete()
        return await utils.answer(
            query.message,
            f"🤨 <b>Вы итак не авторизованы!</b>",
            reply_markup=utils.getMenuKB(query.from_user.id) if query.message.chat.type == pyrogram.enums.chat_type.ChatType.PRIVATE else None
        )

    utils.db.save("DELETE FROM accounts WHERE id = ?", query.from_user.id)
    await query.message.delete()
    await utils.answer(
        query.message,
        f"🗑 <b>Я успешно забыл данные о Вашем аккаунте!</b>\nЕсли понадоблюсь опять — просто напишите /auth",
        reply_markup=utils.getMenuKB(query.from_user.id) if query.message.chat.type == pyrogram.enums.chat_type.ChatType.PRIVATE else None
    )



# Logging in

@auth.on_message(
    pyrogram.filters.private & (
        filters.command(commands=["auth", "login", "войти", "логин"])
        | filters.text("❤️ Войти в аккаунт", False)
    )
)
async def auth_cmd(client: pyrogram.Client, message: types.Message):
    msg = await utils.answer(
        message,
        f"🕓 <b>Подождите…</b>",
        reply_markup=types.ReplyKeyboardRemove()
    )
    args = utils.get_raw_args(message)
    user = utils.db.getNSUser(message.from_user.id)

    if (user) and ("force" not in args):
        await msg[0].delete()
        return await utils.answer(
            message,
            f"😎 <b>Вы авторизованы под логином <code>{user[4]}</code></b>\n" \
            f"<b>Если Вы хотите пройти процесс авторизации сначала, или войти в другой аккаунт — " \
            f"используйте <code>/auth force</code></b>",
            reply_markup=utils.getMenuKB(message.from_user.id) if message.chat.type == pyrogram.enums.chat_type.ChatType.PRIVATE else None
        )

    regions = utils.split_list(list(utils.regions.keys()), 9)

    kb = pyroboard.InlineKeyboard(row_width=1)
    for region_key in regions[0]:
        kb.row(types.InlineKeyboardButton(
            text=utils.regions[region_key]['name'],
            callback_data=f"choose_region:{region_key}:from_cmd"
        ))
    kb.paginate(len(regions), 1, f"regions:{{number}}:from_cmd")

    await msg[0].delete()
    await utils.answer(
        message,
        f"🤔 <b>Выберите регион</b>\n" \
        f"Если нет Вашего региона — перейдите на последнюю страницу и " \
        f"используйте кнопку <b>«☹ Нет моего региона»</b>.",
        reply_markup=kb
    )



# Choosing region

@auth.on_callback_query(
    filters.startswith("regions:")
)
async def get_regions_list(client: pyrogram.Client, query: types.CallbackQuery):
    from_where = query.data.split(":")[2]
    regions = utils.split_list(list(utils.regions.keys()), 9)
    page = int(query.data.split(":")[1])
    page = page if len(regions) >= page else 1

    kb = pyroboard.InlineKeyboard(row_width=1)
    for region_key in regions[page-1]:
        kb.row(types.InlineKeyboardButton(
            text=utils.regions[region_key]['name'],
            callback_data=f"choose_region:{region_key}:{from_where}"
        ))
    if page == len(regions):
        kb.row(types.InlineKeyboardButton(
            text="☹ Нет моего региона",
            callback_data=f"choose_region:NO_MY_REGION:{from_where}"
        ))
    kb.paginate(len(regions), 1, f"regions:{{number}}:{from_where}")
    
    await utils.edit(
        query.message,
        f"🤔 <b>Выберите регион</b>\n" \
        f"Если нет вашего региона — перейдите на последнюю страницу и " \
        f"используйте кнопку <b>«☹ Нет моего региона»</b>.",
        reply_markup=kb
    )

@auth.on_callback_query(
    filters.startswith("choose_region:")
)
async def get_page_of_regions_list(client: pyrogram.Client, query: types.CallbackQuery):
    from_where = query.data.split(":")[2]
    region_key = query.data.split(":")[1]

    if region_key == "NO_MY_REGION":
        await utils.edit(
            query.message,
            f"🔗 <b>Пожалуйста, пришлите ссылку на Ваш «Сетевой Город».</b>\n" \
            f"Пример: <code>https://sgo.edu-74.ru</code>"
        )
        return await dispatch.fsm.set_state(client, "nsauth:url", query.from_user.id, query.message.chat.id)

    await utils.edit(
        query.message, f"🏘 <b>Введите название школы (минимум 2 символа)</b>"
    )
    await dispatch.fsm.set_state(
        client, "nsauth:school", query.from_user.id, query.message.chat.id,
        {"url": utils.regions[region_key]['url']}
    )



# Getting url (if the required region is not in the proposed list)

@auth.on_message(
    dispatch.fsm.StateFilter("nsauth:url")
)
async def get_url(client: pyrogram.Client, message: types.Message):
    data = message.state_data

    if not utils.check_url(message.text):
        await utils.answer(
            message,
            f"☹️ <b>Я не нашёл в Вашем сообщении ссылку, или она недействительна</b>" \
            f"\nПопробуйте ещё раз, или используйте /cancel для отмены."
        )
        return await dispatch.fsm.set_state(client, "nsauth:url", message.from_user.id, message.chat.id)

    try:
        ns = nsapi.NetSchoolAPI(message.text)
    except:
        await utils.answer(
            message,
            f"☹️ <b>Я не нашёл в Вашем сообщении ссылку, или она недействительна</b>" \
            f"\nПопробуйте ещё раз, или используйте /cancel для отмены."
        )
        return await dispatch.fsm.set_state(client, "nsauth:url", message.from_user.id, message.chat.id)

    data['url'] = message.text

    await ns.close()
    await utils.answer(
        message, f"🏘 <b>Введите название школы (минимум 2 символа)</b>"
    )
    await dispatch.fsm.set_state(
        client, "nsauth:school", message.from_user.id, message.chat.id, data
    )



# Getting school ID

@auth.on_message(
    dispatch.fsm.StateFilter("nsauth:school")
)
async def get_schools_list(client: pyrogram.Client, message: types.Message):
    data = message.state_data

    try:
        ns = nsapi.NetSchoolAPI(data['url'])
        names = message.text.split()
        link = f"schools/search?withAddress=true"
        for i in names:
            link += f"&name={i}"
        logger.warning(link)
        sc = await ns.request(
            "GET", link
        )
    except nsapi.errors.NoResponseFromServer as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return await utils.answer(
            message,
            f"⚠ <b>«Сетевой Город» вернул ошибку: [No Response From Server].</b>"
        )
    except nsapi.errors.AuthError as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        out = f"⚠ <b>«Сетевой Город» вернул ошибку авторизации.</b>"
        if e:
            out = f"⚠ <b>«Сетевой Город» вернул ошибку авторизации</b>" \
                  f"<pre language=\"error\">{e}</pre>"
        return await utils.answer(
            message, out
        )
    except httpx.HTTPStatusError as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        out = f"⚠ <b>«Сетевой Город» вернул неизвестную ошибку.</b>"
        if e:
            out = f"⚠ <b>«Сетевой Город» вернул неизвестную ошибку</b>" \
                  f"<pre language=\"error\">{e}</pre>"
        return await utils.answer(
            message, out
        )
    except httpx.ConnectTimeout as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        out = f"⚠ <b>«Сетевой Город» вернул неизвестную ошибку.</b>"
        if e:
            out = f"⚠ <b>«Сетевой Город» вернул неизвестную ошибку</b>" \
                  f"<pre language=\"error\">{e}</pre>"
        return await utils.answer(
            message, out
        )
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        out = f"⚠ <b>«Сетевой Город» вернул неизвестную ошибку.</b>"
        if e:
            out = f"⚠ <b>«Сетевой Город» вернул неизвестную ошибку</b>" \
                  f"<pre language=\"error\">{e}</pre>"
        return await utils.answer(
            message, out
        )

    if len(sc) == 0:
        await utils.answer(message, f"☹ Я не смог найти эту школу, попробуйте ещё раз")
        return await dispatch.fsm.set_state(
            client, "nsauth:school", message.from_user.id, message.chat.id, data
        )

    schools = []
    for i in sc:
        schools.append({"id": str(i['id']), "name": i['shortName']})
    ss = utils.split_list(schools, 9)

    kb = pyroboard.InlineKeyboard(1)
    for i in ss[0]:
        kb.row(types.InlineKeyboardButton(
            text=i['name'],
            callback_data=f"school:{i['id']}"
        ))
    if len(ss) > 1:
        kb.paginate(len(ss), 1, "qschool:{number}")

    data['allschools'] = schools
    await dispatch.fsm.set_state(
        client, "nsauth:choose_school", message.from_user.id, message.chat.id, data
    )
    await utils.answer(
        message,
        f"🏫 <b>Выберите школу из списка ниже</b> <i>(1/{len(ss)})</i>",
        reply_markup=kb
    )


@auth.on_callback_query(
    filters.startswith("qschool:", False)
    & dispatch.fsm.StateFilter("nsauth:choose_school")
)
async def get_page_of_schools_list(client: pyrogram.Client, query: types.CallbackQuery):
    data = query.state_data
    page = int(query.data.split(":")[1])

    schools = data['allschools']
    ss = utils.split_list(schools, 9)

    kb = pyroboard.InlineKeyboard(1)
    for i in ss[page-1 if len(ss) >= page else 0]:
        kb.row(types.InlineKeyboardButton(
            text=i['name'],
            callback_data=f"school:{i['id']}"
        ))
    if len(ss) > 1:
        kb.paginate(len(ss), page if len(ss) >= page else 1, "qschool:{number}")

    data['allschools'] = schools
    await utils.edit(
        query.message,
        f"🏫 <b>Выберите школу из списка ниже</b> <i>(1/{len(ss)})</i>",
        reply_markup=kb
    )
    await dispatch.fsm.set_state(
        client, "nsauth:choose_school", query.from_user.id, query.message.chat.id, data
    )


@auth.on_callback_query(
    filters.startswith("school:")
    & dispatch.fsm.StateFilter("nsauth:choose_school")
)
async def auth_get_school_id(client: pyrogram.Client, query: types.CallbackQuery):
    data = query.state_data
    school_id = int(query.data.split(":")[1])
    data['school_id'] = school_id

    await utils.edit(
        query.message,
        f"🤫 <b>Отправьте мне Ваш логин от «Сетевого Города»</b>"
    )
    await dispatch.fsm.set_state(
        client, "nsauth:get_login", query.from_user.id, query.message.chat.id, data
    )



# Getting login

@auth.on_message(
    dispatch.fsm.StateFilter("nsauth:get_login")
)
async def get_login(client: pyrogram.Client, message: types.Message):
    data = message.state_data
    data['login'] = message.text

    await message.delete()
    await utils.answer(
        message,
        f"🔑 <b>Отлично, теперь отправьте мне Ваш пароль от «Сетевого Города»</b>"
    )
    await dispatch.fsm.set_state(
        client, "nsauth:get_passwd", message.from_user.id, message.chat.id, data
    )



# Getting password

@auth.on_message(
    dispatch.fsm.StateFilter("nsauth:get_passwd")
)
async def get_password(client: pyrogram.Client, message: types.Message):
    data = message.state_data
    data['password'] = message.text
    await message.delete()

    try:
        ns = nsapi.NetSchoolAPI(data['url'])
        await ns.login(
            user_name=data['login'], password=data['password'],
            school_name_or_id=data['school_id']
        )
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return await utils.answer(
            message,
            f"☹️ <b>Не удалось авторизоваться</b>\n" \
            f"Попробуйте использовать команду /auth снова, или попробуйте позже",
            reply=False
        )

    user = utils.db.getNSUser(message.from_user.id)
    if not user:
        utils.db.save(
            "INSERT INTO accounts (id, ns_id, ns_url, ns_school_id, " \
            "ns_login, ns_password) VALUES (?, ?, ?, ?, ?, ?)",
            message.from_user.id, ns._student_id, data['url'],
            data['school_id'], data['login'], data['password']
        )
    else:
        utils.db.save(
            "UPDATE accounts SET ns_id = ?, ns_url = ?, ns_school_id = ?, ns_login = ?, " \
            "ns_password= ? WHERE id = ?",
            ns._student_id, data['url'], data['school_id'], data['login'], data['password'],
            message.from_user.id
        )

    await utils.answer(
        message,
        f"😎 <b>Отлично! Вы вошли с логином</b> <code>{ns._login_data[0]}</code>",
        reply=False, reply_markup=utils.getMenuKB(message.from_user.id) if message.chat.type == pyrogram.enums.chat_type.ChatType.PRIVATE else None
    )
    await ns.full_logout()