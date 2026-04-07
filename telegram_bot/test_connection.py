import asyncio
import logging
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import config

logging.basicConfig(level=logging.DEBUG)

async def test():
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        me = await bot.get_me()
        print(f"Bot connected successfully!")
        print(f"Username: @{me.username}")
        print(f"Name: {me.first_name}")
        print(f"ID: {me.id}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test())
