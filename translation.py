import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton



class Script(object):
    START_MESSAGE = os.environ.get("START_MESSAGE", "**Hii ð\n\n I Am a Notification Bot  Made By @CR_0O0 \n Which Can Helps To Give New released Serials Link With in a second \n Avilable OTTs \n [Hotstar](https://hotstar.com) â¤ï¸âð¥ \n [zee5](https://zee5.com) ð \n [voot](https://www.voot.com) ð \n Buy Subscription From @CR_0O0**")
    HELP_MESSAGE = os.environ.get("HELP_MESSAGE", "**For Plans Details Please Contact To @CR_0O0**")
    ABOUT_MESSAGE = os.environ.get("ABOUT_MESSAGE", "**About Me ð¤\n\nBOT NAME  ð¦¾   : [Notification Robot ð](https://telegram.me/Notify_Rbot)\n\nDEVELOPER ð§  : [_Rá´Êá´x_](https://telegram.me/CR_0O0)\n\nMADE BY ð« : PYTHON \n\nOWNED BY  ð£ :  [_Rá´Êá´x_](https://telegram.me/CR_0O0)\n\nHAVE A NICE DAY Bro â¤ï¸**")

    ADD_ADMIN_TEXT = """Current Admins:
{}
Usage: /addadmin id
Ex: `/addadmin 14035272, 14035272`
To remove a admin,
Ex: `/addadmin remove 14035272`
To remove all admins,
Ex: `/addadmin remove_all`
"""

    BANNED_USERS_LIST = """Current Banned Users:
{}
Usage: /ban id
Ex: `/ban 14035272, 14035272`
To remove a banned user,
Ex: `/ban remove 14035272`
To remove all banned user,
Ex: `/ban remove_all`
"""

    NOTIFY_URLS_LIST = """Current Urls Users:
{}
Usage: /add_url id
Ex: `/add_url Kannada https://www.zee5.com/tv-shows/details/vaidehi-parinaya/0-6-4z5173773`
To remove a url,
Ex: `/add_url remove https://www.zee5.com/tv-shows/details/vaidehi-parinaya/0-6-4z5173773`
To remove all urls,
Ex: `/add_url remove_all`
"""

    SUBSCRIPTION_REMINDER_MESSAGE = """**Your subscription is gonna end soon. 
    
Renew your subscription to continue this service contact @CR_0O0:

Details:
User ID: {user_id}

Subscription Date: {subscription_date}

Expiry Date: {expiry_date}

Subscription Peroid Remaining: {time_remaining}

Allowed Languages: {allowed_languages}

Banned: {banned_status}
**"""

    HELP_REPLY_MARKUP = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('plans', callback_data=f'help_command'),
            InlineKeyboardButton('Language', callback_data=f'lang_command'),

        ],

        [
            InlineKeyboardButton('About', callback_data=f'about_command'),
            InlineKeyboardButton('My Plan', callback_data=f'info_command'),    
        ],
        [
            InlineKeyboardButton('Close', callback_data=f'delete'),    
        ],

    ])

    HOME_BUTTON_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('Home', callback_data='start_command')]])

