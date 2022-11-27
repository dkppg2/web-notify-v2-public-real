import asyncio
import datetime
import logging
import logging.config

from pyrogram import Client

from config import API_HASH, API_ID, BOT_TOKEN, OWNER_ID, REPLIT, languages
from database import db
from helpers import temp
from utils import notifier, ping_server

# Get logging configurations

logging.getLogger().setLevel(logging.INFO)


if REPLIT:
    from threading import Thread

    from flask import Flask, jsonify
    
    app = Flask('')
    
    @app.route('/')
    def main():
        res = {
            "status":"running",
            "hosted":"replit.com",
            "repl":REPLIT,
        }
        
        return jsonify(res)

    def run():
      app.run(host="0.0.0.0", port=8000)
    
    async def keep_alive():
      server = Thread(target=run)
      server.start()


class Bot(Client):

    def __init__(self):
        super().__init__(
        "Notifier",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")
        )

    async def start(self):
        
        if REPLIT:
            await keep_alive()
            asyncio.create_task(ping_server())
            
        await super().start()
        logging.info('Bot started')

        if not await db.get_bot_stats():
            await db.create_config()

        config = await db.get_bot_stats()

        temp.ADMINS_LIST = config['admins']
        if OWNER_ID not in temp.ADMINS_LIST:
            temp.ADMINS_LIST.append(OWNER_ID)
        temp.SLEEP_TIME = config['sleep_time']
        temp.BANNED_USERS = config['banned_users']
        
        notify_urls = await db.filter_notify_url({})
        async for urls in notify_urls:
            temp.NOTIFY_URLS.append(urls['api_url'])

        for ix in languages:
            lang, code = ix.strip().split(",")
            temp_dic = {code.strip():lang}
            temp.LANG.update(temp_dic)
            
        asyncio.create_task(notifier(self))
        logging.info('Task Created')


    async def stop(self, *args):
        await super().stop()
        logging.info('Bot Stopped Bye')
        
if __name__ == '__main__':
    Bot().run()
