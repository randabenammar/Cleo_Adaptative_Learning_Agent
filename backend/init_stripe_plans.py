"""
Initialiser les plans d'abonnement avec les Price IDs Stripe.
"""

import sys
sys.path.insert(0, '.')

from models.database import SessionLocal
from models.subscription import SubscriptionPlan, SubscriptionTier

def init_plans():
    db = SessionLocal()
    
    try:
        print("💎 Initializing subscription plans...")
        
        # ⭐ REMPLACEZ PAR VOS VRAIS PRICE IDs STRIPE
        plans_data = [
            {
                "tier": SubscriptionTier.BRONZE,
                "name": "Bronze Plan",
                "description": "Perfect for learners getting started",
                "price_monthly": 9.99,
                "stripe_price_id_monthly": "price_1SWNiUBiNRA1hXkXHERDEYyz",  # ⭐ À REMPLACER
                "badge": "🥉 Popular",
                "display_order": 1
            },
            {
                "tier": SubscriptionTier.SILVER,
                "name": "Silver Plan",
                "description": "For serious learners",
                "price_monthly": 19.99,
                "stripe_price_id_monthly": "price_1SWNlPBiNRA1hXkXGPcUmDiX",  # ⭐ À REMPLACER
                "badge": "🥈 Best Value",
                "display_order": 2
            },
            {
                "tier": SubscriptionTier.GOLD,
                "name": "Gold Plan",
                "description": "Advanced learning features",
                "price_monthly": 29.99,
                "stripe_price_id_monthly": "price_1SWNmCBiNRA1hXkXXCVGsHG0",  # ⭐ À REMPLACER
                "badge": "🥇 Premium",
                "display_order": 3
            },
            {
                "tier": SubscriptionTier.PLATINUM,
                "name": "Platinum Plan",
                "description": "Unlimited everything",
                "price_monthly": 49.99,
                "stripe_price_id_monthly": "price_1SWNnGBiNRA1hXkXarVunWPk",  # ⭐ À REMPLACER
                "badge": "💎 Ultimate",
                "display_order": 4
            }
        ]
        
        for plan_data in plans_data:
            # Vérifier si existe déjà
            existing = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.tier == plan_data["tier"]
            ).first()
            
            if existing:
                print(f"   ⏭️  {plan_data['name']} already exists, updating...")
                for key, value in plan_data.items():
                    if key != 'tier':
                        setattr(existing, key, value)
            else:
                print(f"   ✅ Creating {plan_data['name']}...")
                plan = SubscriptionPlan(**plan_data)
                db.add(plan)
        
        db.commit()
        print("\n✅ All plans initialized successfully!")
        
        # Afficher les plans
        plans = db.query(SubscriptionPlan).order_by(SubscriptionPlan.display_order).all()
        print("\n📋 Current plans:")
        for plan in plans:
            print(f"   {plan.badge} {plan.name} - ${plan.price_monthly}/month")
            print(f"      Price ID: {plan.stripe_price_id_monthly}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_plans()