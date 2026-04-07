"""
Withdrawal system handlers.
"""
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.database.repositories import WithdrawalRepository, UserRepository
from app.models import WithdrawalStatus
from app.keyboards import get_withdraw_keyboard, get_back_keyboard, get_confirm_keyboard
from app.config import config
from app.utils import format_balance, validate_wallet_address

router = Router()


class WithdrawStates:
    """FSM states for withdrawal."""
    waiting_for_amount = "withdraw_waiting_for_amount"
    waiting_for_wallet = "withdraw_waiting_for_wallet"
    waiting_for_confirmation = "withdraw_waiting_for_confirmation"


@router.callback_query(F.data == "withdraw")
async def handle_withdraw_menu(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show withdrawal menu."""
    _ = lambda x: x
    
    text = (
        f"💸 Withdrawal\n\n"
        f"📊 Available balance: {format_balance(user.balance)}\n"
        f"❄️ Frozen balance: {format_balance(user.frozen_balance)}\n\n"
        f"⚠️ Minimum withdrawal: {config.MIN_WITHDRAWAL_AMOUNT} TON\n\n"
        f"Choose an option:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_withdraw_keyboard(_),
    )
    await callback.answer()


@router.callback_query(F.data == "withdraw_create")
async def handle_withdraw_create(
    callback: types.CallbackQuery,
    state: FSMContext,
    user,
):
    """Start withdrawal process."""
    if user.balance < config.MIN_WITHDRAWAL_AMOUNT:
        await callback.answer(
            f"❌ Insufficient balance. Minimum withdrawal is {config.MIN_WITHDRAWAL_AMOUNT} TON.",
            show_alert=True,
        )
        return
    
    await callback.message.edit_text(
        f"💸 Create Withdrawal\n\n"
        f"📊 Your balance: {format_balance(user.balance)}\n"
        f"⚠️ Minimum: {config.MIN_WITHDRAWAL_AMOUNT} TON\n\n"
        f"Enter the amount to withdraw:",
        reply_markup=get_back_keyboard("withdraw"),
    )
    
    await state.set_state(WithdrawStates.waiting_for_amount)
    await callback.answer()


@router.message(StateFilter(WithdrawStates.waiting_for_amount))
async def process_withdraw_amount(
    message: types.Message,
    state: FSMContext,
    user,
):
    """Process withdrawal amount."""
    try:
        amount = float(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ Invalid amount. Please enter a number (e.g., 0.5)"
        )
        return
    
    # Validate amount
    if amount < config.MIN_WITHDRAWAL_AMOUNT:
        await message.answer(
            f"❌ Amount must be at least {config.MIN_WITHDRAWAL_AMOUNT} TON."
        )
        return
    
    if amount > user.balance:
        await message.answer(
            f"❌ Insufficient balance. You have {format_balance(user.balance)}."
        )
        return
    
    # Save amount to state
    await state.update_data(withdraw_amount=amount)
    
    await message.answer(
        f"✅ Amount: {format_balance(amount)}\n\n"
        f"Now enter your TON wallet address:",
        reply_markup=get_back_keyboard("withdraw"),
    )
    
    await state.set_state(WithdrawStates.waiting_for_wallet)


@router.message(StateFilter(WithdrawStates.waiting_for_wallet))
async def process_withdraw_wallet(
    message: types.Message,
    state: FSMContext,
    user,
):
    """Process wallet address."""
    wallet_address = message.text.strip()
    
    # Validate wallet address
    if not validate_wallet_address(wallet_address):
        await message.answer(
            "❌ Invalid wallet address format.\n"
            "Please enter a valid TON address (starting with UQ or EQ)."
        )
        return
    
    # Save wallet to state
    data = await state.update_data(withdraw_wallet=wallet_address)
    amount = data.get("withdraw_amount", 0)
    
    # Show confirmation
    await message.answer(
        f"💸 Confirm Withdrawal\n\n"
        f"💰 Amount: {format_balance(amount)}\n"
        f"🏦 Wallet: `{wallet_address}`\n"
        f"⚠️ Network fee may apply\n\n"
        f"Confirm this withdrawal?",
        reply_markup=get_confirm_keyboard(
            confirm_callback="withdraw_confirm",
            cancel_callback="withdraw_cancel",
        ),
        parse_mode="Markdown",
    )
    
    await state.set_state(WithdrawStates.waiting_for_confirmation)


@router.callback_query(F.data == "withdraw_confirm")
async def confirm_withdrawal(
    callback: types.CallbackQuery,
    state: FSMContext,
    session,
    user,
):
    """Confirm and create withdrawal request."""
    data = await state.get_data()
    amount = data.get("withdraw_amount", 0)
    wallet = data.get("withdraw_wallet", "")
    
    if not amount or not wallet:
        await callback.answer("❌ Invalid withdrawal data. Please start over.", show_alert=True)
        await state.clear()
        return
    
    # Deduct balance
    user_repo = UserRepository(session)
    await user_repo.deduct_balance(user.id, amount)
    
    # Create withdrawal request
    withdraw_repo = WithdrawalRepository(session)
    withdrawal = await withdraw_repo.create(
        user_id=user.id,
        amount=amount,
        wallet_address=wallet,
    )
    
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Withdrawal request created!\n\n"
        f"📋 Request ID: #{withdrawal.id}\n"
        f"💰 Amount: {format_balance(amount)}\n"
        f"🏦 Wallet: `{wallet}`\n"
        f"📊 Status: Pending\n\n"
        f"⏳ Admin will process your request soon.",
        reply_markup=get_back_keyboard("withdraw_history"),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "withdraw_cancel")
async def cancel_withdrawal(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    """Cancel withdrawal process."""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Withdrawal cancelled.",
        reply_markup=get_withdraw_keyboard(lambda x: x),
    )
    await callback.answer()


@router.callback_query(F.data == "withdraw_history")
async def handle_withdraw_history(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show withdrawal history."""
    _ = lambda x: x
    
    withdraw_repo = WithdrawalRepository(session)
    withdrawals = await withdraw_repo.get_user_withdrawals(user.id)
    
    if not withdrawals:
        text = (
            "📜 Withdrawal History\n\n"
            "You haven't made any withdrawals yet."
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_withdraw_keyboard(_),
        )
        await callback.answer()
        return
    
    text = "📜 Withdrawal History\n\n"
    
    for withdrawal in withdrawals[:10]:  # Show last 10
        status_emoji = {
            WithdrawalStatus.PENDING: "⏳",
            WithdrawalStatus.PROCESSING: "⚙️",
            WithdrawalStatus.COMPLETED: "✅",
            WithdrawalStatus.REJECTED: "❌",
        }.get(withdrawal.status, "❓")
        
        text += f"{status_emoji} #{withdrawal.id} - {format_balance(withdrawal.amount)}\n"
        text += f"   🏦 {withdrawal.wallet_address[:20]}...\n"
        
        if withdrawal.transaction_hash:
            text += f"   🔗 TX: `{withdrawal.transaction_hash[:16]}...`\n"
        
        if withdrawal.admin_comment and withdrawal.status == WithdrawalStatus.REJECTED:
            text += f"   📝 Comment: {withdrawal.admin_comment}\n"
        
        text += "\n"
    
    if len(withdrawals) > 10:
        text += f"... and {len(withdrawals) - 10} more withdrawals\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("withdraw"),
        parse_mode="Markdown",
    )
    await callback.answer()
