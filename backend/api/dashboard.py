from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging 

from backend.api.auth import get_current_active_user
from backend.models.database import get_db
from backend.agents.analytics_agent import AnalyticsAgent
from datetime import datetime, timedelta

from backend.models.quiz_session import QuizSession
from backend.models.subscription import Subscription
from backend.models.user import User

logger = logging.getLogger("backend.app")
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def get_analytics_agent():
    from backend.app import _state
    agent = _state.get("analytics_agent")
    if not agent:
        raise HTTPException(status_code=503, detail="AnalyticsAgent not initialized")
    return agent


@router.get("/{learner_id}")
def get_learner_dashboard(
    learner_id: str,
    db: Session = Depends(get_db),
    analytics_agent: AnalyticsAgent = Depends(get_analytics_agent)
):
    """
    Récupère le dashboard complet d'un apprenant avec toutes les analytics.
    """
    try:
        analytics = analytics_agent.generate_learner_analytics(learner_id, db)
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")


@router.get("/{learner_id}/bloom-stats")
def get_bloom_stats(
    learner_id: str,
    db: Session = Depends(get_db),
    analytics_agent: AnalyticsAgent = Depends(get_analytics_agent)
):
    """Récupère uniquement les stats Bloom."""
    try:
        analytics = analytics_agent.generate_learner_analytics(learner_id, db)
        return analytics["bloom_stats"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{learner_id}/recommendations")
def get_recommendations(
    learner_id: str,
    db: Session = Depends(get_db),
    analytics_agent: AnalyticsAgent = Depends(get_analytics_agent)
):
    """Récupère uniquement les recommandations."""
    try:
        analytics = analytics_agent.generate_learner_analytics(learner_id, db)
        return {
            "recommendations": analytics["recommendations"],
            "strengths": analytics["strengths"],
            "weaknesses": analytics["weaknesses"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_quiz_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère l'historique des quiz selon le plan."""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        limits = subscription.get_limits() if subscription else {"analytics_history_days": 7}
        history_days = limits["analytics_history_days"]
        
        # ⭐ Calculer la date limite
        cutoff_date = datetime.utcnow() - timedelta(days=history_days)
        
        # Récupérer sessions
        learner_id = f"user_{current_user.id}"
        sessions = db.query(QuizSession).filter(
            QuizSession.learner_id == learner_id,
            QuizSession.completed_at >= cutoff_date  # ⭐ Filtrer par date
        ).order_by(QuizSession.completed_at.desc()).all()
        
        return {
            "sessions": [s.to_dict() for s in sessions],
            "history_days": history_days,
            "total_sessions": len(sessions)
        }
        
    except Exception as e:
        logger.exception(f"❌ Error fetching history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching history: {str(e)}"
        )