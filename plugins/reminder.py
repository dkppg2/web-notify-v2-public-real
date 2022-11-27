
import asyncio
import datetime
import logging
import random
import string
import time
import traceback

import aiofiles
import aiofiles.os
from database.users import (delete_user, expiry_date, filter_users,
                            is_user_verified, total_premium_users_count,
                            update_user_info)
from helpers import human_time, temp
from pyrogram import Client, filters
from pyrogram.errors import (FloodWait, InputUserDeactivated, PeerIdInvalid,
                             UserIsBlocked)
from pyrogram.types import Message
from translation import Script

broadcast_ids = {}

@Client.on_message(filters.command("premium_reminder") & filters.private)
async def reminder_handler(c:Client, m:Message):
    if m.from_user.id not in temp.ADMINS_LIST:
        return 

    try:
        await main_reminder_handler(c, m)
    except Exception as e:
        logging.error("Failed to execute reminder", exc_info=True)


async def send_msg(user_id, msg, client: Client):
    try:
        await client.send_message(user_id, msg)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, msg, client)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


async def main_reminder_handler(client: Client, m: Message):
    all_users = await filter_users({"has_access":True, "banned":False})

    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for _ in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(text="Reminder Message Started Sending to users! You will be notified with log file when all the users are notified.")

    start_time = time.time()
    total_users = await total_premium_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(total=total_users, current=done, failed=failed, success=success)

    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            expiry_date_str, time_remaining = await expiry_date(user["user_id"])

            if time_remaining <= 172800:
                subscription_date = user['last_verified'] if user["has_access"] else None
                if not await is_user_verified(user["user_id"]):
                    await update_user_info(user["user_id"], {"has_access": False})
                    subscription_date = expiry_date_str = time_remaining = "Expired"
                text = Script.SUBSCRIPTION_REMINDER_MESSAGE.format(
                                        user_id=user["user_id"], 
                                        subscription_date=subscription_date, 
                                        expiry_date=expiry_date_str, 
                                        time_remaining=human_time(time_remaining) if type(time_remaining) is int else time_remaining , 
                                        allowed_languages=" ".join(user["allowed_languages"]),
                                        banned_status=user["banned"])
            
                sts, msg = await send_msg(int(user['user_id']), text, client=client)
                if msg is not None:
                    await broadcast_log_file.write(msg)
                if sts == 200:
                    success += 1
                else:
                    failed += 1
                if sts == 400:
                    await delete_user(user['user_id'])
                done += 1
                if broadcast_ids.get(broadcast_id) is None:
                    break
                else:
                    broadcast_ids[broadcast_id].update(dict(current=done, failed=failed, success=success))

    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(text=f"Reminder Notification completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.", quote=True)

    else:
        await m.reply_document(document='broadcast.txt', caption=f"Reminder Notification completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.", quote=True)

    await aiofiles.os.remove('broadcast.txt')
