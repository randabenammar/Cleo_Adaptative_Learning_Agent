from sqlalchemy import Column, Integer, String, Text, Float, JSON
from .database import Base


class Subject(Base):
    """
    Modèle pour les sujets d'apprentissage.
    """
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50))
    summary = Column(Text)
    key_concepts = Column(JSON)
    prerequisites = Column(JSON)
    learning_objectives = Column(JSON)
    estimated_duration_hours = Column(Integer)
    difficulty_rating = Column(Float)
    
    def to_dict(self):
        """Convertit le sujet en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "summary": self.summary,
            "key_concepts": self.key_concepts,
            "prerequisites": self.prerequisites,
            "learning_objectives": self.learning_objectives,
            "estimated_duration_hours": self.estimated_duration_hours,
            "difficulty_rating": self.difficulty_rating
        }