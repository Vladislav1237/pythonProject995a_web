"""
Main bot application entry point.
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import config, Config
from app.database import db
from app.middlewares import setup_middlewares
from app.handlers import register_handlers


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Called when bot starts."""
    logger.info("Bot is starting up...")
    
    # Initialize database
    await db.connect()
    logger.info("Database connected.")
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot @{bot_info.username} started successfully!")


async def on_shutdown(bot: Bot):
    """Called when bot shuts down."""
    logger.info("Bot is shutting down...")
    
    # Close database connection
    await db.disconnect()
    logger.info("Database disconnected.")


def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher."""
    dp = Dispatcher()
    
    # Inject database session FIRST (before auth middleware)
    @dp.message.middleware()
    @dp.callback_query.middleware()
    async def inject_session(handler, event, data):
        """Inject database session into handler context."""
        async with db.get_session() as session:
            data["session"] = session
            return await handler(event, data)
    
    # Setup middlewares (auth, i18n, etc.)
    setup_middlewares(dp)
    
    # Register handlers
    register_handlers(dp)
    
    # Register startup/shutdown hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    return dp


async def main():
    """Main function to run the bot."""
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # Create bot instance
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Create dispatcher (includes session injection and middlewares)
    dp = create_dispatcher()
    
    try:
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
