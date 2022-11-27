from motor.motor_asyncio import AsyncIOMotorClient
from config import DATABASE_URL, DATABASE_NAME
from datetime import datetime
import time 

client = AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]
col = db["users"]


async def get_user(user_id, first_name=None):
    user_id = int(user_id)
    user = await col.find_one({"user_id": user_id})
    if not user:
        res = {
            "user_id": user_id,
            "has_access": False,
            "last_verified": datetime(1970,1,1),
            "access_days":0, # in seconds
            "banned": False,
            'allowed_languages': [],
            'lang':'en'
        }
        await col.insert_one(res)
        user = await col.find_one({"user_id": user_id})
    return user

async def update_user_info(user_id, value:dict, tag="$set"):
    user_id = int(user_id)
    myquery = {"user_id": user_id}
    newvalues = {tag : value }
    await col.update_one(myquery, newvalues)

async def unbanalluser(tag="$set"):
    myquery = {"banned": True}
    newvalues = {"$set" : {"banned": False} }
    await col.update_many(myquery, newvalues)

async def filter_users(dict):
    return col.find(dict)

async def total_users_count():
    return await col.count_documents({})

async def get_all_users():
    return col.find({})

async def delete_user(user_id):
    await col.delete_one({'user_id': int(user_id)})

async def total_users_count():
    return await col.count_documents({})

async def total_premium_users_count():
    return await col.count_documents({"has_access":True, "banned":False})

async def is_user_exist(id):
    user = await col.find_one({'user_id':int(id)})
    return bool(user)

async def is_user_verified(user_id):
    user = await get_user(user_id)
    access_days = datetime.fromtimestamp(time.mktime(user["last_verified"].timetuple()) + user['access_days'])
    return (access_days - datetime.now()).seconds >= 0

async def expiry_date(user_id):
    user = await get_user(user_id)
    access_days = datetime.fromtimestamp(time.mktime(user["last_verified"].timetuple()) + user['access_days'])
    return access_days, int((access_days - datetime.now()).total_seconds())