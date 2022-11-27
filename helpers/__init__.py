import translators as ts
from config import IS_USER_ALLOWED_TO_CHANGE_LANGUAGE, VALIDITY

from database import db, get_user
from pyrogram.types import InlineKeyboardButton

from database.users import expiry_date, is_user_verified, update_user_info
from .human_time import human_time


class temp(object):
    ADMINS_LIST = None
    SLEEP_TIME = None
    BANNED_USERS = []
    NOTIFY_URLS = [] # only links
    ZEE5:dict = {}
    # ZEE5 = {'0-6-4z5173773': '0-1-6z5237151', '0-6-4z5185799': '0-1-6z5236634'}
    COLORS:dict = {}
    HOTSTAR:dict = {} #{'1260026801': 100083286} 
    LANG = {}

async def translate(text, from_language='en', to_language=None):  
    return ts.google(text, from_language=from_language, to_language=to_language) if to_language != from_language else text

def user_allowed_langauage(user, lang):
    return f"Allow {lang} ❌️" if lang not in user['allowed_languages'] else f"Disallow {lang} ✅️"

async def get_user_info_button(user_id):
    user = await get_user(user_id)
    btn = [[InlineKeyboardButton(text=f"Add {human_time(time_in_s)}", callback_data=f'validity#{user_id}#{time_in_s}')] for time_in_s in VALIDITY]
    avl_serial_lang = []
    async for lan in await db.filter_notify_url({}):
        language = lan['lang']
        avl_serial_lang.append(language) if language not in avl_serial_lang else []
    btn.append([InlineKeyboardButton(text=f"{user_allowed_langauage(user, serial_lang)}", callback_data=f'allowlang#{user_id}#{serial_lang}#ident') for serial_lang in avl_serial_lang
    ])
    btn.append([InlineKeyboardButton("Remove from database", callback_data=f"deleteuser#{user_id}")])
    btn.append([InlineKeyboardButton("Remove access", callback_data=f"removeaccess#{user_id}")])
    btn.append([InlineKeyboardButton("Close", callback_data="delete")])
    return btn

def listToString(s):
    # return string
    return " ".join(s)


async def get_user_info_text(user_id):
    txt = """**User ID:** `{user_id}`

**Subscription Date:** `{subscription_date}`

**Expiry Date:** `{expiry_date}`

**Subscription Peroid Remaining:** `{time_remaining}`

Allowed Languages: `{allowed_languages}`

**Banned:** `{banned_status}`
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

    return await translate(text, to_language=(await get_user(user_id))["lang"])

async def get_serial_language(user_id):
    user = await get_user(user_id)
    avl_serial_lang = []
    async for lan in await db.filter_notify_url({}):
        if lan not in avl_serial_lang:
            language = lan['lang']
            avl_serial_lang.append(language) if language not in avl_serial_lang else []

    btn = [[InlineKeyboardButton(text=f"{user_allowed_langauage(user, serial_lang)}", callback_data=f'allowlang#{user_id}#{serial_lang}#serial_lang')] for serial_lang in avl_serial_lang]
    btn.append([InlineKeyboardButton("Close", callback_data="delete")])
    symbol = "❌️" if IS_USER_ALLOWED_TO_CHANGE_LANGUAGE else "✅️"
    text = f'Selected Serial Languages: {" ".join(user["allowed_languages"])} {symbol}'
    return text, btn
