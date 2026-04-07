"""
Task system handlers - users submit screenshots for admin approval.
"""
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.database.repositories import TaskRepository, UserRepository
from app.models import TaskStatus
from app.keyboards import get_tasks_keyboard, get_back_keyboard

router = Router()


class TaskStates:
    """FSM states for task creation."""
    waiting_for_title = "task_waiting_for_title"
    waiting_for_description = "task_waiting_for_description"
    waiting_for_screenshot = "task_waiting_for_screenshot"
    waiting_for_reward = "task_waiting_for_reward"


@router.callback_query(F.data == "tasks")
async def handle_tasks_menu(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show tasks menu."""
    _ = lambda x: x
    
    text = (
        f"📋 Task Management\n\n"
        f"Complete tasks and earn TON!\n\n"
        f"📝 Submit a screenshot of completed work.\n"
        f"✅ Admin will review and approve.\n"
        f"💰 Reward will be added to your balance.\n\n"
        f"Choose an option:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_tasks_keyboard(_),
    )
    await callback.answer()


@router.callback_query(F.data == "task_new")
async def handle_new_task(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    """Start creating a new task."""
    _ = lambda x: x
    
    await callback.message.edit_text(
        "📝 New Task Submission\n\n"
        "Please enter the task title:\n"
        "(e.g., 'Follow us on Twitter')",
        reply_markup=get_back_keyboard("tasks"),
    )
    
    await state.set_state(TaskStates.waiting_for_title)
    await callback.answer()


@router.message(StateFilter(TaskStates.waiting_for_title))
async def process_task_title(
    message: types.Message,
    state: FSMContext,
    session,
    user,
):
    """Process task title input."""
    title = message.text.strip()
    
    if len(title) < 3:
        await message.answer(
            "❌ Title is too short. Please enter at least 3 characters."
        )
        return
    
    # Save title to state
    await state.update_data(task_title=title)
    
    await message.answer(
        f"✅ Title saved: {title}\n\n"
        f"Now please enter the task description (optional):\n"
        f"(or send /skip to skip)",
        reply_markup=get_back_keyboard("tasks"),
    )
    
    await state.set_state(TaskStates.waiting_for_description)


@router.message(F.text == "/skip", StateFilter(TaskStates.waiting_for_description))
@router.message(F.text == "/skip", StateFilter(TaskStates.waiting_for_reward))
async def skip_optional_field(
    message: types.Message,
    state: FSMContext,
):
    """Skip optional field."""
    data = await state.get_data()
    
    if await state.get_state() == TaskStates.waiting_for_description:
        await state.update_data(task_description=None)
        
        await message.answer(
            "✅ Description skipped.\n\n"
            f"📸 Now please send a screenshot of your completed task:",
            reply_markup=get_back_keyboard("tasks"),
        )
        await state.set_state(TaskStates.waiting_for_screenshot)
    
    elif await state.get_state() == TaskStates.waiting_for_reward:
        # Admin-defined reward or default
        reward = float(data.get("task_reward", 0.1))
        
        # Create the task
        await create_task(
            session=session,
            user=user,
            title=data["task_title"],
            description=data.get("task_description"),
            screenshot_file_id=data["screenshot_file_id"],
            reward=reward,
            state=state,
        )


@router.message(StateFilter(TaskStates.waiting_for_description))
async def process_task_description(
    message: types.Message,
    state: FSMContext,
):
    """Process task description input."""
    description = message.text.strip()
    
    await state.update_data(task_description=description)
    
    await message.answer(
        f"✅ Description saved.\n\n"
        f"📸 Now please send a screenshot of your completed task:",
        reply_markup=get_back_keyboard("tasks"),
    )
    
    await state.set_state(TaskStates.waiting_for_screenshot)


@router.message(F.photo, StateFilter(TaskStates.waiting_for_screenshot))
async def process_task_screenshot(
    message: types.Message,
    state: FSMContext,
    session,
    user,
):
    """Process task screenshot."""
    # Get the largest photo
    screenshot_file_id = message.photo[-1].file_id
    
    await state.update_data(screenshot_file_id=screenshot_file_id)
    
    # Get stored data
    data = await state.get_data()
    
    # Check if reward was pre-set (admin task) or ask user
    if "task_reward" in data:
        # Admin-defined reward
        reward = float(data["task_reward"])
        
        await create_task(
            session=session,
            user=user,
            title=data["task_title"],
            description=data.get("task_description"),
            screenshot_file_id=screenshot_file_id,
            reward=reward,
            state=state,
        )
    else:
        # User-submitted task with default reward
        await message.answer(
            "✅ Screenshot received!\n\n"
            f"📤 Submitting task for admin review...\n\n"
            f"⏳ Please wait for approval.",
            reply_markup=get_back_keyboard("tasks"),
        )
        
        await create_task(
            session=session,
            user=user,
            title=data["task_title"],
            description=data.get("task_description"),
            screenshot_file_id=screenshot_file_id,
            reward=0.1,  # Default reward
            state=state,
        )


async def create_task(
    session,
    user,
    title: str,
    description: str | None,
    screenshot_file_id: str,
    reward: float,
    state: FSMContext,
):
    """Create a new task in the database."""
    task_repo = TaskRepository(session)
    
    task = await task_repo.create(
        user_id=user.id,
        title=title,
        description=description,
        screenshot_file_id=screenshot_file_id,
        reward=reward,
    )
    
    await state.clear()
    
    # Notify user
    from aiogram.types import ReplyKeyboardRemove
    
    text = (
        f"✅ Task submitted successfully!\n\n"
        f"📋 Title: {title}\n"
        f"💰 Reward: {reward:.4f} TON\n"
        f"📊 Status: Pending Review\n\n"
        f"⏳ Admin will review your submission soon."
    )
    
    # Try to edit the last message or send new one
    try:
        await state.update_data(last_message_id=None)
    except:
        pass
    
    # Send confirmation
    from aiogram import Bot
    bot = Bot(token="")  # Will be injected
    
    # Just send as new message
    await message.answer(
        text,
        reply_markup=get_back_keyboard("task_my"),
    )


@router.callback_query(F.data == "task_my")
async def handle_my_tasks(
    callback: types.CallbackQuery,
    session,
    user,
):
    """Show user's tasks."""
    _ = lambda x: x
    
    task_repo = TaskRepository(session)
    tasks = await task_repo.get_user_tasks(user.id)
    
    if not tasks:
        text = (
            "📜 My Tasks\n\n"
            "You haven't submitted any tasks yet.\n\n"
            "📝 Create a new task to get started!"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_tasks_keyboard(_),
        )
        await callback.answer()
        return
    
    # Show recent tasks
    text = "📜 My Tasks\n\n"
    
    for task in tasks[:10]:  # Show last 10 tasks
        status_emoji = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.APPROVED: "✅",
            TaskStatus.REJECTED: "❌",
        }.get(task.status, "❓")
        
        text += f"{status_emoji} #{task.id} - {task.title}\n"
        text += f"   💰 {task.reward:.4f} TON\n"
        
        if task.admin_comment and task.status == TaskStatus.REJECTED:
            text += f"   📝 Comment: {task.admin_comment}\n"
        
        text += "\n"
    
    if len(tasks) > 10:
        text += f"... and {len(tasks) - 10} more tasks\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("tasks"),
    )
    await callback.answer()
