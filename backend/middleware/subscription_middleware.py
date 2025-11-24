"""
Middleware pour vérifier automatiquement les quotas avant certaines actions.
"""

from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
import logging

from backend.models.database import SessionLocal
from backend.models.user import User
from backend.models.subscription import Subscription

logger = logging.getLogger("backend.app")

async def check_quiz_quota(request: Request):
    """
    Middleware pour vérifier le quota de quiz.
    À utiliser sur les endpoints de création de quiz.
    """
    # Récupérer l'utilisateur depuis le token
    # (déjà fait par get_current_user, on peut skip pour l'instant)
    pass

def require_tier(required_tier: str):
    """
    Décorateur pour vérifier que l'utilisateur a le tier requis.
    
    Usage:
        @router.get("/premium-feature")
        @require_tier("gold")
        def premium_feature(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Vérifier le tier
            # TODO: Implémenter
            return await func(*args, **kwargs)
        return wrapper
    return decorator