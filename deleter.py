import asyncio
import sys
from aiogram import Bot
from crontab import CronTab

from config import BOT_TOKEN
from database import del_record, sql_start

bot = Bot(BOT_TOKEN, parse_mode="HTML")
event, user_id = sys.argv[1], int(sys.argv[2])


async def main(chat_id, eventname):
    try:
        sql_start()
        await del_record(chat_id, eventname)
        my_cron = CronTab(user='pazon')
        print(chat_id, eventname)
        await bot.send_message(chat_id=chat_id, text=f'{eventname} started!', parse_mode="HTML")
        my_cron.remove_all(comment=f'{eventname}{chat_id}')
        my_cron.write()
        await bot.close()
    except:
        print('Cannot delete')


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(user_id, event))
        loop.close()
    except Exception as exception:
        print(f'{exception}')
