"""
Admin panel handlers for task review and withdrawal management.
"""
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.database.repositories import (
    TaskRepository, WithdrawalRepository, UserRepository, 
    PromoCodeRepository, AdminLogRepository
)
from app.models import TaskStatus, WithdrawalStatus
from app.keyboards import (
    get_task_review_keyboard, get_withdrawal_action_keyboard,
    get_admin_menu_keyboard, get_back_keyboard
)
from app.config import config

router = Router()


class AdminStates:
    """FSM states for admin actions."""
    waiting_for_promo_amount = "admin_promo_amount"
    waiting_for_promo_uses = "admin_promo_uses"
    waiting_for_promo_expiry = "admin_promo_expiry"
    waiting_for_reject_reason = "admin_waiting_for_reject_reason"
    waiting_for_reject_withdraw_reason = "admin_waiting_for_reject_withdraw_reason"


# Admin menu entry point
@router.callback_query(F.data == "admin_panel")
async def handle_admin_menu(
    callback: types.CallbackQuery,
    user,
):
    """Show admin panel menu."""
    _ = lambda x: x
    
    # Verify admin
    if user.telegram_id not in config.ADMIN_IDS:
        await callback.answer("⛔️ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🛠️ Admin Panel\n\n"
        "Select an option:",
        reply_markup=get_admin_menu_keyboard(_),
    )
    await callback.answer()


# Task Review Queue
@router.callback_query(F.data == "admin_tasks_queue")
async def handle_admin_tasks_queue(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show pending tasks queue."""
    if user.telegram_id not in config.ADMIN_IDS:
        await callback.answer("⛔️ Access denied.", show_alert=True)
        return
    
    task_repo = TaskRepository(session)
    pending_tasks = await task_repo.get_pending_tasks()
    
    if not pending_tasks:
        text = (
            "📋 Pending Tasks\n\n"
            "✅ No pending tasks!\n\n"
            "All tasks have been reviewed."
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_menu_keyboard(lambda x: x),
        )
        await callback.answer()
        return
    
    # Show first pending task
    task = pending_tasks[0]
    
    text = (
        f"📋 Task Review #{task.id}\n\n"
        f"👤 User: @{task.user.username or 'N/A'} ({task.user.telegram_id})\n"
        f"📝 Title: {task.title}\n"
    )
    
    if task.description:
        text += f"📄 Description: {task.description}\n"
    
    text += f"💰 Reward: {task.reward:.4f} TON\n"
    text += f"⏳ Submitted: {task.created_at.strftime('%Y-%m-%d %H:%M')}\n"
    
    await callback.message.answer(
        text,
        reply_markup=get_task_review_keyboard(task.id),
    )
    
    # Send screenshot if available
    if task.screenshot_file_id:
        await callback.message.answer_photo(
            photo=task.screenshot_file_id,
            caption=f"📸 Screenshot for task #{task.id}",
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("task_approve:"))
async def handle_task_approve(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Approve a task."""
    if user.telegram_id not in config.ADMIN_IDS:
        await callback.answer("⛔️ Access denied.", show_alert=True)
        return
    
    task_id = int(callback.data.split(":")[1])
    
    task_repo = TaskRepository(session)
    user_repo = UserRepository(session)
    admin_log_repo = AdminLogRepository(session)
    
    task = await task_repo.get_by_id(task_id)
    
    if not task:
        await callback.answer("❌ Task not found.", show_alert=True)
        return
    
    # Update task status
    await task_repo.update_status(
        task_id=task_id,
        status=TaskStatus.APPROVED,
        reviewed_by=user.id,
    )
    
    # Credit reward to user
    await user_repo.update_balance(task.user_id, task.reward, freeze=False)
    
    # Log action
    await admin_log_repo.create(
        admin_id=user.telegram_id,
        action="approve_task",
        target_type="task",
        target_id=task_id,
        details=f"Approved task #{task_id} for user {task.user_id}, reward: {task.reward}",
    )
    
    await callback.answer("✅ Task approved! Reward credited.", show_alert=True)
    
    # Notify user (optional - would need bot instance)
    
    # Show next task
    await handle_admin_tasks_queue(callback, session, user)


@router.callback_query(F.data.startswith("task_reject:"))
async def handle_task_reject(
    callback: types.CallbackQuery,
    state: FSMContext,
    session,
    user,
):
    """Reject a task (asks for comment)."""
    if user.telegram_id not in config.ADMIN_IDS:
        await callback.answer("⛔️ Access denied.", show_alert=True)
        return
    
    task_id = int(callback.data.split(":")[1])
    
    await state.update_data(reject_task_id=task_id)
    
    await callback.message.answer(
        "❌ Reject Task\n\n"
        "Please enter a reason for rejection:\n"
        "(or send /skip for no comment)",
        reply_markup=get_back_keyboard("admin_tasks_queue"),
    )
    
    await state.set_state(AdminStates.waiting_for_reject_reason)
    await callback.answer()


@router.message(StateFilter(AdminStates.waiting_for_reject_reason))
async def process_reject_reason(
    message: types.Message,
    state: FSMContext,
    session,
    user,
):
    """Process rejection reason."""
    data = await state.get_data()
    task_id = data.get("reject_task_id")
    
    if not task_id:
        await message.answer("❌ Error: Task ID not found.")
        await state.clear()
        return
    
    comment = message.text.strip()
    
    if comment == "/skip":
        comment = None
    
    task_repo = TaskRepository(session)
    admin_log_repo = AdminLogRepository(session)
    
    # Update task status
    await task_repo.update_status(
        task_id=task_id,
        status=TaskStatus.REJECTED,
        admin_comment=comment,
        reviewed_by=user.id,
    )
    
    # Log action
    await admin_log_repo.create(
        admin_id=user.telegram_id,
        action="reject_task",
        target_type="task",
        target_id=task_id,
        details=f"Rejected task #{task_id}. Comment: {comment}",
    )
    
    await state.clear()
    
    await message.answer(
        f"❌ Task #{task_id} rejected.",
        reply_markup=get_admin_menu_keyboard(lambda x: x),
    )


# Withdrawal Review Queue
@router.callback_query(F.data == "admin_withdrawals_queue")
async def handle_admin_withdrawals_queue(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show pending withdrawals queue."""
    if user.telegram_id not in config.ADMIN_IDS:
        await callback.answer("⛔️ Access denied.", show_alert=True)
        return
    
    withdraw_repo = WithdrawalRepository(session)
    pending_withdrawals = await withdraw_repo.get_pending_withdrawals()
    
    if not pending_withdrawals:
        text = (
            "💸 Pending Withdrawals\n\n"
            "✅ No pending withdrawals!\n\n"
            "All withdrawals have been processed."
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_menu_keyboard(lambda x: x),
        )
        await callback.answer()
        return
    
    # Show first pending withdrawal
    withdrawal = pending_withdrawals[0]
    
    text = (
        f"💸 Withdrawal Request #{withdrawal.id}\n\n"
        f"👤 User: @{withdrawal.user.username or 'N/A'} ({withdrawal.user.telegram_id})\n"
        f"💰 Amount: {withdrawal.amount:.4f} TON\n"
        f"🏦 Wallet: `{withdrawal.wallet_address}`\n"
        f"⏳ Requested: {withdrawal.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"User Balance: {withdrawal.user.balance:.4f} TON"
    )
    
    await callback.message.answer(
        text,
        reply_markup=get_withdrawal_action_keyboard(withdrawal.id),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("withdraw_approve:"))
async def handle_withdraw_approve(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Approve and process withdrawal."""
    if user.telegram_id not in config.ADMIN_IDS:
        await callback.answer("⛔️ Access denied.", show_alert=True)
        return
    
    withdrawal_id = int(callback.data.split(":")[1])
    
    withdraw_repo = WithdrawalRepository(session)
    admin_log_repo = AdminLogRepository(session)
    
    withdrawal = await withdraw_repo.get_by_id(withdrawal_id)
    
    if not withdrawal:
        await callback.answer("❌ Withdrawal not found.", show_alert=True)
        return
    
    # In production, this would trigger actual TON transfer
    # For now, just mark as completed with a mock TX hash
    import hashlib
    mock_tx_hash = hashlib.sha256(
        f"{withdrawal_id}{user.telegram_id}".encode()
    ).hexdigest()[:64]
    
    # Update withdrawal status
    await withdraw_repo.update_status(
        withdrawal_id=withdrawal_id,
        status=WithdrawalStatus.COMPLETED,
        processed_by=user.id,
        transaction_hash=mock_tx_hash,
    )
    
    # Log action
    await admin_log_repo.create(
        admin_id=user.telegram_id,
        action="approve_withdrawal",
        target_type="withdrawal",
        target_id=withdrawal_id,
        details=f"Approved withdrawal #{withdrawal_id} for {withdrawal.amount} TON",
    )
    
    await callback.answer("✅ Withdrawal approved!", show_alert=True)
    
    # Show next withdrawal
    await handle_admin_withdrawals_queue(callback, session, user)


@router.callback_query(F.data.startswith("withdraw_reject:"))
async def handle_withdraw_reject(
    callback: types.CallbackQuery,
    state: FSMContext,
    session,
    user,
):
    """Reject withdrawal (asks for comment)."""
    if user.telegram_id not in config.ADMIN_IDS:
        await callback.answer("⛔️ Access denied.", show_alert=True)
        return
    
    withdrawal_id = int(callback.data.split(":")[1])
    
    await state.update_data(reject_withdrawal_id=withdrawal_id)
    
    await callback.message.answer(
        "❌ Reject Withdrawal\n\n"
        "Please enter a reason for rejection:",
        reply_markup=get_back_keyboard("admin_withdrawals_queue"),
    )
    
    await state.set_state(AdminStates.waiting_for_reject_withdraw_reason)
    await callback.answer()


@router.message(StateFilter(AdminStates.waiting_for_reject_withdraw_reason))
async def process_reject_withdraw_reason(
    message: types.Message,
    state: FSMContext,
    session,
    user,
):
    """Process withdrawal rejection reason."""
    data = await state.get_data()
    withdrawal_id = data.get("reject_withdrawal_id")
    
    if not withdrawal_id:
        await message.answer("❌ Error: Withdrawal ID not found.")
        await state.clear()
        return
    
    comment = message.text.strip()
    
    withdraw_repo = WithdrawalRepository(session)
    user_repo = UserRepository(session)
    admin_log_repo = AdminLogRepository(session)
    
    withdrawal = await withdraw_repo.get_by_id(withdrawal_id)
    
    if withdrawal:
        # Refund the amount
        await user_repo.update_balance(withdrawal.user_id, withdrawal.amount, freeze=False)
        
        # Update withdrawal status
        await withdraw_repo.update_status(
            withdrawal_id=withdrawal_id,
            status=WithdrawalStatus.REJECTED,
            admin_comment=comment,
            processed_by=user.id,
        )
        
        # Log action
        await admin_log_repo.create(
            admin_id=user.telegram_id,
            action="reject_withdrawal",
            target_type="withdrawal",
            target_id=withdrawal_id,
            details=f"Rejected withdrawal #{withdrawal_id}. Comment: {comment}",
        )
    
    await state.clear()
    
    await message.answer(
        f"❌ Withdrawal #{withdrawal_id} rejected. Amount refunded.",
        reply_markup=get_admin_menu_keyboard(lambda x: x),
    )


# Promo Code Creation
@router.callback_query(F.data == "admin_promo_create")
async def handle_admin_promo_create(
    callback: types.CallbackQuery,
    state: FSMContext,
    user,
):
    """Start creating a promo code."""
    if user.telegram_id not in config.ADMIN_IDS:
        await callback.answer("⛔️ Access denied.", show_alert=True)
        return
    
    await callback.message.answer(
        "🎁 Create Promo Code\n\n"
        "Enter the reward amount (in TON):",
        reply_markup=get_back_keyboard("admin_panel"),
    )
    
    await state.set_state(AdminStates.waiting_for_promo_amount)
    await callback.answer()


@router.message(StateFilter(AdminStates.waiting_for_promo_amount))
async def process_promo_amount(
    message: types.Message,
    state: FSMContext,
):
    """Process promo code reward amount."""
    try:
        amount = float(message.text.strip())
    except ValueError:
        await message.answer("❌ Invalid amount. Please enter a number.")
        return
    
    if amount <= 0:
        await message.answer("❌ Amount must be greater than 0.")
        return
    
    await state.update_data(promo_amount=amount)
    
    await message.answer(
        f"✅ Reward: {amount:.4f} TON\n\n"
        "Enter maximum number of uses:",
        reply_markup=get_back_keyboard("admin_panel"),
    )
    
    await state.set_state(AdminStates.waiting_for_promo_uses)


@router.message(StateFilter(AdminStates.waiting_for_promo_uses))
async def process_promo_uses(
    message: types.Message,
    state: FSMContext,
):
    """Process promo code max uses."""
    try:
        uses = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Invalid number. Please enter an integer.")
        return
    
    if uses <= 0:
        await message.answer("❌ Uses must be greater than 0.")
        return
    
    await state.update_data(promo_max_uses=uses)
    
    await message.answer(
        f"✅ Max uses: {uses}\n\n"
        "Promo code created! Use /promo_info to see it.\n"
        "(Code generation handled by admin command)",
        reply_markup=get_admin_menu_keyboard(lambda x: x),
    )
    
    # In production, generate and store the promo code
    await state.clear()
