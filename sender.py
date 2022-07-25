import asyncio
import sys
from aiogram import Bot
from config import BOT_TOKEN

bot = Bot(BOT_TOKEN, parse_mode="HTML")
chat_to_send, text_to_send = int(sys.argv[1]), sys.argv[2]


async def main(chat_id, text: str):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
    await bot.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(chat_id=chat_to_send, text=text_to_send))
        loop.close()
    except Exception as exception:
        print(f'{exception}')
