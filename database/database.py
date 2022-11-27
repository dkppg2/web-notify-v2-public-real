from config import DATABASE_NAME, DATABASE_URL, HOTSTAR_API_URL, VOOT_API_URL, ZEE5_API_URL, BOT_USERNAME
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp


class Database:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.misc = self.db['misc']
        self.notify_urls = self.db['notify_urls']

    async def getApiUrl(self, url):
        show_id = url.split("/")[-1]
        if "voot.com" in url:
            headers = {'Host': 'psapi.voot.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0', 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'Referer': 'https://www.voot.com/', 'usertype': 'avod', 'Content-Version': 'V5', 'Origin': 'https://www.voot.com', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site', 'Sec-GPC': '1', 'Connection': 'keep-alive'}
            temp_url = "https://psapi.voot.com/jio/voot/v1/voot-web/content/generic/season-by-show?sort=season%3Adesc&id={}&responseType=common"
            show_id = (await get_response(temp_url.format(show_id), headers=headers))["result"][0]["seasonId"]
            return VOOT_API_URL.format(show_id=show_id)
        elif "zee5.com" in url:
            return ZEE5_API_URL.format(show_id=show_id)

        elif "hotstar.com" in url:
            return HOTSTAR_API_URL.format(show_id=show_id)

    async def get_bot_stats(self):
        return await self.misc.find_one({"bot": BOT_USERNAME})

    async def create_config(self):
        await self.misc.insert_one({
            'bot':BOT_USERNAME,
            'sleep_time': 0,
            'admins': [],
            'banned_users': [],
        })
    
    async def update_stats(self, dict):
        myquery = {"bot": BOT_USERNAME}
        newvalues = {"$set" : dict}
        return await self.misc.update_one(myquery, newvalues)
    
    async def add_notify_url(self, url, lang, domain):
        try:
            notify_url = await self.notify_urls.find_one({"url": url})
            if not notify_url:
                res = {
                    "url": url,
                    "lang": lang,
                    "site": domain,
                    "api_url":await self.getApiUrl(url)
                }
                await self.notify_urls.insert_one(res)
                notify_url = await self.notify_urls.find_one({"url": url})
        except Exception as e:
            print(e)

        return notify_url

    async def delete_notify_url(self, url):
        myquery = {"url": url}
        return await self.notify_urls.delete_one(myquery)

    async def deleteall_notify_url(self):
        return await self.notify_urls.delete_many({})

    async def update_notify_url(self, url, value:dict, tag="$set"):
        myquery = {"url": url}
        newvalues = {tag : value}
        return await self.notify_urls.update_one(myquery, newvalues)

    async def filter_notify_url(self, dict):
        return self.notify_urls.find(dict)
        

db = Database(DATABASE_URL, DATABASE_NAME)

async def get_response(url, headers=None):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, raise_for_status=True) as response:
            return await response.json()