from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class LearnerProgress(Base):
    __tablename__ = "learner_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(String(100), index=True, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    
    current_bloom_level = Column(Integer, default=1)  # 1-6
    completion_percentage = Column(Float, default=0.0)
    total_time_spent_hours = Column(Float, default=0.0)
    
    completed_modules = Column(JSON, default=[])  # Liste des modules terminés
    current_module = Column(Integer, default=1)
    
    last_activity_date = Column(DateTime, default=datetime.utcnow)
    started_date = Column(DateTime, default=datetime.utcnow)
    
    # Relation
    subject = relationship("Subject")
    
    def to_dict(self):
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "subject_id": self.subject_id,
            "current_bloom_level": self.current_bloom_level,
            "completion_percentage": self.completion_percentage,
            "total_time_spent_hours": self.total_time_spent_hours,
            "completed_modules": self.completed_modules,
            "current_module": self.current_module,
            "last_activity_date": self.last_activity_date.isoformat() if self.last_activity_date else None,
            "started_date": self.started_date.isoformat() if self.started_date else None
        }