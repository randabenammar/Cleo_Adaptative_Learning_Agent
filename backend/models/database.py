import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ⭐ Chemin ABSOLU vers backend/cleo.db
CURRENT_FILE = os.path.abspath(__file__)
BACKEND_DIR = os.path.dirname(os.path.dirname(CURRENT_FILE))
DATABASE_PATH = os.path.join(BACKEND_DIR, "cleo.db")
# Convertir en format SQLite URL (avec /)
DATABASE_PATH_NORMALIZED = DATABASE_PATH.replace("\\", "/")
DATABASE_URL = f"sqlite:///{DATABASE_PATH_NORMALIZED}"

print(f"🔧 Database configuration:")
print(f"   File: {__file__}")
print(f"   Backend dir: {BACKEND_DIR}")
print(f"   Database path: {DATABASE_PATH}")
print(f"   Database URL: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30  # ⭐ Timeout plus long
    },
    echo=False,  # Mettre True pour debug SQL
    pool_pre_ping=True  # ⭐ Vérifier la connexion avant utilisation
)

# ⭐ Ajouter expire_on_commit=False
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # ⭐ IMPORTANT
)

Base = declarative_base()

def get_db():
    """Dependency pour FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialise la base de données."""
    Base.metadata.create_all(bind=engine)