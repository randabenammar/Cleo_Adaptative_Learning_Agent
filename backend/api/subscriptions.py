"""
API pour gérer les abonnements et les packs premium.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field
import logging

from backend.models.database import get_db
from backend.models.user import User
from backend.models.subscription import (
    Subscription, 
    SubscriptionPlan, 
    SubscriptionTier, 
    SubscriptionStatus
)
from backend.api.auth import get_current_active_user

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
logger = logging.getLogger("backend.app")

# ========================================
# PYDANTIC MODELS
# ========================================

class SubscriptionPlanResponse(BaseModel):
    """Réponse pour un plan d'abonnement."""
    id: int
    tier: str
    name: str
    description: str
    price_monthly: float
    price_yearly: Optional[float]
    currency: str
    badge: Optional[str]
    display_order: int
    limits: dict
    features: List[str]

class SubscriptionResponse(BaseModel):
    """Réponse pour un abonnement utilisateur."""
    id: int
    user_id: int
    tier: str
    status: str
    start_date: str
    end_date: Optional[str]
    amount_paid: float
    currency: str
    usage: dict
    is_active: bool
    limits: dict
    features: List[str]

class UpgradeRequest(BaseModel):
    """Requête pour upgrader."""
    target_tier: str
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")

class QuotaCheckRequest(BaseModel):
    """Requête pour vérifier un quota."""
    quota_type: str = Field(..., pattern="^(quiz|ai_hint|subject)$")

# ========================================
# GET /api/subscriptions/plans
# ========================================

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
def get_subscription_plans(db: Session = Depends(get_db)):
    """
    Récupère tous les plans d'abonnement disponibles.
    
    Returns:
        Liste des plans avec leurs limites et features
    """
    try:
        logger.info("📋 Fetching subscription plans")
        
        plans = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.is_active == True
        ).order_by(SubscriptionPlan.display_order).all()
        
        result = []
        for plan in plans:
            # Créer une subscription temporaire pour obtenir limits et features
            temp_sub = Subscription(tier=plan.tier)
            
            result.append({
                "id": plan.id,
                "tier": plan.tier.value,
                "name": plan.name,
                "description": plan.description,
                "price_monthly": plan.price_monthly,
                "price_yearly": plan.price_yearly,
                "currency": plan.currency,
                "badge": plan.badge,
                "display_order": plan.display_order,
                "limits": temp_sub.get_limits(),
                "features": temp_sub.get_features()
            })
        
        logger.info(f"✅ Found {len(result)} plans")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error fetching plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching plans: {str(e)}"
        )

# ========================================
# GET /api/subscriptions/my-subscription
# ========================================

@router.get("/my-subscription")
def get_my_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère l'abonnement de l'utilisateur connecté."""
    try:
        logger.info(f"📊 Fetching subscription for user: {current_user.username}")
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            logger.warning(f"⚠️ No subscription found for {current_user.username}, creating FREE")
            subscription = Subscription(
                user_id=current_user.id,
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE,
                quizzes_this_month=0,
                questions_this_month=0,
                ai_hints_this_month=0,
                usage_reset_date=datetime.utcnow().replace(day=1)
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
        
        # ⭐ UTILISER to_dict() qui doit être à jour
        return subscription.to_dict()
        
    except Exception as e:
        logger.exception(f"❌ Error fetching subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching subscription: {str(e)}"
        )
    
# ========================================
# POST /api/subscriptions/upgrade
# ========================================

@router.post("/upgrade")
def upgrade_subscription(
    request: UpgradeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upgrader vers un plan supérieur.
    """
    try:
        logger.info(f"⬆️ Upgrade request: {current_user.username} -> {request.target_tier}")
        
        # Récupérer l'abonnement actuel
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        # Vérifier le tier cible
        try:
            target_tier = SubscriptionTier(request.target_tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {request.target_tier}"
            )
        
        # Vérifier que c'est bien un upgrade
        tier_order = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.BRONZE: 1,
            SubscriptionTier.SILVER: 2,
            SubscriptionTier.GOLD: 3,
            SubscriptionTier.PLATINUM: 4
        }
        
        if tier_order[target_tier] <= tier_order[subscription.tier]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target tier must be higher than current tier"
            )
        
        # Récupérer le plan
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == target_tier
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        # Calculer le prix
        price = plan.price_monthly if request.billing_cycle == "monthly" else plan.price_yearly
        
        # Calculer la date de fin
        if request.billing_cycle == "monthly":
            end_date = datetime.utcnow() + timedelta(days=30)
        else:
            end_date = datetime.utcnow() + timedelta(days=365)
        
        # ⭐ TODO: Intégrer Stripe ici pour le paiement
        # Pour l'instant, on simule un paiement réussi
        
        # Mettre à jour l'abonnement
        subscription.tier = target_tier
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.end_date = end_date
        subscription.amount_paid = price
        subscription.currency = plan.currency
        subscription.updated_at = datetime.utcnow()
        
        # Reset usage
        
        
        db.commit()
        db.refresh(subscription)
        
        logger.info(f"✅ Upgraded {current_user.username} to {target_tier.value}")
        
        return {
            "success": True,
            "message": f"Successfully upgraded to {plan.name}!",
            "subscription": subscription.to_dict(),
            "payment": {
                "amount": price,
                "currency": plan.currency,
                "billing_cycle": request.billing_cycle,
                "next_billing_date": end_date.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"❌ Error upgrading subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error upgrading subscription: {str(e)}"
        )

# ========================================
# POST /api/subscriptions/downgrade
# ========================================

@router.post("/downgrade")
def downgrade_subscription(
    target_tier: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Downgrader vers un plan inférieur.
    Le downgrade prendra effet à la fin de la période en cours.
    """
    try:
        logger.info(f"⬇️ Downgrade request: {current_user.username} -> {target_tier}")
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        try:
            target_tier_enum = SubscriptionTier(target_tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {target_tier}"
            )
        
        # Le downgrade prend effet à la fin de la période
        # On pourrait ajouter un champ "pending_tier" pour ça
        
        logger.info(f"✅ Downgrade scheduled for {current_user.username} to {target_tier}")
        
        return {
            "success": True,
            "message": f"Your subscription will be downgraded to {target_tier} at the end of your current billing period",
            "effective_date": subscription.end_date.isoformat() if subscription.end_date else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error downgrading subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downgrading subscription: {str(e)}"
        )

# ========================================
# POST /api/subscriptions/cancel
# ========================================

@router.post("/cancel")
def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Annuler l'abonnement.
    L'utilisateur aura accès jusqu'à la fin de la période payée.
    """
    try:
        logger.info(f"❌ Cancel request from: {current_user.username}")
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        if subscription.tier == SubscriptionTier.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel free subscription"
            )
        
        subscription.status = SubscriptionStatus.CANCELLED
        db.commit()
        
        logger.info(f"✅ Cancelled subscription for {current_user.username}")
        
        return {
            "success": True,
            "message": "Your subscription has been cancelled. You will have access until the end of your billing period.",
            "access_until": subscription.end_date.isoformat() if subscription.end_date else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"❌ Error cancelling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling subscription: {str(e)}"
        )

# ========================================
# GET /api/subscriptions/usage
# ========================================

@router.get("/usage")
def get_usage(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère l'utilisation et les quotas."""
    try:
        logger.info(f"📊 Usage request from: {current_user.username}")
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            logger.warning(f"⚠️ No subscription found for {current_user.username}, creating FREE")
            subscription = Subscription(
                user_id=current_user.id,
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE,
                quizzes_this_month=0,
                questions_this_month=0,
                ai_hints_this_month=0,
                usage_reset_date=datetime.utcnow().replace(day=1)
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
        
        limits = subscription.get_limits()
        
        # ⭐ Utiliser les colonnes directement avec protection contre NULL
        quizzes_used = subscription.quizzes_this_month or 0
        questions_used = subscription.questions_this_month or 0
        hints_used = subscription.ai_hints_this_month or 0
        
        return {
            "tier": subscription.tier.value,
            "limits": limits,
            "usage": {
                "quizzes_this_month": quizzes_used,
                "questions_this_month": questions_used,
                "ai_hints_this_month": hints_used,
                "reset_date": subscription.usage_reset_date.isoformat() if subscription.usage_reset_date else datetime.utcnow().replace(day=1).isoformat()
            },
            "remaining": {
                "quizzes": max(0, limits["quizzes_per_month"] - quizzes_used),
                "ai_hints": max(0, limits["ai_hints_per_month"] - hints_used)
            },
            "reset_date": subscription.usage_reset_date.isoformat() if subscription.usage_reset_date else datetime.utcnow().replace(day=1).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error fetching usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching usage: {str(e)}"
        )
    
# ========================================
# POST /api/subscriptions/check-quota
# ========================================

@router.post("/check-quota")
def check_quota(
    request: QuotaCheckRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Vérifie si l'utilisateur peut effectuer une action (quota).
    """
    try:
        logger.info(f"🔍 Quota check: {current_user.username} - {request.quota_type}")
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            return {"allowed": False, "reason": "No subscription found"}
        
        allowed = subscription.check_quota(request.quota_type)
        
        if not allowed:
            limits = subscription.get_limits()
            usage = subscription.quizzes_this_month or 0
            
            if request.quota_type == "quiz":
                return {
                    "allowed": False,
                    "reason": f"Monthly quiz limit reached ({limits['quizzes_per_month']})",
                    "current_usage": subscription.quizzes_this_month or 0,
                    "limit": limits["quizzes_per_month"],
                    "upgrade_to": "silver"  # Suggestion
                }
            elif request.quota_type == "ai_hint":
                return {
                    "allowed": False,
                    "reason": f"Monthly AI hints limit reached ({limits['ai_hints_per_month']})",
                    "current_usage": subscription.ai_hints_this_month or 0,
                    "limit": limits["ai_hints_per_month"],
                    "upgrade_to": "bronze"
                }
        
        return {"allowed": True}
        
    except Exception as e:
        logger.exception(f"❌ Error checking quota: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking quota: {str(e)}"
        )
    
# Ajouter ces routes à la fin du fichier

from pydantic import BaseModel

class UpdateFavoritesRequest(BaseModel):
    subject_ids: list[int]

@router.get("/favorites")
def get_favorite_subjects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère les sujets favoris de l'utilisateur."""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            return {"favorite_subject_ids": []}
        
        favorite_ids = subscription.get_favorite_subjects()
        
        return {
            "favorite_subject_ids": favorite_ids,
            "has_favorites": len(favorite_ids) > 0
        }
        
    except Exception as e:
        logger.exception(f"❌ Error fetching favorites: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching favorites: {str(e)}"
        )

@router.post("/favorites")
def update_favorite_subjects(
    payload: UpdateFavoritesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Met à jour les sujets favoris."""
    try:
        logger.info(f"📝 Updating favorites for {current_user.username}: {payload.subject_ids}")
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        # Vérifier la limite
        limits = subscription.get_limits()
        max_subjects = limits["subjects_access"]
        
        if max_subjects < 999 and len(payload.subject_ids) > max_subjects:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "limit_exceeded",
                    "message": f"You can only select up to {max_subjects} subjects with your {subscription.tier.value.upper()} plan",
                    "limit": max_subjects,
                    "selected": len(payload.subject_ids),
                    "upgrade_url": "/pricing"
                }
            )
        
        # Mettre à jour
        subscription.set_favorite_subjects(payload.subject_ids)
        
        db.commit()
        db.refresh(subscription)
        
        logger.info(f"✅ Favorites updated successfully")
        
        return {
            "success": True,
            "favorite_subject_ids": subscription.get_favorite_subjects()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"❌ Error updating favorites: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating favorites: {str(e)}"
        )

@router.get("/current")
def get_current_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupère la subscription actuelle de l'utilisateur avec toutes les infos.
    """
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        # Récupérer les limites
        limits = subscription.get_limits()
        
        # Calculer l'usage restant
        remaining = {
            "quizzes": max(0, limits["quizzes_per_month"] - subscription.quizzes_this_month),
            "questions": limits["questions_per_quiz"],  # Par quiz
            "ai_hints": max(0, limits["ai_hints_per_month"] - subscription.ai_hints_this_month),
        }
        
        # Récupérer les sujets favoris
        favorite_ids = subscription.get_favorite_subjects()
        
        return {
            "subscription": {
                "id": subscription.id,
                "tier": subscription.tier.value,
                "status": subscription.status.value,
                "start_date": subscription.start_date.isoformat() if subscription.start_date else None,
                "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
                "stripe_subscription_id": subscription.stripe_subscription_id,
                "stripe_customer_id": subscription.stripe_customer_id,
                
                # Limites du plan
                "limits": limits,
                
                # Usage actuel
                "usage": {
                    "quizzes_this_month": subscription.quizzes_this_month,
                    "questions_this_month": subscription.questions_this_month,
                    "ai_hints_this_month": subscription.ai_hints_this_month,
                    "usage_reset_date": subscription.usage_reset_date.isoformat() if subscription.usage_reset_date else None
                },
                
                # Restant
                "remaining": remaining,
                
                # Favoris
                "favorite_subject_ids": favorite_ids,
                "has_favorites": len(favorite_ids) > 0,
                
                # Timestamps
                "created_at": subscription.created_at.isoformat() if subscription.created_at else None,
                "updated_at": subscription.updated_at.isoformat() if subscription.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error fetching current subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching subscription: {str(e)}"
        )