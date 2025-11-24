from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(200), unique=True, index=True)
    
    # Apprenant
    learner_id = Column(String(100), index=True, nullable=False)
    
    # Sujet et contexte
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    subject_name = Column(String(100))
    topic = Column(String(200))
    
    # Configuration du quiz
    bloom_level = Column(Integer)
    question_type = Column(String(50))
    num_questions = Column(Integer)
    
    # État de la session
    status = Column(String(50), default="in_progress")  # in_progress, completed, abandoned
    current_question_index = Column(Integer, default=0)
    
    # Scores
    total_questions = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_points_earned = Column(Float, default=0.0)
    total_points_possible = Column(Float, default=0.0)
    
    # Temps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    
    # Données du quiz
    questions_data = Column(JSON)  # Liste des questions dans cette session
    
    # Adaptation
    initial_bloom_level = Column(Integer)
    final_bloom_level = Column(Integer, nullable=True)
    level_changed = Column(Boolean, default=False)
    
    # Relations
    subject = relationship("Subject")
    answers = relationship("Answer", back_populates="quiz_session", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "learner_id": self.learner_id,
            "subject_name": self.subject_name,
            "topic": self.topic,
            "bloom_level": self.bloom_level,
            "question_type": self.question_type,
            "status": self.status,
            "current_question_index": self.current_question_index,
            "total_questions": self.total_questions,
            "questions_answered": self.questions_answered,
            "correct_answers": self.correct_answers,
            "total_points_earned": self.total_points_earned,
            "total_points_possible": self.total_points_possible,
            "score_percentage": (self.total_points_earned / self.total_points_possible * 100) if self.total_points_possible > 0 else 0,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "time_spent_seconds": self.time_spent_seconds,
            "questions_data": self.questions_data,
            "initial_bloom_level": self.initial_bloom_level,
            "final_bloom_level": self.final_bloom_level,
            "level_changed": self.level_changed
        }