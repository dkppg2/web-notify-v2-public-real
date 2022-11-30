import os

from dotenv import load_dotenv
load_dotenv()

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Mandatory variables for the bot to start
API_ID = int(os.environ.get("API_ID", "18274091"))
API_HASH = os.environ.get("API_HASH", "97afe4ab12cb99dab4bed25f768f5bbc")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "5664706056:AAF1JNlMEeIX2rCVlgkOQa8EnLU_Qn5uZEs")
OWNER_ID = int(os.environ.get("OWNER_ID", "2109516065"))
DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://abcd:abcd@cluster0.ruawekg.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "Notification")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001637919182"))
BOT_USERNAME = os.environ.get("BOT_USERNAME", "@Notify_Rbot")
BROADCAST_AS_COPY = os.environ.get("BROADCAST_AS_COPY", True)
VALIDITY = [int(i.strip()) for i in os.environ.get("VALIDITY").split(",")] if os.environ.get("VALIDITY") else [3600,86400,432000,604800,1209600,2419200,2627424,5254848,7776000,31536000,63115200,94672800,315576000,631152000,1577880000]
#languages = os.environ.get("TRANSLATION_LANG").replace(r'\n', '\n').split("\n") 
#English, en \n Tamil, ta

TRANSLATION_LANG  = """English,en 
Hindi,hi 
Bengali,bn 
Telugu,te
Tamil,ta
Kannada,kn"""

languages = os.environ.get("TRANSLATION_LANG", TRANSLATION_LANG).replace(r'\n', '\n').split("\n") 

IS_USER_ALLOWED_TO_CHANGE_LANGUAGE = is_enabled(os.environ.get("IS_USER_ALLOWED_TO_CHANGE_LANGUAGE", "True"), False)

#  Replit Config
REPLIT_USERNAME = os.environ.get("REPLIT_USERNAME", None)
REPLIT_APP_NAME = os.environ.get("REPLIT_APP_NAME", None)
REPLIT = f"https://{REPLIT_APP_NAME.lower()}.{REPLIT_USERNAME}.repl.co" if REPLIT_APP_NAME and REPLIT_USERNAME else False
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "300"))

VOOT_API_URL = "https://psapi.voot.com/jio/voot/v1/voot-web/content/generic/series-wise-episode?sort=episode%3Adesc&id={show_id}&responseType=common"
ZEE5_API_URL = "https://gwapi.zee5.com/content/tvshow/{show_id}?translation=en&country=IN"
HOTSTAR_API_URL = "https://api.hotstar.com/o/v1/show/detail?contentId={show_id}"
