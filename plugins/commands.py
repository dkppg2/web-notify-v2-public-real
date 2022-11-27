import contextlib
from pyrogram import Client, filters
from config import IS_USER_ALLOWED_TO_CHANGE_LANGUAGE, LOG_CHANNEL, OWNER_ID
from database.users import expiry_date, filter_users, get_user, is_user_exist, is_user_verified, unbanalluser, update_user_info
from helpers import get_serial_language, get_user_info_button, get_user_info_text, temp, translate, user_allowed_langauage
from helpers.human_time import human_time
from translation import Script
from pyrogram.types import Message
from database import db
from urllib.parse import urlparse
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("start") & filters.private)
async def start(bot: Client, cmd: Message):
    txt = await cmd.reply("`Processing...`")
    is_user = await is_user_exist(cmd.from_user.id)
    if not is_user and LOG_CHANNEL: await bot.send_message(LOG_CHANNEL, f"#NewUser\n\nUser ID: `{cmd.from_user.id}`\nName: {cmd.from_user.mention}")
    user = await get_user(cmd.from_user.id)
    text = await translate(Script.START_MESSAGE, to_language=user['lang'])
    return await txt.edit(text, reply_markup=Script.HELP_REPLY_MARKUP, disable_web_page_preview=True)

@Client.on_message(filters.command("help") & filters.private)
async def help(bot: Client, cmd):
    txt = await cmd.reply("`Processing...`")
    user = await get_user(cmd.from_user.id)
    text = await translate(Script.HELP_MESSAGE, to_language=user['lang'])
    return await txt.edit(text, reply_markup=Script.HOME_BUTTON_MARKUP)

@Client.on_message(filters.command("about") & filters.private)
async def about(bot: Client, cmd):
    if Script.ABOUT_MESSAGE:
        txt = await cmd.reply("`Processing...`")
        user = await get_user(cmd.from_user.id)
        text = await translate(Script.ABOUT_MESSAGE, to_language=user['lang'])
        return await txt.edit(text, reply_markup=Script.HOME_BUTTON_MARKUP)

@Client.on_message(filters.command('addadmin') & filters.private)
async def addadmin_handler(bot, m: Message):
    if m.from_user.id != OWNER_ID:
        return

    config = await db.get_bot_stats()
    admin_list = config["admins"]
    tdl = ""
    if admin_list:
        for i in admin_list:
            tdl += f"- `{i}`\n"
    else:
        tdl = "None\n"
    if len(m.command) == 1:
        return await m.reply(Script.ADD_ADMIN_TEXT.format(tdl))
    try:
        cmd = m.command
        cmd.remove('addadmin')
        if "remove_all" in cmd:
            admin_list_new = []
        elif "remove" in cmd:
            cmd.remove('remove')
            admin_list_cmd = [int(x) for x in "".join(cmd).strip().split(",")] 

            for i in list(admin_list_cmd):
                with contextlib.suppress(Exception):
                    admin_list.remove(i)
            admin_list_new = list(set(list(admin_list)))
        else:
            admin_list_cmd = [int(x) for x in "".join(cmd).strip().split(",")] 
            admin_list_new = list(set(admin_list_cmd + list(admin_list)))

        await db.update_stats({"admins": admin_list_new})
        temp.ADMINS_LIST = admin_list_new
        return await m.reply("Updated admin list successfully")
    except Exception as e:
        print(e)
        return await m.reply("Some error updating admin list")

@Client.on_message(filters.command('sleep') & filters.private)
async def sleeptime_handler(bot, m: Message):
    if m.from_user.id not in temp.ADMINS_LIST:
        return
    if len(m.command) != 2:
        return await m.reply(f"`/sleep 5`\n\nCurrent Sleep time: {temp.SLEEP_TIME} seconds")

    sleep_time = int(m.command[1])
    await db.update_stats({'sleep_time': sleep_time})
    temp.SLEEP_TIME = sleep_time
    return await m.reply(f"Sleep time: {sleep_time} seconds Updated")


@Client.on_message(filters.command('ban') & filters.private)
async def banneduser_handler(bot, m: Message):
    if m.from_user.id not in temp.ADMINS_LIST:
        return
    config = await db.get_bot_stats()
    tdl = ""
    if banned_user_list := config["banned_users"]:
        for i in banned_user_list:
            tdl += f"- `{i}`\n"
    else:
        tdl = "None\n"
    if len(m.command) == 1:
        return await m.reply(Script.BANNED_USERS_LIST.format(tdl))
    try:
        cmd = m.command
        cmd.remove('ban')
        if "remove_all" in cmd:
            banned_user_list_new = []
            await unbanalluser()

        elif "remove" in cmd:
            cmd.remove('remove')
            banned_user_cmd = [int(x) for x in "".join(cmd).strip().split(",")] 

            for i in list(banned_user_cmd):
                with contextlib.suppress(Exception):
                    await update_user_info(i, {'banned':False})
                    banned_user_list.remove(i)

            banned_user_list_new = list(set(list(banned_user_list)))
        else:
            banned_user_list_cmd = [int(x) for x in "".join(cmd).strip().split(",")] 
            for user in banned_user_list_cmd:
                await update_user_info(user, {'banned':True})

            banned_user_list_new = list(set(banned_user_list_cmd + list(banned_user_list)))

        await db.update_stats({"banned_users": banned_user_list_new})
        temp.BANNED_USERS = banned_user_list_new
        return await m.reply("Updated banned user list successfully")
    except Exception as e:
        print(e)
        return await m.reply("Some error updating banned user list")

@Client.on_message(filters.command('add_url') & filters.private)
async def addurls_handler(bot, m: Message):

    if m.from_user.id not in temp.ADMINS_LIST:
        return

    config = await db.filter_notify_url({})
    tdl = ""
    async for content in config:
        tdl += f"- `{content['url']}` - {content['lang']}\n\n"
        if len(tdl) > 4000 and len(m.command) == 1:
            await m.reply(tdl)
            tdl = ""

    if len(m.command) == 1:
        return await m.reply(tdl)
    
    try:
        cmd = m.command
        cmd.remove('add_url')

        if "remove_all" in cmd:
            notify_urls_list_new = []
            await db.deleteall_notify_url()

        elif "remove" in cmd:
            cmd.remove('remove')
            notify_urls_cmd = cmd[0]
            await db.delete_notify_url(notify_urls_cmd)
            
        else:
            langauge = cmd[0]
            url = cmd[1]
            domain = urlparse(url).netloc
            await db.add_notify_url(url, langauge, domain)

        notify_urls = await db.filter_notify_url({})
        notify_urls_list_new = []
        async for content in notify_urls:
            notify_urls_list_new.append(content['api_url'])

        temp.NOTIFY_URLS = notify_urls_list_new
        return await m.reply("Updated urls list successfully")
        
    except Exception as e:
        print(e)
        return await m.reply("Some error updating urls list")

@Client.on_message(filters.command('lang') & filters.private)
async def lang_cmd_handler(bot, m: Message):
    btn = [
        [
            InlineKeyboardButton(
                text=f"{temp.LANG[lan]}", callback_data=f'changelang#{m.from_user.id}#{lan}#{temp.LANG[lan]}'
            ),
        ]
        for lan in temp.LANG
    ]
    reply_markup = InlineKeyboardMarkup(btn)
    user = await get_user(m.from_user.id)
    await m.reply_text(f"Choose your language\nCurrent Language: {temp.LANG[user['lang']]}", reply_markup=reply_markup)

@Client.on_message(filters.command('myplan') & filters.private)
async def info_cmd_handler(bot, m: Message):
    if len(m.command) == 1 and m.from_user.id in temp.ADMINS_LIST:
        return await m.reply_text("`/myplan id`")
    user_id = m.command[1] if m.from_user.id in temp.ADMINS_LIST else m.from_user.id
    
    btn = await get_user_info_button(user_id)
    text = await get_user_info_text(user_id)
    await m.reply(text, reply_markup=InlineKeyboardMarkup(btn) if m.from_user.id in temp.ADMINS_LIST else None)

@Client.on_message(filters.command('premium_users') & filters.private)
async def premium_users_cmd(bot: Client, m: Message):
    if m.from_user.id not in temp.ADMINS_LIST:
        return

    premium_users = await filter_users({"has_access":True, "banned":False})
    text = "List of premium users\n\n"
    bin_text = ""
    async for user in premium_users:
        if await is_user_verified(user["user_id"]) or user["has_access"] == False:
            tg_user = await bot.get_users(user["user_id"])
            bin_text += "- `{user_id}` {user_link}\n".format(user_id=user["user_id"], user_link=tg_user.mention)
    bin_text = bin_text or "None"
    await m.reply(text+bin_text)

@Client.on_message(filters.command('serial_lang') & filters.private)
async def serial_lang_cmd(bot, m: Message):
    if not IS_USER_ALLOWED_TO_CHANGE_LANGUAGE:
        return
    text, btn = await get_serial_language(m.from_user.id)
    await m.reply(text, reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.command('id') & filters.private)
async def id_cmd(bot, m: Message):
    return await m.reply(f"Chat: {m.from_user.first_name}\nID: `{m.from_user.id}`")