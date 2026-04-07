"""
Repository pattern for database operations.
"""
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List

from app.models import (
    User, Task, Withdrawal, PromoCode, PromoCodeUse, AdminLog,
    UserStatus, TaskStatus, WithdrawalStatus
)


class UserRepository:
    """User repository for database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by internal ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "en",
        referrer_id: Optional[int] = None,
    ) -> User:
        """Create a new user."""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            referrer_id=referrer_id,
        )
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def update_balance(
        self, user_id: int, amount: float, freeze: bool = False
    ) -> User:
        """Update user balance."""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if freeze:
            user.frozen_balance += amount
        else:
            user.balance += amount
        
        await self.session.flush()
        return user
    
    async def unfreeze_balance(self, user_id: int, amount: float) -> User:
        """Unfreeze user balance."""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if user.frozen_balance < amount:
            raise ValueError("Insufficient frozen balance")
        
        user.frozen_balance -= amount
        user.balance += amount
        await self.session.flush()
        return user
    
    async def deduct_balance(self, user_id: int, amount: float) -> User:
        """Deduct from user balance."""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if user.balance < amount:
            raise ValueError("Insufficient balance")
        
        user.balance -= amount
        await self.session.flush()
        return user
    
    async def update_subscription(
        self,
        user_id: int,
        is_subscribed: bool,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> User:
        """Update user subscription status."""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.is_subscribed = is_subscribed
        if start_date:
            user.subscription_start = start_date
        if end_date:
            user.subscription_end = end_date
        
        await self.session.flush()
        return user
    
    async def update_last_reward_claim(self, user_id: int) -> User:
        """Update last reward claim time."""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.last_reward_claim = datetime.utcnow()
        await self.session.flush()
        return user
    
    async def get_all_users(self) -> List[User]:
        """Get all users."""
        result = await self.session.execute(select(User))
        return list(result.scalars().all())
    
    async def get_referral_count(self, user_id: int) -> int:
        """Get number of referred users."""
        result = await self.session.execute(
            select(func.count()).where(User.referrer_id == user_id)
        )
        return result.scalar() or 0


class TaskRepository:
    """Task repository for database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        screenshot_file_id: Optional[str] = None,
        reward: float = 0.0,
    ) -> Task:
        """Create a new task."""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            screenshot_file_id=screenshot_file_id,
            reward=reward,
        )
        self.session.add(task)
        await self.session.flush()
        return task
    
    async def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        result = await self.session.execute(
            select(Task)
            .where(Task.status == TaskStatus.PENDING)
            .options(selectinload(Task.user))
            .order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_user_tasks(self, user_id: int) -> List[Task]:
        """Get all tasks for a user."""
        result = await self.session.execute(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_status(
        self,
        task_id: int,
        status: TaskStatus,
        admin_comment: Optional[str] = None,
        reviewed_by: Optional[int] = None,
    ) -> Task:
        """Update task status."""
        task = await self.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.status = status
        task.admin_comment = admin_comment
        task.reviewed_by = reviewed_by
        task.reviewed_at = datetime.utcnow()
        
        await self.session.flush()
        return task


class WithdrawalRepository:
    """Withdrawal repository for database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        user_id: int,
        amount: float,
        wallet_address: str,
    ) -> Withdrawal:
        """Create a new withdrawal request."""
        withdrawal = Withdrawal(
            user_id=user_id,
            amount=amount,
            wallet_address=wallet_address,
        )
        self.session.add(withdrawal)
        await self.session.flush()
        return withdrawal
    
    async def get_by_id(self, withdrawal_id: int) -> Optional[Withdrawal]:
        """Get withdrawal by ID."""
        result = await self.session.execute(
            select(Withdrawal).where(Withdrawal.id == withdrawal_id)
        )
        return result.scalar_one_or_none()
    
    async def get_pending_withdrawals(self) -> List[Withdrawal]:
        """Get all pending withdrawals."""
        result = await self.session.execute(
            select(Withdrawal)
            .where(Withdrawal.status == WithdrawalStatus.PENDING)
            .options(selectinload(Withdrawal.user))
            .order_by(Withdrawal.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_status(
        self,
        withdrawal_id: int,
        status: WithdrawalStatus,
        admin_comment: Optional[str] = None,
        processed_by: Optional[int] = None,
        transaction_hash: Optional[str] = None,
    ) -> Withdrawal:
        """Update withdrawal status."""
        withdrawal = await self.get_by_id(withdrawal_id)
        if not withdrawal:
            raise ValueError(f"Withdrawal {withdrawal_id} not found")
        
        withdrawal.status = status
        withdrawal.admin_comment = admin_comment
        withdrawal.processed_by = processed_by
        withdrawal.processed_at = datetime.utcnow()
        if transaction_hash:
            withdrawal.transaction_hash = transaction_hash
        
        await self.session.flush()
        return withdrawal
    
    async def get_user_withdrawals(self, user_id: int) -> List[Withdrawal]:
        """Get all withdrawals for a user."""
        result = await self.session.execute(
            select(Withdrawal)
            .where(Withdrawal.user_id == user_id)
            .order_by(Withdrawal.created_at.desc())
        )
        return list(result.scalars().all())


class PromoCodeRepository:
    """Promo code repository for database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_code(self, code: str) -> Optional[PromoCode]:
        """Get promo code by code string."""
        result = await self.session.execute(
            select(PromoCode).where(PromoCode.code == code.upper())
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        code: str,
        reward_amount: float,
        max_uses: int = 1,
        expires_at: Optional[datetime] = None,
    ) -> PromoCode:
        """Create a new promo code."""
        promo_code = PromoCode(
            code=code.upper(),
            reward_amount=reward_amount,
            max_uses=max_uses,
            expires_at=expires_at,
        )
        self.session.add(promo_code)
        await self.session.flush()
        return promo_code
    
    async def use_promo_code(self, promo_code_id: int, user_id: int) -> PromoCodeUse:
        """Record promo code usage."""
        use = PromoCodeUse(promo_code_id=promo_code_id, user_id=user_id)
        
        # Update usage count
        promo_code = await self.get_by_id(promo_code_id)
        if promo_code:
            promo_code.current_uses += 1
        
        self.session.add(use)
        await self.session.flush()
        return use
    
    async def get_by_id(self, promo_code_id: int) -> Optional[PromoCode]:
        """Get promo code by ID."""
        result = await self.session.execute(
            select(PromoCode).where(PromoCode.id == promo_code_id)
        )
        return result.scalar_one_or_none()
    
    async def has_user_used(self, promo_code_id: int, user_id: int) -> bool:
        """Check if user has already used this promo code."""
        result = await self.session.execute(
            select(PromoCodeUse).where(
                and_(
                    PromoCodeUse.promo_code_id == promo_code_id,
                    PromoCodeUse.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def get_all_active(self) -> List[PromoCode]:
        """Get all active promo codes."""
        result = await self.session.execute(
            select(PromoCode)
            .where(
                and_(
                    PromoCode.is_active == True,
                    PromoCode.current_uses < PromoCode.max_uses,
                )
            )
        )
        return list(result.scalars().all())


class AdminLogRepository:
    """Admin log repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        admin_id: int,
        action: str,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        details: Optional[str] = None,
    ) -> AdminLog:
        """Create an admin log entry."""
        log = AdminLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
        )
        self.session.add(log)
        await self.session.flush()
        return log
