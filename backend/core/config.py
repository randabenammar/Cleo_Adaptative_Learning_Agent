import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuration de l'application CLEO.
    Les valeurs peuvent être surchargées par des variables d'environnement.
    """
    
    # Application
    APP_NAME: str = "CLEO - Adaptive Learning Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "cleo-super-secret-key-change-in-production-2024"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./backend/cleo.db"
    )
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Groq API
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    
    # HuggingFace API
    HF_API_KEY: Optional[str] = None
    HF_MODEL: Optional[str] = None
    HF_API_URL: Optional[str] = None
    
    # ChromaDB
    CHROMA_DB_PATH: str = "./chroma_pdf_db"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: str = "8000"
    FRONTEND_URL: str = "http://localhost:5173"
    
    # ML Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMOTION_MODEL: str = "j-hartmann/emotion-english-distilroberta-base"
    GENERATION_MODEL: str = "llama-3.1-8b-instant"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt", ".md", ".doc", ".docx"}
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # ⭐ IMPORTANT : Autoriser les variables extra
        extra = "allow"  # ou "ignore"


# Instance globale des settings
settings = Settings()