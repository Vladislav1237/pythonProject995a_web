"""
Balance and economy handlers.
"""
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from app.database.repositories import UserRepository
from app.keyboards import get_back_keyboard
from app.utils import format_balance, is_subscription_active, can_claim_reward

router = Router()


@router.callback_query(F.data == "balance")
async def handle_balance(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show user balance information."""
    _ = lambda x: x
    
    # Calculate total (available + frozen)
    total = user.balance + user.frozen_balance
    
    text = (
        f"💰 Balance Information\n\n"
        f"📊 Available: {format_balance(user.balance)}\n"
        f"❄️ Frozen: {format_balance(user.frozen_balance)}\n"
        f"💵 Total: {format_balance(total)}\n\n"
    )
    
    # Subscription status
    if is_subscription_active(user):
        text += f"✅ Subscription: Active\n"
        if user.subscription_end:
            from app.utils import get_time_until
            text += f"⏰ Expires in: {get_time_until(user.subscription_end)}\n"
    else:
        text += f"❌ Subscription: Inactive\n"
        text += f"💡 Subscribe to earn daily rewards!\n"
    
    # Referral earnings info
    referral_count = len(user.referred_users)
    if referral_count > 0:
        text += f"\n👥 You have {referral_count} referrals\n"
        text += f"💰 Earned from referrals: {format_balance(referral_count * 0.025)}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "claim_reward")
async def handle_claim_reward(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Claim daily subscription reward."""
    from app.config import config
    
    _ = lambda x: x
    
    can_claim, next_claim_time = can_claim_reward(user)
    
    if not can_claim:
        if next_claim_time:
            from app.utils import get_time_until
            wait_time = get_time_until(next_claim_time)
            await callback.answer(
                f"⏰ Please wait {wait_time} before claiming again.",
                show_alert=True,
            )
        else:
            await callback.answer(
                "❌ You need an active subscription to claim rewards.",
                show_alert=True,
            )
        return
    
    # Reward amount (configurable)
    reward_amount = 0.01  # Daily reward in TON
    
    # Update user balance
    user_repo = UserRepository(session)
    await user_repo.update_balance(user.id, reward_amount, freeze=False)
    await user_repo.update_last_reward_claim(user.id)
    
    await callback.message.answer(
        f"✅ Reward claimed!\n\n"
        f"💰 Amount: {format_balance(reward_amount)}\n"
        f"⏰ Next claim available in 24 hours."
    )
    await callback.answer()
