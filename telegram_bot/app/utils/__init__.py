"""
Utility functions for the Telegram bot.
"""
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from app.config import config


def generate_referral_link(bot_username: str, user_id: int) -> str:
    """Generate a referral link for a user."""
    return f"https://t.me/{bot_username}?start={user_id}"


def format_balance(amount: float, currency: str = "TON") -> str:
    """Format balance with currency."""
    return f"{amount:.4f} {currency}"


def is_subscription_active(user) -> bool:
    """Check if user's subscription is active."""
    if not user.is_subscribed:
        return False
    
    if not user.subscription_end:
        return False
    
    return datetime.utcnow() < user.subscription_end


def can_claim_reward(user, freeze_hours: int = None) -> tuple[bool, Optional[datetime]]:
    """
    Check if user can claim reward.
    Returns (can_claim, next_claim_time).
    
    Rules:
    - Must be subscribed
    - 24h freeze period after last claim
    """
    if freeze_hours is None:
        freeze_hours = config.FREEZE_PERIOD_HOURS
    
    if not is_subscription_active(user):
        return False, None
    
    if not user.last_reward_claim:
        return True, None
    
    next_claim_time = user.last_reward_claim + timedelta(hours=freeze_hours)
    
    if datetime.utcnow() >= next_claim_time:
        return True, None
    
    return False, next_claim_time


def calculate_early_unsubscribe_penalty(
    subscription_start: datetime,
    subscription_end: datetime,
    total_amount: float,
) -> float:
    """
    Calculate penalty for early unsubscribe.
    Penalty is proportional to remaining time.
    """
    total_duration = subscription_end - subscription_start
    remaining_duration = subscription_end - datetime.utcnow()
    
    if remaining_duration <= timedelta(0):
        return 0.0
    
    penalty_ratio = remaining_duration.total_seconds() / total_duration.total_seconds()
    penalty = total_amount * penalty_ratio
    
    return min(penalty, total_amount)


def validate_wallet_address(address: str) -> bool:
    """Validate TON wallet address format."""
    # Basic validation - TON addresses are typically 48 characters
    # This can be enhanced with proper TON address validation
    if not address:
        return False
    
    # UQ/ EQ format or raw format
    if address.startswith("UQ") or address.startswith("EQ"):
        return len(address) >= 46
    
    # Raw format (hex)
    if all(c in "0123456789abcdefABCDEF" for c in address):
        return len(address) in [48, 64]
    
    return False


def generate_promo_code(length: int = 8) -> str:
    """Generate a random promo code."""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    hash_input = f"{datetime.utcnow().isoformat()}{length}"
    hash_bytes = hashlib.sha256(hash_input.encode()).hexdigest()
    
    code = ""
    for i in range(length):
        code += chars[int(hash_bytes[i], 16) % len(chars)]
    
    return code


def format_datetime(dt: datetime, locale: str = "en") -> str:
    """Format datetime for display."""
    if locale == "ru":
        return dt.strftime("%d.%m.%Y %H:%M")
    return dt.strftime("%Y-%m-%d %H:%M")


def get_time_until(dt: datetime) -> str:
    """Get human-readable time until datetime."""
    now = datetime.utcnow()
    diff = dt - now
    
    if diff.total_seconds() <= 0:
        return "now"
    
    hours = int(diff.total_seconds() // 3600)
    minutes = int((diff.total_seconds() % 3600) // 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
