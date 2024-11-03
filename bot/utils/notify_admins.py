import logging

from aiogram import Bot

from data.config import ADMINS
from utils.db.postgres import Database

async def on_startup_notify(bot: Bot, db: Database):
    for admin in ADMINS:
        try:
            bot_properties = await bot.me()
            message = ["<b>Bot ishga tushdi.</b>\n",
                       f"<b>Bot ID:</b> {bot_properties.id}",
                       f"<b>Foydalanuvchilar soni:</b> {await db.get_users_count()}",
                       f"<b>Yangi foydalanuvchilar soni(7kunlik):</b> {await db.get_users_count_last_week()}",
                       f"<b> Ijara oluvchilar soni:</b> {await db.get_renters_count()}",
                       f"<b> Ijara beruvchilar soni:</b> {await db.get_landlords_count()}",
                       f"<b> Kvartiralar soni:</b> {await db.get_apartments_count()}"]
            await bot.send_message(int(admin), "\n".join(message))
        except Exception as err:
            logging.exception(err)
