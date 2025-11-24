from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from backend.models.database import get_db
from backend.models.emotion_log import EmotionLog
from backend.models.support_intervention import SupportIntervention
from backend.models.answer import Answer
from backend.models.quiz_session import QuizSession
from backend.agents.support_agent import SupportAgent

router = APIRouter(prefix="/api/emotion-support", tags=["emotion_support"])


def get_support_agent():
    from backend.app import _state
    agent = _state.get("support_agent")
    if not agent:
        raise HTTPException(status_code=503, detail="SupportAgent not initialized")
    return agent


# Modèles Pydantic
class EmotionData(BaseModel):
    learner_id: str
    quiz_session_id: Optional[int] = None
    question_id: Optional[int] = None
    happy: float = 0.0
    sad: float = 0.0
    angry: float = 0.0
    fear: float = 0.0
    disgust: float = 0.0
    surprise: float = 0.0
    neutral: float = 0.0
    detection_method: str = "webcam"


class InterventionFeedback(BaseModel):
    intervention_id: int
    was_helpful: bool
    action_taken: str  # break_taken, continued, dismissed


@router.post("/log-emotion")
def log_emotion(
    payload: EmotionData,
    db: Session = Depends(get_db)
):
    """
    Enregistre une émotion détectée.
    """
    try:
        emotion_log = EmotionLog(
            learner_id=payload.learner_id,
            quiz_session_id=payload.quiz_session_id,
            question_id=payload.question_id,
            happy=payload.happy,
            sad=payload.sad,
            angry=payload.angry,
            fear=payload.fear,
            disgust=payload.disgust,
            surprise=payload.surprise,
            neutral=payload.neutral,
            detection_method=payload.detection_method
        )
        
        # Calculer métriques dérivées
        emotion_log.calculate_derived_metrics()
        
        db.add(emotion_log)
        db.commit()
        db.refresh(emotion_log)
        
        return {
            "success": True,
            "emotion_log": emotion_log.to_dict()
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging emotion: {str(e)}")


@router.post("/check-intervention/{learner_id}")
def check_intervention(
    learner_id: str,
    quiz_session_id: Optional[int] = None,
    db: Session = Depends(get_db),
    support_agent: SupportAgent = Depends(get_support_agent)
):
    """
    Vérifie si une intervention est nécessaire pour cet apprenant.
    """
    try:
        # Récupérer émotions récentes (dernières 5 minutes)
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        recent_emotions = db.query(EmotionLog).filter(
            EmotionLog.learner_id == learner_id,
            EmotionLog.detected_at >= five_min_ago
        ).order_by(EmotionLog.detected_at.desc()).limit(10).all()
        
        emotions_data = [e.to_dict() for e in recent_emotions]
        
        # Récupérer réponses récentes
        recent_answers = []
        if quiz_session_id:
            answers = db.query(Answer).filter(
                Answer.learner_id == learner_id,
                Answer.quiz_session_id == quiz_session_id
            ).order_by(Answer.answered_at.desc()).limit(5).all()
            recent_answers = [a.to_dict() for a in answers]
        
        # Contexte session
        learner_context = {}
        if quiz_session_id:
            session = db.query(QuizSession).filter(QuizSession.id == quiz_session_id).first()
            if session and session.started_at:
                duration = (datetime.utcnow() - session.started_at).total_seconds() / 60
                learner_context = {
                    "session_duration_minutes": duration,
                    "current_subject": session.subject_name,
                    "bloom_level": session.bloom_level
                }
        
        # Vérifier besoin d'intervention
        decision = support_agent.should_intervene(
            recent_emotions=emotions_data,
            recent_answers=recent_answers,
            learner_context=learner_context
        )
        
        # Si intervention nécessaire, générer message
        if decision["should_intervene"]:
            support_message = support_agent.generate_support_message(
                intervention_type=decision["intervention_type"],
                learner_name=learner_id.split('_')[0].title(),
                context=learner_context
            )
            
            # Enregistrer intervention
            intervention = SupportIntervention(
                learner_id=learner_id,
                quiz_session_id=quiz_session_id,
                intervention_type=decision["intervention_type"],
                severity=decision["severity"],
                message=support_message.get("message"),
                suggestions=support_message.get("suggestions"),
                recommended_action=support_message.get("recommended_action")
            )
            
            db.add(intervention)
            db.commit()
            db.refresh(intervention)
            
            return {
                "should_intervene": True,
                "decision": decision,
                "support_message": support_message,
                "intervention": intervention.to_dict()
            }
        
        return {
            "should_intervene": False,
            "decision": decision
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error checking intervention: {str(e)}")


@router.post("/intervention-feedback")
def submit_intervention_feedback(
    payload: InterventionFeedback,
    db: Session = Depends(get_db)
):
    """
    Enregistre le feedback de l'apprenant sur une intervention.
    """
    try:
        intervention = db.query(SupportIntervention).filter(
            SupportIntervention.id == payload.intervention_id
        ).first()
        
        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention not found")
        
        intervention.was_helpful = payload.was_helpful
        intervention.action_taken = payload.action_taken
        intervention.resolved_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Feedback recorded"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")


@router.get("/stress-techniques")
def get_stress_techniques(
    support_agent: SupportAgent = Depends(get_support_agent)
):
    """
    Récupère les techniques de gestion du stress.
    """
    return {
        "techniques": support_agent.get_stress_relief_techniques()
    }


@router.get("/motivational-quotes")
def get_motivational_quotes(
    support_agent: SupportAgent = Depends(get_support_agent)
):
    """
    Récupère des citations motivationnelles.
    """
    return {
        "quotes": support_agent.get_motivational_quotes()
    }


@router.get("/emotion-history/{learner_id}")
def get_emotion_history(
    learner_id: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique émotionnel d'un apprenant.
    """
    try:
        time_ago = datetime.utcnow() - timedelta(hours=hours)
        
        emotions = db.query(EmotionLog).filter(
            EmotionLog.learner_id == learner_id,
            EmotionLog.detected_at >= time_ago
        ).order_by(EmotionLog.detected_at.asc()).all()
        
        return {
            "learner_id": learner_id,
            "period_hours": hours,
            "emotions": [e.to_dict() for e in emotions]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching emotion history: {str(e)}")


@router.get("/interventions/{learner_id}")
def get_interventions_history(
    learner_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique des interventions pour un apprenant.
    """
    try:
        interventions = db.query(SupportIntervention).filter(
            SupportIntervention.learner_id == learner_id
        ).order_by(SupportIntervention.triggered_at.desc()).limit(limit).all()
        
        return {
            "learner_id": learner_id,
            "interventions": [i.to_dict() for i in interventions]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching interventions: {str(e)}")