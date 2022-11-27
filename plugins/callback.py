from datetime import datetime
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, CallbackQuery)
from pyrogram import Client, filters
from config import IS_USER_ALLOWED_TO_CHANGE_LANGUAGE

from database.users import delete_user, expiry_date, get_user, is_user_verified, update_user_info
from helpers import get_serial_language, get_user_info_button, get_user_info_text, human_time, temp, translate, user_allowed_langauage
from translation import Script
from database import db 

@Client.on_callback_query(filters.regex('^changelang'))
async def changelang_cb(c, m: CallbackQuery):
    _, user_id, lang_code, lan = m.data.split("#")
    await update_user_info(int(user_id), {"lang": lang_code})
    await m.edit_message_text(f"Language changed successfully to {lan}")

@Client.on_callback_query(filters.regex('^validity'))
async def change_validity_cb(c, m: CallbackQuery):
    _, user_id, time_in_s = m.data.split("#")
    await update_user_info(user_id, {"has_access":True, "access_days":int(time_in_s), "last_verified":datetime.now()})
    text = await get_user_info_text(user_id)
    await m.edit_message_text(text, reply_markup=m.message.reply_markup)
    await m.answer("Updated Successfully", show_alert=True)

@Client.on_callback_query(filters.regex('^deleteuser'))
async def deleteuser_cb(c, m: CallbackQuery):
    _, user_id = m.data.split("#")
    user_id = int(user_id)
    await delete_user(user_id=user_id)
    await m.answer("User deleted successfully", show_alert=True)

@Client.on_callback_query(filters.regex('^removeaccess'))
async def removeaccess_cb(c, m: CallbackQuery):
    _, user_id = m.data.split("#")
    user_id = int(user_id)
    await update_user_info(user_id=user_id, value={"has_access": False,"last_verified":datetime(1970,1,1), "access_days":0})
    text = await get_user_info_text(user_id)
    await m.edit_message_text(text, reply_markup=m.message.reply_markup)
    await m.answer("Access has been removed", show_alert=True)

@Client.on_callback_query(filters.regex('^allowlang'))
async def allowlang_cb(c, m: CallbackQuery):
    _, user_id, serial_lang, ident = m.data.split("#")
    user = await get_user(user_id)
    allowed_lang = user['allowed_languages']

    if serial_lang in allowed_lang:
        allowed_lang.remove(serial_lang)
    else:
        allowed_lang.append(serial_lang) if serial_lang not in allowed_lang else allowed_lang

    await update_user_info(user_id, {"allowed_languages":allowed_lang})
    
    if ident == "serial_lang":
        text, btn = await get_serial_language(user_id)
        await m.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btn))
        return 

    btn = await get_user_info_button(user_id)
    text = await get_user_info_text(user_id)
    await m.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btn))
    await m.answer("Updated Successfully", show_alert=True)

@Client.on_callback_query(filters.regex('^delete$'))
async def delete_cb(c, m: CallbackQuery):
    await m.message.delete()
    return 

@Client.on_callback_query(filters.regex('^start_command$'))
async def start_command_cb(c, m: CallbackQuery):
    user = await get_user(m.from_user.id)
    text = await translate(Script.START_MESSAGE, to_language=user['lang'])
    await m.message.edit(text, reply_markup=Script.HELP_REPLY_MARKUP)

@Client.on_callback_query(filters.regex('^help_command$'))
async def help_command_cb(c, m: CallbackQuery):
    user = await get_user(m.from_user.id)
    text = await translate(Script.HELP_MESSAGE, to_language=user['lang'])
    await m.message.edit(text, reply_markup=Script.HOME_BUTTON_MARKUP)

@Client.on_callback_query(filters.regex('^about_command$'))
async def about_command_cb(c, m: CallbackQuery):
    user = await get_user(m.from_user.id)
    text = await translate(Script.ABOUT_MESSAGE, to_language=user['lang'])
    await m.message.edit(text, reply_markup=Script.HOME_BUTTON_MARKUP)

@Client.on_callback_query(filters.regex('^lang_command$'))
async def lang_command_cb(c, m: CallbackQuery):
    btn = [
        [
            InlineKeyboardButton(
                text=f"{temp.LANG[lan]}", callback_data=f'changelang#{m.from_user.id}#{lan}#{temp.LANG[lan]}'
            ),
        ]
        for lan in temp.LANG
    ]
    btn.append([InlineKeyboardButton('Home', callback_data='start_command')])
    reply_markup = InlineKeyboardMarkup(btn)
    user = await get_user(m.from_user.id)
    await m.edit_message_text(f"Choose your language\nCurrent Language: {temp.LANG[user['lang']]}", reply_markup=reply_markup)


@Client.on_callback_query(filters.regex('^info_command$'))
async def info_command_cb(c, m: CallbackQuery):
    user_id =  m.from_user.id
    txt = """User ID: {user_id}
Subscription Date: {subscription_date}
Expiry Date: {expiry_date}
Subscription Peroid Remaining: {time_remaining}
Allowed Languages: {allowed_languages}
Banned: {banned_status}
    """

    user = await get_user(user_id)
    btn = await get_user_info_button(user_id)
    expiry_date_str, time_remaining = await expiry_date(user_id)
    subscription_date = user['last_verified'] if user["has_access"] else None

    if user["has_access"] == False or not await is_user_verified(user_id):
        await update_user_info(user_id, {"has_access": False})
        subscription_date = expiry_date_str = time_remaining = "Expired"

    text = txt.format(
        user_id=user_id, 
        subscription_date=subscription_date, 
        expiry_date=expiry_date_str, 
        time_remaining=human_time(time_remaining) if type(time_remaining) is int else time_remaining , 
        allowed_languages=" ".join(user["allowed_languages"]),
        banned_status=user["banned"]
        )
    text = await translate(text, to_language=user['lang'])
    await m.edit_message_text(text, reply_markup=Script.HOME_BUTTON_MARKUP)