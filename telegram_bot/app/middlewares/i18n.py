"""
Internationalization (i18n) middleware for aiogram 3.x
"""
import gettext
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from babel.support import Translations

from app.config import config


class I18nMiddleware(BaseMiddleware):
    """Middleware for internationalization support."""
    
    def __init__(self, locale_dir: Optional[Path] = None):
        super().__init__()
        self.locale_dir = locale_dir or Path(__file__).parent.parent.parent / "locales"
        self.translations: Dict[str, Translations] = {}
        
        # Load translations
        self._load_translations()
    
    def _load_translations(self):
        """Load all available translations."""
        for locale in config.AVAILABLE_LOCALES:
            try:
                translations = Translations.load(
                    dirname=self.locale_dir,
                    locales=[locale],
                    domain="messages"
                )
                self.translations[locale] = translations
            except Exception as e:
                print(f"Warning: Could not load translation for {locale}: {e}")
                # Create empty translation as fallback
                self.translations[locale] = Translations()
    
    def get_translation(self, locale: str) -> Translations:
        """Get translation for a specific locale."""
        if locale not in self.translations:
            locale = config.DEFAULT_LOCALE
        return self.translations.get(locale, self.translations[config.DEFAULT_LOCALE])
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process the event and set up i18n context."""
        # Get user's language code
        locale = config.DEFAULT_LOCALE
        
        if isinstance(event, Message):
            if event.from_user and event.from_user.language_code:
                user_locale = event.from_user.language_code.split("-")[0]
                if user_locale in config.AVAILABLE_LOCALES:
                    locale = user_locale
            # Store session data for language switching
            data["session"] = event.from_user.id
        
        elif isinstance(event, CallbackQuery):
            if event.from_user and event.from_user.language_code:
                user_locale = event.from_user.language_code.split("-")[0]
                if user_locale in config.AVAILABLE_LOCALES:
                    locale = user_locale
        
        # Set translation in context
        translation = self.get_translation(locale)
        data["_"] = translation.gettext
        data["locale"] = locale
        
        return await handler(event, data)


class FSMContextI18nMiddleware(BaseMiddleware):
    """Middleware to persist user's language choice in FSM context."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process the event and check for stored language preference."""
        from aiogram.fsm.context import FSMContext
        
        if isinstance(event, (Message, CallbackQuery)):
            fsm_context: FSMContext = data.get("state")
            if fsm_context:
                user_data = await fsm_context.get_data()
                if "language" in user_data:
                    data["locale"] = user_data["language"]
                    translation = data.get("_translator", {}).get(
                        user_data["language"], 
                        data.get("_translator", {}).get(config.DEFAULT_LOCALE)
                    )
                    if translation:
                        data["_"] = translation.gettext
        
        return await handler(event, data)


def setup_i18n_middleware(dp):
    """Setup i18n middleware on dispatcher."""
    i18n_middleware = I18nMiddleware()
    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)
    dp.edited_message.middleware(i18n_middleware)
    return i18n_middleware
