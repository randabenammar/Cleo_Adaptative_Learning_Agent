"""
Middleware pour vérifier les quotas.
"""

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
import logging

try:
    from backend.models.database import get_db
    from backend.models.user import User
    from backend.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
    from backend.api.auth import get_current_active_user
except ImportError:
    from models.database import get_db
    from models.user import User
    from models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
    from api.auth import get_current_active_user

logger = logging.getLogger("backend.app")

class QuotaExceeded(HTTPException):
    """Exception levée quand un quota est dépassé."""
    def __init__(self, quota_type: str, current_usage: int, limit: int, upgrade_tier: str):
        detail = {
            "error": "quota_exceeded",
            "quota_type": quota_type,
            "message": f"You've reached your monthly limit of {limit} {quota_type}",
            "current_usage": current_usage,
            "limit": limit,
            "upgrade_to": upgrade_tier,
            "upgrade_url": "/pricing"
        }
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

def check_quiz_quota(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Vérifie si l'utilisateur peut démarrer un nouveau quiz."""
    logger.info(f"🔍 Checking quiz quota for: {current_user.username}")
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        logger.warning(f"⚠️ No subscription found for {current_user.username}")
        subscription = Subscription(
            user_id=current_user.id,
            tier=SubscriptionTier.FREE,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    if not subscription.check_quota("quiz"):
        limits = subscription.get_limits()
        current_usage = subscription.quizzes_this_month
        limit = limits["quizzes_per_month"]
        
        logger.warning(f"❌ Quota exceeded for {current_user.username}: {current_usage}/{limit}")
        
        tier_order = [
            SubscriptionTier.FREE,
            SubscriptionTier.BRONZE,
            SubscriptionTier.SILVER,
            SubscriptionTier.GOLD,
            SubscriptionTier.PLATINUM
        ]
        
        current_tier_index = tier_order.index(subscription.tier)
        if current_tier_index < len(tier_order) - 1:
            suggested_tier = tier_order[current_tier_index + 1].value
        else:
            suggested_tier = "platinum"
        
        raise QuotaExceeded("quizzes", current_usage, limit, suggested_tier)
    
    logger.info(f"✅ Quota check passed for {current_user.username}")
    return subscription

def increment_quiz_usage(subscription: Subscription, db: Session):
    """Incrémente l'usage des quiz."""
    logger.info(f"📈 Incrementing quiz usage for user_id: {subscription.user_id}")
    logger.info(f"   Before: {subscription.quizzes_this_month}")
    
    # ⭐ SIMPLE INCREMENT (pas de JSON, pas de flag_modified)
    subscription.increment_usage("quizzes")
    
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"   After: {subscription.quizzes_this_month}")
    logger.info(f"✅ Quiz usage updated: {subscription.quizzes_this_month}/{subscription.get_limits()['quizzes_per_month']}")

def increment_ai_hint_usage(subscription: Subscription, db: Session):
    """Incrémente l'usage des AI hints."""
    logger.info(f"📈 Incrementing AI hint usage for user_id: {subscription.user_id}")
    
    subscription.increment_usage("ai_hints")
    
    db.commit()
    db.refresh(subscription)
    
    logger.info(f"✅ AI hint usage updated: {subscription.ai_hints_this_month}/{subscription.get_limits()['ai_hints_per_month']}")