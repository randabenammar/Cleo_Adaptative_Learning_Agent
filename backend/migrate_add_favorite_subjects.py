"""
Ajouter le champ favorite_subject_ids à subscriptions.
"""

import sys
sys.path.insert(0, '.')

from models.database import engine
from sqlalchemy import text

def migrate():
    print("🔄 Adding favorite_subject_ids column to subscriptions...")
    
    try:
        with engine.connect() as conn:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("PRAGMA table_info(subscriptions)"))
            columns = [row[1] for row in result]
            
            if 'favorite_subject_ids' not in columns:
                print("➕ Adding column...")
                conn.execute(text('ALTER TABLE subscriptions ADD COLUMN favorite_subject_ids TEXT DEFAULT "[]"'))
                conn.commit()
                print("✅ Column added successfully!")
            else:
                print("⏭️  Column already exists")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()