
import asyncio
import logging
import os

from aiohttp import web

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


async def health_check(request):
    return web.Response(
        text="TrustedMoney24x7Bot is running!",
        status=200
    )


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    port = int(os.environ.get("PORT", 10000))

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=port
    )

    await site.start()

    logger.info("Web server started on port %s", port)

    return runner


async def main():
    if not BOT_TOKEN:
        logger.error(
            "BOT_TOKEN is missing! Please check your .env file."
        )
        return

    await init_db()
    logger.info("Database initialized successfully.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
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

    web_runner = await start_web_server()

    logger.info("Bot is starting...")

    try:
        await dp.start_polling(bot)

    finally:
        logger.info("Stopping bot and web server...")

        await bot.session.close()
        await web_runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Bot stopped.")
        
