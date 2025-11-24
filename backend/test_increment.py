"""
Script pour tester l'incrémentation.
"""

import sys
sys.path.insert(0, '.')

from models.database import SessionLocal
from models.subscription import Subscription
from models.user import User
from sqlalchemy.orm.attributes import flag_modified

def increment_quiz_usage(subscription, db):
    """Version locale pour le test."""
    usage = subscription.usage or {}
    current = usage.get("quizzes_this_month", 0)
    
    print(f"   Current: {current}")
    
    usage["quizzes_this_month"] = current + 1
    
    print(f"   New: {usage['quizzes_this_month']}")
    
    # ⭐ CRUCIAL
    subscription.usage = usage
    flag_modified(subscription, "usage")
    
    db.commit()
    print(f"   ✅ Committed")

def test_increment():
    db = SessionLocal()
    
    try:
        # Récupérer l'user ID 2
        user = db.query(User).filter(User.id == 2).first()
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"👤 User: {user.username} (ID: {user.id})")
        
        sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        
        if not sub:
            print("❌ No subscription")
            return
        
        print(f"\n📊 BEFORE increments:")
        print(f"   usage: {sub.usage}")
        
        # Tester 3 incrémentations
        for i in range(1, 4):
            print(f"\n{'='*50}")
            print(f"🔄 INCREMENT #{i}")
            print(f"{'='*50}")
            
            # Incrémenter
            increment_quiz_usage(sub, db)
            
            # Recharger depuis la DB
            db.expire(sub)
            db.refresh(sub)
            
            current = sub.usage.get('quizzes_this_month', 0)
            print(f"✅ After increment #{i}: {current}")
        
        print(f"\n{'='*50}")
        print(f"📊 FINAL RESULT")
        print(f"{'='*50}")
        final_value = sub.usage.get('quizzes_this_month', 0)
        print(f"Quizzes this month: {final_value}")
        print(f"Expected: 3")
        
        if final_value == 3:
            print("\n✅ ✅ ✅ SUCCESS! Increment works correctly!")
        else:
            print(f"\n❌ ❌ ❌ FAILED! Got {final_value} instead of 3")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_increment()