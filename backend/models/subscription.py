import json
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from .database import Base

class SubscriptionTier(enum.Enum):
    """Niveaux d'abonnement."""
    FREE = "free"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class SubscriptionStatus(enum.Enum):
    """Statut de l'abonnement."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"

class Subscription(Base):
    """Modèle pour les abonnements utilisateurs."""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Tier et statut
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    
    # Dates
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Paiement
    stripe_subscription_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    amount_paid = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    
    # ⭐ NOUVEAU : Utilisation avec colonnes séparées (plus fiable que JSON)
    quizzes_this_month = Column(Integer, default=0)
    questions_this_month = Column(Integer, default=0)
    ai_hints_this_month = Column(Integer, default=0)
    usage_reset_date = Column(DateTime, default=lambda: datetime.utcnow().replace(day=1))
     # ⭐ NOUVEAU : Sujets favoris (stockés en JSON)
    favorite_subject_ids = Column(Text, default="[]")
    # Relations
    user = relationship("User", back_populates="subscription")
    
    def get_favorite_subjects(self):
        """Retourne la liste des IDs de sujets favoris."""
        try:
            if not self.favorite_subject_ids:
                return []
            return json.loads(self.favorite_subject_ids)
        except:
            return []
    
    def set_favorite_subjects(self, subject_ids: list):
        """Définit les sujets favoris."""
        self.favorite_subject_ids = json.dumps(subject_ids)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tier": self.tier.value,
            "status": self.status.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "amount_paid": self.amount_paid,
            "currency": self.currency,
            "usage": {
                "quizzes_this_month": self.quizzes_this_month,
                "questions_this_month": self.questions_this_month,
                "ai_hints_this_month": self.ai_hints_this_month,
                "reset_date": self.usage_reset_date.isoformat() if self.usage_reset_date else None
            },
            "is_active": self.is_active(),
            "limits": self.get_limits(),
            "features": self.get_features()
        }
    
    def is_active(self):
        """Vérifie si l'abonnement est actif."""
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        if self.end_date and datetime.utcnow() > self.end_date:
            return False
        return True
    
    def get_limits(self):
        """Retourne les limites selon le tier."""
        limits = {
            SubscriptionTier.FREE: {
                "quizzes_per_month": 5,
                "questions_per_quiz": 5,
                "subjects_access": 2,
                "ai_hints_per_month": 0,
                "analytics_history_days": 7,
                "can_export_data": False
            },
            SubscriptionTier.BRONZE: {
                "quizzes_per_month": 20,
                "questions_per_quiz": 10,
                "subjects_access": 5,
                "ai_hints_per_month": 10,
                "analytics_history_days": 30,
                "can_export_data": True
            },
            SubscriptionTier.SILVER: {
                "quizzes_per_month": 50,
                "questions_per_quiz": 15,
                "subjects_access": 999,
                "ai_hints_per_month": 50,
                "analytics_history_days": 90,
                "can_export_data": True
            },
            SubscriptionTier.GOLD: {
                "quizzes_per_month": 150,
                "questions_per_quiz": 20,
                "subjects_access": 999,
                "ai_hints_per_month": 200,
                "analytics_history_days": 365,
                "can_export_data": True
            },
            SubscriptionTier.PLATINUM: {
                "quizzes_per_month": 999,
                "questions_per_quiz": 30,
                "subjects_access": 999,
                "ai_hints_per_month": 999,
                "analytics_history_days": 999,
                "can_export_data": True
            }
        }
        return limits.get(self.tier, limits[SubscriptionTier.FREE])
    
    def get_features(self):
        """Retourne les features selon le tier."""
        features = {
            SubscriptionTier.FREE: [
                "Basic quizzes",
                "Limited analytics",
                "2 subjects access"
            ],
            SubscriptionTier.BRONZE: [
                "20 quizzes/month",
                "10 questions/quiz",
                "5 subjects access",
                "Basic AI hints",
                "30-day analytics",
                "Export data (PDF)"
            ],
            SubscriptionTier.SILVER: [
                "50 quizzes/month",
                "15 questions/quiz",
                "All subjects access",
                "50 AI hints/month",
                "90-day analytics",
                "Export data (PDF, CSV)",
                "Priority support"
            ],
            SubscriptionTier.GOLD: [
                "150 quizzes/month",
                "20 questions/quiz",
                "All subjects access",
                "200 AI hints/month",
                "1-year analytics",
                "Export data (all formats)",
                "Priority support",
                "Custom learning paths",
                "Advanced analytics"
            ],
            SubscriptionTier.PLATINUM: [
                "Unlimited quizzes",
                "30 questions/quiz",
                "All subjects access",
                "Unlimited AI hints",
                "Lifetime analytics",
                "Export data (all formats)",
                "VIP support 24/7",
                "Custom learning paths",
                "Advanced analytics",
                "Personal AI tutor",
                "Certificate generation"
            ]
        }
        return features.get(self.tier, features[SubscriptionTier.FREE])
    
    def check_quota(self, quota_type: str):
        """Vérifie si l'utilisateur a dépassé son quota."""
        limits = self.get_limits()
        
        # Reset mensuel si nécessaire
        if datetime.utcnow() > self.usage_reset_date + timedelta(days=30):
            self.quizzes_this_month = 0
            self.questions_this_month = 0
            self.ai_hints_this_month = 0
            self.usage_reset_date = datetime.utcnow().replace(day=1)
        
        if quota_type == "quiz":
            return self.quizzes_this_month < limits["quizzes_per_month"]
        elif quota_type == "ai_hint":
            return self.ai_hints_this_month < limits["ai_hints_per_month"]
        
        return True
    
    def increment_usage(self, usage_type: str):
        """Incrémente l'utilisation."""
        if usage_type == "quizzes":
            self.quizzes_this_month += 1
        elif usage_type == "questions":
            self.questions_this_month += 1
        elif usage_type == "ai_hints":
            self.ai_hints_this_month += 1


class SubscriptionPlan(Base):
    """Plans d'abonnement disponibles."""
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    tier = Column(SQLEnum(SubscriptionTier), unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    
    price_monthly = Column(Float, nullable=False)
    price_yearly = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    
    stripe_price_id_monthly = Column(String, nullable=True)
    stripe_price_id_yearly = Column(String, nullable=True)
    stripe_product_id = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    badge = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "tier": self.tier.value,
            "name": self.name,
            "description": self.description,
            "price_monthly": self.price_monthly,
            "price_yearly": self.price_yearly,
            "currency": self.currency,
            "badge": self.badge,
            "display_order": self.display_order
        }