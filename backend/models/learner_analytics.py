from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from datetime import datetime
from .database import Base


class LearnerAnalytics(Base):
    """
    Modèle pour stocker des analytics pré-calculées (cache).
    Permet d'éviter de recalculer à chaque requête.
    """
    __tablename__ = "learner_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(String(100), index=True, nullable=False, unique=True)
    
    # Métriques globales
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    total_questions_answered = Column(Integer, default=0)
    total_correct_answers = Column(Integer, default=0)
    overall_accuracy = Column(Float, default=0.0)
    total_time_minutes = Column(Float, default=0.0)
    
    # Bloom stats (JSON)
    bloom_stats = Column(JSON)  # Stats par niveau Bloom
    current_average_bloom_level = Column(Float, default=1.0)
    
    # Subject stats (JSON)
    subject_stats = Column(JSON)  # Liste de stats par sujet
    
    # Temporal patterns (JSON)
    temporal_stats = Column(JSON)
    
    # Strengths & Weaknesses
    strengths = Column(JSON)  # Liste de forces
    weaknesses = Column(JSON)  # Liste de faiblesses
    
    # Recommendations (JSON)
    recommendations = Column(JSON)
    
    # Metadata
    last_calculated = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "total_sessions": self.total_sessions,
            "completed_sessions": self.completed_sessions,
            "total_questions_answered": self.total_questions_answered,
            "total_correct_answers": self.total_correct_answers,
            "overall_accuracy": self.overall_accuracy,
            "total_time_minutes": self.total_time_minutes,
            "bloom_stats": self.bloom_stats,
            "current_average_bloom_level": self.current_average_bloom_level,
            "subject_stats": self.subject_stats,
            "temporal_stats": self.temporal_stats,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "last_calculated": self.last_calculated.isoformat() if self.last_calculated else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }