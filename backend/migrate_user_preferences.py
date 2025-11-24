"""
Créer la table user_preferences.
"""

import sys
sys.path.insert(0, '.')

from models.database import engine
from sqlalchemy import text

def migrate():
    print("🔄 Creating user_preferences table...")
    
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    favorite_subject_ids TEXT DEFAULT '[]',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            conn.commit()
            print("✅ Table created successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    migrate()