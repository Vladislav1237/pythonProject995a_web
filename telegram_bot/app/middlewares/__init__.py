"""
Middleware initialization.
"""
from aiogram import Dispatcher

from app.middlewares.i18n import setup_i18n_middleware
from app.middlewares.auth import setup_auth_middleware


def setup_middlewares(dp: Dispatcher):
    """Setup all middlewares on dispatcher."""
    # Setup i18n middleware
    setup_i18n_middleware(dp)
    
    # Setup auth middleware
    setup_auth_middleware(dp)
