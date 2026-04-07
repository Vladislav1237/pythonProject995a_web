"""
Handler registration module.
"""
from aiogram import Dispatcher

from app.handlers import (
    start,
    balance,
    referral,
    tasks,
    withdraw,
    promo,
    admin,
)


def register_handlers(dp: Dispatcher):
    """Register all handlers with the dispatcher."""
    
    # User handlers
    dp.include_router(start.router)
    dp.include_router(balance.router)
    dp.include_router(referral.router)
    dp.include_router(tasks.router)
    dp.include_router(withdraw.router)
    dp.include_router(promo.router)
    
    # Admin handlers
    dp.include_router(admin.router)
