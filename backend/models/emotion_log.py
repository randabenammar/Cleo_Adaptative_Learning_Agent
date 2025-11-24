from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from datetime import datetime
from .database import Base


class EmotionLog(Base):
    """
    Log des émotions détectées pendant les sessions d'apprentissage.
    """
    __tablename__ = "emotion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(String(100), index=True, nullable=False)
    
    # Session/Contexte
    quiz_session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    
    # Émotions détectées (scores 0-1)
    happy = Column(Float, default=0.0)
    sad = Column(Float, default=0.0)
    angry = Column(Float, default=0.0)
    fear = Column(Float, default=0.0)
    disgust = Column(Float, default=0.0)
    surprise = Column(Float, default=0.0)
    neutral = Column(Float, default=0.0)
    
    # Métriques dérivées
    stress_level = Column(Float, default=0.0)  # Calculé: fear + angry + disgust
    confidence_level = Column(Float, default=0.0)  # Calculé: happy - (sad + fear)
    
    # Metadata
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    detection_method = Column(String(50))  # "webcam", "text_analysis", "performance"
    
    # Données brutes (optionnel)
    raw_data = Column(JSON)
    
    def to_dict(self):
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "quiz_session_id": self.quiz_session_id,
            "happy": self.happy,
            "sad": self.sad,
            "angry": self.angry,
            "fear": self.fear,
            "disgust": self.disgust,
            "surprise": self.surprise,
            "neutral": self.neutral,
            "stress_level": self.stress_level,
            "confidence_level": self.confidence_level,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "detection_method": self.detection_method
        }
    
    def calculate_derived_metrics(self):
        """Calcule stress et confidence à partir des émotions de base."""
        self.stress_level = min(1.0, (self.fear + self.angry + self.disgust) / 3)
        self.confidence_level = max(0.0, min(1.0, self.happy - (self.sad + self.fear) / 2))