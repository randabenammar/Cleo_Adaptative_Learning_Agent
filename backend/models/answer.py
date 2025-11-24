from sqlalchemy import Column, Integer, String, Text, JSON, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    quiz_session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    learner_id = Column(String(100), index=True, nullable=False)
    
    # Réponse de l'apprenant
    user_answer = Column(Text)  # Réponse textuelle
    user_answer_data = Column(JSON)  # Pour réponses complexes (matching, etc.)
    
    # Évaluation
    is_correct = Column(Boolean)
    points_earned = Column(Float, default=0.0)
    points_possible = Column(Float)
    score_percentage = Column(Float)  # 0-100
    
    # Feedback
    feedback = Column(Text)
    explanation = Column(Text)
    evaluation_data = Column(JSON)  # Détails de l'évaluation (strengths, weaknesses, etc.)
    
    # Timing
    time_taken_seconds = Column(Integer)
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Méthode d'évaluation
    evaluation_method = Column(String(50))  # ai, keyword_matching, exact_match
    confidence = Column(Float)  # Confiance de l'évaluation (0-1)
    
    # Relations
    quiz_session = relationship("QuizSession", back_populates="answers")
    question = relationship("Question")
    
    def to_dict(self):
        return {
            "id": self.id,
            "quiz_session_id": self.quiz_session_id,
            "question_id": self.question_id,
            "learner_id": self.learner_id,
            "user_answer": self.user_answer,
            "is_correct": self.is_correct,
            "points_earned": self.points_earned,
            "points_possible": self.points_possible,
            "score_percentage": self.score_percentage,
            "feedback": self.feedback,
            "explanation": self.explanation,
            "evaluation_data": self.evaluation_data,
            "time_taken_seconds": self.time_taken_seconds,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
            "evaluation_method": self.evaluation_method,
            "confidence": self.confidence
        }