"""
Script pour corriger les statuts de subscription dans la DB.
"""

import sys
sys.path.insert(0, '.')

from models.database import SessionLocal
from models.subscription import Subscription, SubscriptionStatus

def fix_statuses():
    db = SessionLocal()
    
    try:
        print("🔧 Fixing subscription statuses...")
        
        # Récupérer toutes les subscriptions
        subscriptions = db.query(Subscription).all()
        
        print(f"Found {len(subscriptions)} subscriptions")
        
        for sub in subscriptions:
            print(f"\nUser ID: {sub.user_id}")
            print(f"  Current status type: {type(sub.status)}")
            print(f"  Current status value: {sub.status}")
            
            # Si c'est une string, convertir en Enum
            if isinstance(sub.status, str):
                if sub.status.lower() == "active":
                    sub.status = SubscriptionStatus.ACTIVE
                elif sub.status.lower() == "cancelled":
                    sub.status = SubscriptionStatus.CANCELLED
                elif sub.status.lower() == "expired":
                    sub.status = SubscriptionStatus.EXPIRED
                elif sub.status.lower() == "pending":
                    sub.status = SubscriptionStatus.PENDING
                
                print(f"  ✅ Fixed to: {sub.status}")
            else:
                print(f"  ⏭️  Already correct")
        
        db.commit()
        print("\n✅ All statuses fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_statuses()