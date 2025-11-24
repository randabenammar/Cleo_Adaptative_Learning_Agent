"""
Script pour initialiser les plans d'abonnement.
"""

import sys
sys.path.insert(0, '.')

from models.database import SessionLocal, engine, Base
from models.subscription import SubscriptionPlan, SubscriptionTier, Subscription
from models.user import User

def init_plans():
    """Initialise les plans d'abonnement."""
    db = SessionLocal()
    
    try:
        print("🎯 Initializing subscription plans...")
        
        plans = [
            {
                "tier": SubscriptionTier.FREE,
                "name": "Free",
                "description": "Perfect to get started with adaptive learning",
                "price_monthly": 0.0,
                "price_yearly": 0.0,
                "display_order": 1,
                "badge": None
            },
            {
                "tier": SubscriptionTier.BRONZE,
                "name": "Bronze",
                "description": "For casual learners who want more practice",
                "price_monthly": 9.99,
                "price_yearly": 99.99,  # 2 mois gratuits
                "display_order": 2,
                "badge": None
            },
            {
                "tier": SubscriptionTier.SILVER,
                "name": "Silver",
                "description": "For dedicated students aiming for excellence",
                "price_monthly": 19.99,
                "price_yearly": 199.99,
                "display_order": 3,
                "badge": "Popular"
            },
            {
                "tier": SubscriptionTier.GOLD,
                "name": "Gold",
                "description": "For serious learners with ambitious goals",
                "price_monthly": 39.99,
                "price_yearly": 399.99,
                "display_order": 4,
                "badge": "Best Value"
            },
            {
                "tier": SubscriptionTier.PLATINUM,
                "name": "Platinum",
                "description": "Ultimate learning experience with VIP support",
                "price_monthly": 79.99,
                "price_yearly": 799.99,
                "display_order": 5,
                "badge": "Premium"
            }
        ]
        
        for plan_data in plans:
            existing = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.tier == plan_data["tier"]
            ).first()
            
            if not existing:
                plan = SubscriptionPlan(**plan_data)
                db.add(plan)
                print(f"✅ Created plan: {plan_data['name']}")
            else:
                print(f"⏭️  Plan already exists: {plan_data['name']}")
        
        db.commit()
        print("\n✅ All subscription plans initialized!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def assign_free_subscriptions():
    """Assigne un abonnement gratuit à tous les utilisateurs existants."""
    db = SessionLocal()
    
    try:
        print("\n🎁 Assigning free subscriptions to existing users...")
        
        users = db.query(User).all()
        
        for user in users:
            if not user.subscription:
                sub = Subscription(
                    user_id=user.id,
                    tier=SubscriptionTier.FREE,
                    status="active"
                )
                db.add(sub)
                print(f"✅ Assigned FREE to: {user.username}")
        
        db.commit()
        print("\n✅ All users have subscriptions!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    # Initialiser les plans
    init_plans()
    
    # Assigner FREE à tous les users existants
    assign_free_subscriptions()