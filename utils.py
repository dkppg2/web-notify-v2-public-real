import asyncio
import logging
import traceback
from pyrogram import Client
import aiohttp
from config import OWNER_ID, PING_INTERVAL, REPLIT
import requests
from bs4 import BeautifulSoup
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging.config
from database.users import filter_users
from database import db
from slugify import slugify

from helpers import temp
logging.getLogger().setLevel(logging.INFO)

headers = {'Host': 'gwapi.zee5.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0', 'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'Referer': 'https://www.zee5.com/', 'x-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9kdWN0X2NvZGUiOiJ6ZWU1QDk3NSIsInBsYXRmb3JtX2NvZGUiOiJXZWJAJCF0Mzg3MTIiLCJpc3N1ZWRBdCI6IjIwMjItMTAtMDRUMjA6MTQ6MzMuNzEzWiIsInR0bCI6ODY0MDAwMDAsImlhdCI6MTY2NDkxNDQ3M30.0siprWCgg7fKNhT8O8LC32zvTvUZVatXlZ1aHNvwDw8', 'Origin': 'https://www.zee5.com', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site', 'Sec-GPC': '1', 'Connection': 'keep-alive'}

async def ping_server():
    sleep_time = PING_INTERVAL
    while True:
        await asyncio.sleep(sleep_time)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(REPLIT) as resp:
                    logging.info(f"Pinged server with response: {resp.status}")
        except TimeoutError:
            logging.warning("Couldn't connect to the site URL..!")
        except Exception:
            traceback.print_exc()

async def notifier(client: Client):
    sleep_time = temp.SLEEP_TIME
    while True:
        # print(f"Hostar {temp.HOTSTAR}\n\n")
        await asyncio.sleep(sleep_time)
        try:
            for url in temp.NOTIFY_URLS:
                image_url = ""
                msg = ""
                episode_url = ""
                if "zee5.com" in url:
                    try:
                        changed_content = await zee5_link_handler(url)
                        if changed_content:
                            await client.send_message(OWNER_ID, "Changes detected in Zee5")
                            title = changed_content['title']
                            slug = changed_content['web_url']
                            _url = episode_url = f'https://www.zee5.com/{slug}'
                            image_url = changed_content['image_url'].replace("270x152", "1440x810")
                            msg = f'**Title: {title}\nLink: {_url}**'
                    except Exception as e:
                        logging.exception(e, exc_info=True)

                elif "voot.com" in url:
                    changed_content = await voot_link_handler(url)
                    if changed_content:
                        await client.send_message(OWNER_ID, "Changes detected in Voot")
                        title = changed_content['fullTitle']
                        _url = episode_url = changed_content['slug']
                        image_url = f"http://v3img.voot.com/{changed_content['showImage']}"
                        msg = f'**Title: {title}\nLink: {_url}**'


                elif "hotstar.com" in url:
                    changed_content = await hotstar_link_handler(url)
                    if changed_content:
                        await client.send_message(OWNER_ID, "Changes detected in Hotstar")
                        title = changed_content['title']
                        show_name:str = slugify(changed_content["showName"])
                        _url = episode_url = f"https://www.hotstar.com/in/tv/{show_name}/{changed_content['showContentId']}/{changed_content['contentId']}"
                        image_url = f"https://img1.hotstarext.com/image/upload/{changed_content['images']['h']}"
                        msg = f'**Title: {title}\nLink: {_url}**'

                if bool(image_url and msg and episode_url):
                    share_url = "https://telegram.me/share/url?url={}"
                    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Share', url=share_url.format(episode_url)),]])

                    await serial_broadcast(client=client, serial_url=url, image_url=image_url, caption=msg, reply_markup=reply_markup)
                    admin_list = temp.ADMINS_LIST
                    # await client.send_photo(OWNER_ID, photo=image_url, caption=msg, reply_markup=reply_markup)
                    # for admin_id in admin_list:
                    #     await client.send_photo(admin_id, photo=image_url, caption=msg, reply_markup=reply_markup)

        except Exception as e:
            logging.exception(e, exc_info=True)

async def voot_link_handler(url):
    headers = {'Host': 'psapi.voot.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0', 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'Referer': 'https://www.voot.com/', 'usertype': 'avod', 'Content-Version': 'V5', 'Origin': 'https://www.voot.com', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site', 'Sec-GPC': '1', 'Connection': 'keep-alive'}
    res = (await get_response(url, headers=headers))["result"][0]
    if old_values := temp.COLORS.get(res['showId'], None):
        old_id = old_values
        new_id = res['id']
        if new_id != old_id:
            temp.COLORS[res['showId']] = res['id']
            return res
        else:
            temp.COLORS[res['showId']] = new_id
    else:
        temp.COLORS[res['showId']] = res['id']
    return None

async def zee5_link_handler(url):
    res = (await get_response(url, headers=headers))["seasons"][0]['episodes'][0]
    if old_values := temp.ZEE5.get(res['tvshow']['id'], None):
        old_id = old_values
        new_id = res['id']
        if new_id != old_id:
            temp.ZEE5[res['tvshow']['id']] = res['id']
            return res
        else:
            temp.ZEE5[res['tvshow']['id']] = new_id
    else:
        temp.ZEE5[res['tvshow']['id']] = res['id']
    return []

async def hotstar_link_handler(url):
    try:
        headers= {'User-Agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:107.0) Gecko/20100101 Firefox/107.0', 'Accept': ' */*', 'Accept-Language': ' eng', 'Accept-Encoding': ' gzip, deflate, br', 'Referer': ' https://www.hotstar.com/', 'x-country-code': ' IN', 'x-platform-code': ' PCTV', 'x-client-code': ' LR', 'hotstarauth': ' st=1669222094~exp=1669228094~acl=/*~hmac=47eefd6950b2da45cfddeaba7db97cf32767ab1fa60cf17a96546a021c00909b', 'x-hs-usertoken': ' eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1bV9hY2Nlc3MiLCJleHAiOjE2Njk2MzY0NzMsImlhdCI6MTY2OTAzMTY3MywiaXNzIjoiVFMiLCJqdGkiOiIwYTkwYThlMGNmODE0YWQ1OWU5ODU4NzYzZjExYWNlZiIsInN1YiI6IntcImhJZFwiOlwiODk2MTU0NDVmZmVkNDVlM2FiYzY4NjFiZWIxMjAxZWZcIixcInBJZFwiOlwiMzQwNDBhN2E4MmRmNDJmN2EzM2MxMTBmZmM5ZjIyMmFcIixcIm5hbWVcIjpcIkd1ZXN0IFVzZXJcIixcImlwXCI6XCIxMTAuNDQuMTAuMjA0XCIsXCJjb3VudHJ5Q29kZVwiOlwiaW5cIixcImN1c3RvbWVyVHlwZVwiOlwibnVcIixcInR5cGVcIjpcImd1ZXN0XCIsXCJpc0VtYWlsVmVyaWZpZWRcIjpmYWxzZSxcImlzUGhvbmVWZXJpZmllZFwiOmZhbHNlLFwiZGV2aWNlSWRcIjpcIjg3M2ZkOGFjLWI2MzctNDAyNy04ZjMwLTc1NTZkMjhhZGMyMFwiLFwicHJvZmlsZVwiOlwiQURVTFRcIixcInZlcnNpb25cIjpcInYyXCIsXCJzdWJzY3JpcHRpb25zXCI6e1wiaW5cIjp7fX0sXCJpc3N1ZWRBdFwiOjE2NjkwMzE2NzM0MjN9IiwidmVyc2lvbiI6IjFfMCJ9.9WzjEvitAecX2qOct9gvSM-T7mimFymo3b-D7_C2_pM', 'Origin': ' https://www.hotstar.com', 'Connection': ' keep-alive', 'Sec-Fetch-Dest': ' empty', 'Sec-Fetch-Mode': ' cors', 'Sec-Fetch-Site': ' same-site', 'Sec-GPC': ' 1', 'TE': ' trailers'}

        org_res = (await get_response(url, headers=headers))

        try:
            res = org_res["body"]["results"]['trays']["items"][0]["assets"]["items"][0]
        except KeyError:
            res = org_res["body"]["results"]["trays"]["items"][1]["assets"]["items"][0]

        if old_values := temp.HOTSTAR.get(res['showContentId'], None):
            old_id = old_values
            new_id = res['contentId']
            if new_id != old_id:
                temp.HOTSTAR[res['showContentId']] = res['contentId']
                return res
            else:
                temp.HOTSTAR[res['showContentId']] = new_id
        else:
            temp.HOTSTAR[res['showContentId']] = res['contentId']
        return []
    except Exception as e:
        logging.error(e, exc_info=True)
        
async def get_response(url, headers=None):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, raise_for_status=True) as response:
            return await response.json()

async def get_soup(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'
    }
    html_content = requests.get(url, headers=headers).content
    return BeautifulSoup(html_content, 'html.parser')


async def serial_broadcast(client: Client, serial_url, image_url, caption, reply_markup=None):
    users = await filter_users({"has_access":True, "banned":False})
    async for user in users:
        notify_url = await db.filter_notify_url({"api_url": serial_url})
        async for url in notify_url:
            if url["lang"] in user["allowed_languages"]:
                try:
                    await client.send_photo(user['user_id'], image_url, caption, reply_markup=reply_markup)
                except Exception as e:
                    print(e)
