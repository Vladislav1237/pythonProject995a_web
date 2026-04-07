"""
Inline keyboards for the Telegram bot.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard(_) -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=_("💰 Balance"), callback_data="balance")
    builder.button(text=_("👥 Referrals"), callback_data="referrals")
    builder.button(text=_("📋 Tasks"), callback_data="tasks")
    builder.button(text=_("💸 Withdraw"), callback_data="withdraw")
    builder.button(text=_("🎁 Promo Code"), callback_data="promo")
    builder.button(text=_("📊 Statistics"), callback_data="stats")
    
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    
    builder.adjust(1)
    return builder.as_markup()


def get_tasks_keyboard(_) -> InlineKeyboardMarkup:
    """Get tasks menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=_("📝 New Task"), callback_data="task_new")
    builder.button(text=_("📜 My Tasks"), callback_data="task_my")
    builder.button(text=_("🔙 Back"), callback_data="main_menu")
    
    builder.adjust(2, 1)
    return builder.as_markup()


def get_withdraw_keyboard(_) -> InlineKeyboardMarkup:
    """Get withdrawal menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=_("💳 Create Withdrawal"), callback_data="withdraw_create")
    builder.button(text=_("📜 Withdrawal History"), callback_data="withdraw_history")
    builder.button(text=_("🔙 Back"), callback_data="main_menu")
    
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def get_task_review_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Get task review keyboard for admins."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Approve", callback_data=f"task_approve:{task_id}")
    builder.button(text="❌ Reject", callback_data=f"task_reject:{task_id}")
    builder.button(text="🔙 Back to Queue", callback_data="admin_tasks_queue")
    
    builder.adjust(2, 1)
    return builder.as_markup()


def get_withdrawal_action_keyboard(withdrawal_id: int) -> InlineKeyboardMarkup:
    """Get withdrawal action keyboard for admins."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Approve & Pay", callback_data=f"withdraw_approve:{withdrawal_id}")
    builder.button(text="❌ Reject", callback_data=f"withdraw_reject:{withdrawal_id}")
    builder.button(text="🔙 Back to Queue", callback_data="admin_withdrawals_queue")
    
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def get_referral_keyboard(referral_link: str) -> InlineKeyboardMarkup:
    """Get referral share keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=_("📤 Share Link"), url=referral_link)
    builder.button(text=_("🔙 Back"), callback_data="main_menu")
    
    builder.adjust(1, 1)
    return builder.as_markup()


def get_back_keyboard(callback: str = "main_menu") -> InlineKeyboardMarkup:
    """Get simple back keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🔙 Back", callback_data=callback)
    
    return builder.as_markup()


def get_confirm_keyboard(confirm_callback: str, cancel_callback: str) -> InlineKeyboardMarkup:
    """Get confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Confirm", callback_data=confirm_callback)
    builder.button(text="❌ Cancel", callback_data=cancel_callback)
    
    builder.adjust(2)
    return builder.as_markup()


def get_admin_menu_keyboard(_) -> InlineKeyboardMarkup:
    """Get admin panel keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=_("📋 Pending Tasks"), callback_data="admin_tasks_queue")
    builder.button(text=_("💸 Pending Withdrawals"), callback_data="admin_withdrawals_queue")
    builder.button(text=_("🎁 Create Promo Code"), callback_data="admin_promo_create")
    builder.button(text=_("👥 All Users"), callback_data="admin_users")
    builder.button(text=_("🔙 Exit Admin"), callback_data="main_menu")
    
    builder.adjust(2, 2, 1)
    return builder.as_markup()
