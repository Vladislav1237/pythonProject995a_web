"""
Promo code system handlers.
"""
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.database.repositories import PromoCodeRepository, UserRepository
from app.keyboards import get_back_keyboard
from app.utils import format_balance

router = Router()


class PromoStates:
    """FSM states for promo code."""
    waiting_for_code = "promo_waiting_for_code"


@router.callback_query(F.data == "promo")
async def handle_promo_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    """Show promo code menu."""
    _ = lambda x: x
    
    await callback.message.edit_text(
        "🎁 Promo Code\n\n"
        "Enter your promo code to receive a reward:\n\n"
        "💡 Promo codes are case-insensitive.",
        reply_markup=get_back_keyboard(),
    )
    
    await state.set_state(PromoStates.waiting_for_code)
    await callback.answer()


@router.message(StateFilter(PromoStates.waiting_for_code))
async def process_promo_code(
    message: types.Message,
    state: FSMContext,
    session,
    user,
):
    """Process promo code input."""
    from datetime import datetime
    
    code = message.text.strip().upper()
    
    if not code:
        await message.answer("❌ Please enter a valid promo code.")
        return
    
    promo_repo = PromoCodeRepository(session)
    
    # Find promo code
    promo = await promo_repo.get_by_code(code)
    
    if not promo:
        await message.answer(
            "❌ Invalid promo code.\n"
            "Please check the code and try again."
        )
        return
    
    # Check if active
    if not promo.is_active:
        await message.answer(
            "❌ This promo code has been deactivated."
        )
        return
    
    # Check expiration
    if promo.expires_at and datetime.utcnow() > promo.expires_at:
        await message.answer(
            "❌ This promo code has expired."
        )
        return
    
    # Check usage limit
    if promo.current_uses >= promo.max_uses:
        await message.answer(
            "❌ This promo code has reached its usage limit."
        )
        return
    
    # Check if user already used
    has_used = await promo_repo.has_user_used(promo.id, user.id)
    if has_used:
        await message.answer(
            "❌ You have already used this promo code."
        )
        return
    
    # Apply promo code
    user_repo = UserRepository(session)
    await user_repo.update_balance(user.id, promo.reward_amount, freeze=False)
    await promo_repo.use_promo_code(promo.id, user.id)
    
    await state.clear()
    
    await message.answer(
        f"✅ Promo code activated!\n\n"
        f"🎁 Reward: {format_balance(promo.reward_amount)}\n"
        f"💰 Your new balance: {format_balance(user.balance + promo.reward_amount)}\n\n"
        f"Thank you for using our promo code!",
        reply_markup=get_back_keyboard(),
    )


@router.callback_query(F.data == "promo_info")
async def handle_promo_info(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show promo code information (for users who want to know about available promos)."""
    _ = lambda x: x
    
    promo_repo = PromoCodeRepository(session)
    active_promos = await promo_repo.get_all_active()
    
    if not active_promos:
        text = (
            "🎁 Available Promo Codes\n\n"
            "There are currently no active promo codes.\n\n"
            "💡 Follow our channel for updates!"
        )
    else:
        text = "🎁 Available Promo Codes\n\n"
        
        for promo in active_promos[:5]:  # Show up to 5
            uses_left = promo.max_uses - promo.current_uses
            
            text += f"🏷️ Code: Hidden (ask admin)\n"
            text += f"   💰 Reward: {format_balance(promo.reward_amount)}\n"
            text += f"   📊 Uses left: {uses_left}/{promo.max_uses}\n"
            
            if promo.expires_at:
                from app.utils import get_time_until
                text += f"   ⏰ Expires in: {get_time_until(promo.expires_at)}\n"
            
            text += "\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("promo"),
    )
    await callback.answer()
