"""
Script pour recréer les subscriptions avec les bons Enums.
"""

import sys
sys.path.insert(0, '.')

from models.database import SessionLocal
from models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from models.user import User

def recreate_subscriptions():
    db = SessionLocal()
    
    try:
        print("🔧 Recreating subscriptions with correct Enums...")
        
        # Récupérer tous les users
        users = db.query(User).all()
        
        print(f"Found {len(users)} users")
        
        for user in users:
            print(f"\n👤 User: {user.username} (ID: {user.id})")
            
            # Créer une nouvelle subscription FREE
            sub = Subscription(
                user_id=user.id,
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE  # ⭐ ENUM, pas string
            )
            
            db.add(sub)
            print(f"   ✅ Created FREE subscription with ACTIVE status")
        
        db.commit()
        print("\n✅ All subscriptions recreated!")
        
        # Vérifier
        print("\n🔍 Verification:")
        subscriptions = db.query(Subscription).all()
        for sub in subscriptions:
            print(f"   User ID {sub.user_id}: {sub.tier.value} - {sub.status.value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    recreate_subscriptions()