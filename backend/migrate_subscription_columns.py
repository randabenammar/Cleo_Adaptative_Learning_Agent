"""
Script pour migrer de JSON vers colonnes séparées.
"""

import sys
sys.path.insert(0, '.')

from models.database import SessionLocal, engine
from models.subscription import Subscription
from sqlalchemy import text
from datetime import datetime

def migrate():
    print("🔄 Migrating subscription usage to separate columns...")
    
    try:
        # Utiliser connection.execute au lieu de engine.execute
        with engine.connect() as conn:
            
            # Vérifier si les colonnes existent déjà
            result = conn.execute(text("PRAGMA table_info(subscriptions)"))
            columns = [row[1] for row in result]
            
            print(f"📋 Existing columns: {columns}")
            
            if 'quizzes_this_month' not in columns:
                print("\n➕ Adding new columns...")
                
                # Ajouter les colonnes une par une
                conn.execute(text('ALTER TABLE subscriptions ADD COLUMN quizzes_this_month INTEGER DEFAULT 0'))
                print("   ✅ quizzes_this_month")
                
                conn.execute(text('ALTER TABLE subscriptions ADD COLUMN questions_this_month INTEGER DEFAULT 0'))
                print("   ✅ questions_this_month")
                
                conn.execute(text('ALTER TABLE subscriptions ADD COLUMN ai_hints_this_month INTEGER DEFAULT 0'))
                print("   ✅ ai_hints_this_month")
                
                conn.execute(text('ALTER TABLE subscriptions ADD COLUMN usage_reset_date DATETIME'))
                print("   ✅ usage_reset_date")
                
                conn.commit()
                print("\n✅ Columns added successfully!")
            else:
                print("⏭️  Columns already exist")
        
        # Initialiser les valeurs
        db = SessionLocal()
        
        try:
            print("\n🔄 Initializing values...")
            
            subscriptions = db.query(Subscription).all()
            
            for sub in subscriptions:
                print(f"\n👤 User ID: {sub.user_id}")
                
                # Initialiser usage_reset_date si NULL
                if not sub.usage_reset_date:
                    sub.usage_reset_date = datetime.utcnow().replace(day=1)
                    print(f"   Set reset_date: {sub.usage_reset_date}")
                
                # Assurer que les compteurs sont à 0
                if sub.quizzes_this_month is None:
                    sub.quizzes_this_month = 0
                if sub.questions_this_month is None:
                    sub.questions_this_month = 0
                if sub.ai_hints_this_month is None:
                    sub.ai_hints_this_month = 0
                
                print(f"   Quizzes: {sub.quizzes_this_month}")
                print(f"   Questions: {sub.questions_this_month}")
                print(f"   AI Hints: {sub.ai_hints_this_month}")
            
            db.commit()
            print("\n✅ Migration completed successfully!")
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()