from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship

from datetime import datetime
import enum
from .database import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    """
    Modèle utilisateur avec authentification et rôles.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Credentials
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(200))
    avatar_url = Column(String(500))
    bio = Column(String(1000))
    
    # Role & Status
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Preferences
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # ⭐ AJOUTER cette relation
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    # Dans la classe User, ajouter :
    #preferences = relationship("UserPreference", back_populates="user", uselist=False)
    # Relationships (mise à jour des autres modèles plus tard)
    # quiz_sessions = relationship("QuizSession", back_populates="user")
    # learner_progress = relationship("LearnerProgress", back_populates="user")
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "role": self.role.value if self.role else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "preferred_language": self.preferred_language,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "subscription": self.subscription.to_dict() if self.subscription else None
        }
    
    def to_public_dict(self):
        """Version publique sans infos sensibles."""
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "role": self.role.value if self.role else None
        }