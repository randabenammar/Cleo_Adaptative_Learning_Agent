from sqlalchemy import Column, Integer, String, Text, JSON, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String(200), unique=True, index=True)  # Identifiant unique
    
    # Métadonnées
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    subject_name = Column(String(100))
    topic = Column(String(200))
    
    # Taxonomie Bloom
    bloom_level = Column(Integer, default=2)  # 1-6
    bloom_label = Column(String(50))  # Remember, Understand, etc.
    
    # Type et difficulté
    question_type = Column(String(50))  # mcq, open_ended, matching, true_false
    difficulty = Column(Integer, default=3)  # 1-5
    points = Column(Integer, default=10)
    
    # Contenu de la question
    question_text = Column(Text, nullable=False)
    question_data = Column(JSON)  # Stocke options, réponses, etc. selon type
    
    # Métadonnées supplémentaires
    created_at = Column(DateTime, default=datetime.utcnow)
    times_used = Column(Integer, default=0)
    avg_success_rate = Column(Float, default=0.0)
    
    # Relations
    subject = relationship("Subject", backref="questions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "subject_name": self.subject_name,
            "topic": self.topic,
            "bloom_level": self.bloom_level,
            "bloom_label": self.bloom_label,
            "question_type": self.question_type,
            "difficulty": self.difficulty,
            "points": self.points,
            "question_text": self.question_text,
            "question_data": self.question_data,
            "times_used": self.times_used,
            "avg_success_rate": self.avg_success_rate
        }