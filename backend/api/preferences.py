"""
API pour les préférences utilisateur.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import json

from backend.models.database import get_db
from backend.models.user import User
from backend.models.subscription import Subscription
from backend.models.user_preferences import UserPreference
from backend.api.auth import get_current_active_user

logger = logging.getLogger("backend.app")
router = APIRouter(prefix="/api/preferences", tags=["preferences"])

class UpdateFavoritesRequest(BaseModel):
    subject_ids: list[int]

@router.get("/favorites")
def get_favorite_subjects(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère les sujets favoris de l'utilisateur."""
    try:
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()
        
        if not preferences:
            return {"favorite_subject_ids": []}
        
        return {"favorite_subject_ids": preferences.favorite_subject_ids or []}
        
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
    """Met à jour les sujets favoris de l'utilisateur."""
    try:
        logger.info(f"📝 Updating favorites for {current_user.username}")
        
        # Vérifier la limite selon le tier
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if subscription:
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
        
        # Récupérer ou créer les préférences
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()
        
        if not preferences:
            preferences = UserPreference(user_id=current_user.id)
            db.add(preferences)
        
        # Mettre à jour
        preferences.favorite_subject_ids = payload.subject_ids
        
        db.commit()
        db.refresh(preferences)
        
        logger.info(f"✅ Favorites updated: {payload.subject_ids}")
        
        return {
            "success": True,
            "favorite_subject_ids": preferences.favorite_subject_ids
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