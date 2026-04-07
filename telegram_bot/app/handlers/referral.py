"""
Referral system handlers.
"""
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from app.database.repositories import UserRepository
from app.keyboards import get_referral_keyboard, get_back_keyboard
from app.utils import generate_referral_link, format_balance

router = Router()


@router.callback_query(F.data == "referrals")
async def handle_referrals(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show referral information and link."""
    from aiogram.types import Bot
    
    _ = lambda x: x
    
    bot: Bot = callback.bot
    
    # Get bot info for username
    bot_info = await bot.get_me()
    
    # Generate referral link
    referral_link = generate_referral_link(bot_info.username, user.id)
    
    # Count referrals
    referral_count = len(user.referred_users)
    
    # Calculate earnings
    total_earned = referral_count * 0.025  # 0.025 TON per referral
    
    text = (
        f"👥 Referral Program\n\n"
        f"📊 Your referrals: {referral_count}\n"
        f"💰 Reward per referral: 0.025 TON\n"
        f"💵 Total earned: {format_balance(total_earned)}\n\n"
        f"🔗 Your referral link:\n"
        f"<code>{referral_link}</code>\n\n"
        f"💡 Share this link with friends!\n"
        f"When they join, you'll receive 0.025 TON.\n\n"
        f"⚠️ Rewards are credited when your referral:\n"
        f"• Joins the bot\n"
        f"• Subscribes to the channel\n"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_referral_keyboard(referral_link),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("referral_earnings:"))
async def handle_referral_earnings(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show detailed referral earnings."""
    _ = lambda x: x
    
    referral_count = len(user.referred_users)
    pending_count = 0  # Could track pending referrals
    
    # Calculate different tiers or bonuses if needed
    base_earnings = referral_count * 0.025
    bonus = 0
    
    if referral_count >= 10:
        bonus = base_earnings * 0.1  # 10% bonus for 10+ referrals
    elif referral_count >= 5:
        bonus = base_earnings * 0.05  # 5% bonus for 5+ referrals
    
    total = base_earnings + bonus
    
    text = (
        f"📊 Referral Earnings Breakdown\n\n"
        f"👥 Total referrals: {referral_count}\n"
        f"💰 Base earnings: {format_balance(base_earnings)}\n"
    )
    
    if bonus > 0:
        text += f"🎁 Bonus ({int((bonus/base_earnings)*100)}%): {format_balance(bonus)}\n"
    
    text += f"💵 Total: {format_balance(total)}\n\n"
    
    if referral_count == 0:
        text += "💡 Start inviting friends to earn TON!"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("referrals"),
    )
    await callback.answer()
