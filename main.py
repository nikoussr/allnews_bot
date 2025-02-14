import asyncio
import logging
from aiogram import Bot, Dispatcher
from configs import TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
from database.db import Database

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot)
db = Database()



async def main():
    await db.connect('postgresql://postgres:postgrespostgres@localhost/allnews')
    await bot.delete_webhook()
    import handlers.start_handler
    dp.include_router(handlers.start_handler.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('EXIT')
