"""
Modèle pour les préférences utilisateur.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class UserPreference(Base):
    """Préférences de l'utilisateur (sujets préférés, etc.)."""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Liste des IDs de sujets favoris
    favorite_subject_ids = Column(JSON, default=list)
    
    # Dernière mise à jour
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation
    user = relationship("User", back_populates="preferences")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "favorite_subject_ids": self.favorite_subject_ids or [],
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }