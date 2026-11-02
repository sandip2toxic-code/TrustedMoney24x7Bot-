import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db
from handlers import router as main_router
from promote_handlers import router as promote_router
from app_promote_handlers import router as app_promote_router
from create_bot_handlers import router as create_bot_router
from content_handlers import router as content_router
from admin_handlers import router as admin_router
from admin_content_handlers import router as admin_content_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing! Please check your .env file.")
        return

    await init_db()
    logger.info("Database initialized successfully.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(main_router)
    dp.include_router(promote_router)
    dp.include_router(app_promote_router)
    dp.include_router(create_bot_router)
    dp.include_router(content_router)
    dp.include_router(admin_router)
    dp.include_router(admin_content_router)

    logger.info("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
