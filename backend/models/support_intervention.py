from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean
from datetime import datetime
from .database import Base


class SupportIntervention(Base):
    """
    Log des interventions de support effectuées.
    """
    __tablename__ = "support_interventions"
    
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(String(100), index=True, nullable=False)
    
    # Contexte
    quiz_session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=True)
    triggered_by_emotion_log_id = Column(Integer, ForeignKey("emotion_logs.id"), nullable=True)
    
    # Type et sévérité
    intervention_type = Column(String(50))  # stress_management, encouragement, etc.
    severity = Column(String(20))  # low, medium, high
    
    # Contenu
    message = Column(Text)
    suggestions = Column(JSON)  # Liste de suggestions
    recommended_action = Column(String(50))  # break, continue, review
    
    # Réponse de l'apprenant
    was_helpful = Column(Boolean, nullable=True)  # L'apprenant a-t-il trouvé ça utile?
    action_taken = Column(String(50), nullable=True)  # break_taken, continued, dismissed
    
    # Metadata
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "quiz_session_id": self.quiz_session_id,
            "intervention_type": self.intervention_type,
            "severity": self.severity,
            "message": self.message,
            "suggestions": self.suggestions,
            "recommended_action": self.recommended_action,
            "was_helpful": self.was_helpful,
            "action_taken": self.action_taken,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }