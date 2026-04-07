"""
Authentication and admin middleware.
"""
from typing import Any, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.config import config


class AuthMiddleware(BaseMiddleware):
    """Middleware to ensure user is registered in the database."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process the event and ensure user exists in DB."""
        from app.database.repositories import UserRepository
        
        # Get user from event
        user_obj = None
        if isinstance(event, Message):
            user_obj = event.from_user
        elif isinstance(event, CallbackQuery):
            user_obj = event.from_user
        
        if not user_obj:
            return await handler(event, data)
        
        # Get DB session
        session = data.get("session")
        if not session:
            return await handler(event, data)
        
        # Check if user exists
        user_repo = UserRepository(session)
        db_user = await user_repo.get_by_telegram_id(user_obj.id)
        
        if not db_user:
            # Create new user
            referrer_id = None
            # Check for referral in start command args (handled elsewhere)
            
            db_user = await user_repo.create(
                telegram_id=user_obj.id,
                username=user_obj.username,
                first_name=user_obj.first_name,
                last_name=user_obj.last_name,
                language_code=user_obj.language_code or "en",
                referrer_id=referrer_id,
            )
        
        # Store user in context
        data["user"] = db_user
        
        return await handler(event, data)


class AdminMiddleware(BaseMiddleware):
    """Middleware to check if user is an admin."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Check if user is admin before processing."""
        user = data.get("user")
        
        if not user:
            if isinstance(event, (Message, CallbackQuery)):
                await event.answer("Access denied. Admins only.", show_alert=True)
            return
        
        if user.telegram_id not in config.ADMIN_IDS:
            if isinstance(event, Message):
                await event.answer("⛔️ Access denied. Admins only.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔️ Access denied. Admins only.", show_alert=True)
            return
        
        return await handler(event, data)


def setup_auth_middleware(dp):
    """Setup authentication middleware on dispatcher."""
    auth_middleware = AuthMiddleware()
    dp.message.middleware(auth_middleware)
    dp.callback_query.middleware(auth_middleware)
    return auth_middleware
