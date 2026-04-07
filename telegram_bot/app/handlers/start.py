"""
Start command and user registration handler.
"""
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.database.repositories import UserRepository
from app.keyboards import get_main_menu_keyboard, get_language_keyboard
from app.utils import generate_referral_link

router = Router()


@router.message(CommandStart())
async def handle_start(
    message: types.Message,
    state: FSMContext,
    session,
    event_from_user: types.User,
):
    """Handle /start command with optional referral parameter."""
    user_repo = UserRepository(session)
    
    # Check if user exists
    db_user = await user_repo.get_by_telegram_id(event_from_user.id)
    
    # Parse referral ID from start parameters
    args = message.text.split() if message.text else []
    referral_id = None
    
    if len(args) > 1 and args[1].isdigit():
        referral_id = int(args[1])
    
    _ = lambda x: x  # Default translation
    
    if not db_user:
        # Create new user
        if referral_id and referral_id != event_from_user.id:
            # Verify referrer exists
            referrer = await user_repo.get_by_id(referral_id)
            if not referrer:
                referral_id = None
        
        db_user = await user_repo.create(
            telegram_id=event_from_user.id,
            username=event_from_user.username,
            first_name=event_from_user.first_name,
            last_name=event_from_user.last_name,
            language_code=event_from_user.language_code or "en",
            referrer_id=referral_id,
        )
        
        welcome_text = (
            f"👋 Welcome, {event_from_user.first_name}!\n\n"
            f"🎉 You've successfully started the bot.\n\n"
            f"💡 Use the menu below to explore features:\n"
            f"• 💰 Check your balance\n"
            f"• 👥 Invite friends and earn rewards\n"
            f"• 📋 Complete tasks for TON\n"
            f"• 💸 Withdraw your earnings\n\n"
            f"🔔 Don't forget to subscribe to our channel for daily rewards!"
        )
        
        if referral_id:
            welcome_text += f"\n\n✨ You were referred by a friend!"
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard(_),
        )
        
        # Suggest language selection if not English/Russian
        if event_from_user.language_code and not event_from_user.language_code.startswith(('en', 'ru')):
            await message.answer(
                "🌐 Select your preferred language:",
                reply_markup=get_language_keyboard(),
            )
    else:
        # Existing user
        welcome_back_text = (
            f"👋 Welcome back, {event_from_user.first_name}!\n\n"
            f"💰 Your balance: {db_user.balance:.4f} TON\n"
            f"❄️ Frozen: {db_user.frozen_balance:.4f} TON\n\n"
            f"Use the menu below to continue."
        )
        
        await message.answer(
            welcome_back_text,
            reply_markup=get_main_menu_keyboard(_),
        )
    
    # Clear any previous state
    await state.clear()


@router.callback_query(F.data == "main_menu")
async def handle_main_menu(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Handle main menu button press."""
    _ = lambda x: x  # Default translation
    
    text = (
        f"🏠 Main Menu\n\n"
        f"💰 Balance: {user.balance:.4f} TON\n"
        f"❄️ Frozen: {user.frozen_balance:.4f} TON\n"
        f"👥 Referrals: {len(user.referred_users)}\n\n"
        f"Select an option below:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu_keyboard(_),
    )
    await callback.answer()
