from pathlib import Path
from time import time
from dotenv import load_dotenv
import os 
from starlette.requests import Request
from backend.api import stripe_payment

from backend.models.database import init_db
from backend.agents.subject_agent import SubjectAgent
from backend.agents.content_agent import ContentAgent
from backend.agents.bloom_agent import BloomAgent
from backend.agents.evaluation_agent import EvaluationAgent
from backend.agents.quiz_agent import QuizAgent
from backend.agents.analytics_agent import AnalyticsAgent
from backend.agents.support_agent import SupportAgent
from backend.agents.admin_agent import AdminAgent
from backend.api import subjects, content, quiz, dashboard, emotion_support, auth, users,admin, subscriptions
from backend.core.dependencies import get_current_user

# Charger .env AVANT tout import
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Imports standard
import logging
from typing import Optional

# Imports FastAPI
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging AVANT d'importer les modules backend
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.app")

# Imports backend (APRÈS load_dotenv et logging setup)
try:
    from backend.core.emotion import EmotionClient
    from backend.core.groq import GroqClient
    from backend.core.orchestrator import Orchestrator
except ImportError as e:
    logger.error("Failed to import backend modules: %s", e)
    logger.error("Make sure backend/core/emotion.py, groq_client.py, and orchestrator.py exist")
    raise

# Reste du code...
app = FastAPI(title="CLEO Backend API",
description="AI-powered adaptive learning with emotional support",
    version="2.0.0"  # ⭐ Version mise à jour
    )

# CORS
# ⭐ CORS Configuration - IMPORTANT
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # ⭐ Permettre toutes les méthodes
    allow_headers=["*"],  # ⭐ Permettre tous les headers
)
# État global
_state = {}


API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


import threading


# --- Lazy init routine (runs in background thread) ---
def init_orchestrator_background():
    if _state["orchestrator"] is not None or _state["initializing"]:
        return
    _state["initializing"] = True
    _state["init_started_at"] = time.time()
    def _init():
        try:
            logger.info("Orchestrator init: importing core modules (this can take time on first run)...")
            # Import modules inside thread so they perform heavy work here and not at import-time
            from backend.core.rag import RAG
            from backend.core.emotion import EmotionClient
            from backend.core.groq import GroqClient
            from backend.core.agents import Orchestrator
            # Instantiate components (these may trigger downloads)
            rag = RAG()
            try:
                emotion_client = EmotionClient()
            except Exception as e:
                logger.warning("EmotionClient init failed: %s", e)
                class _StubEmotion:
                    def analyze(self, text): return {"dominant_emotion": "neutre", "confidence": 0.0, "error": str(e)}
                emotion_client = _StubEmotion()
            try:
                groq = GroqClient()
            except Exception as e:
                logger.warning("GroqClient init failed: %s", e)
                class _StubGen:
                    def generate(self, prompt, system_prompt=None, max_tokens=400, temperature=0.7):
                        return "[Groq not configured]"
                groq = _StubGen()
            orch = Orchestrator(rag=rag, emotion_client=emotion_client, generator=groq)
            _state["orchestrator"] = orch
            _state["init_finished_at"] = time.time()
            logger.info("Orchestrator initialized successfully in %.1fs", _state["init_finished_at"] - _state["init_started_at"])
        except Exception as e:
            _state["init_error"] = str(e)
            logger.exception("Failed to initialize orchestrator: %s", e)
        finally:
            _state["initializing"] = False
    t = threading.Thread(target=_init, daemon=True)
    t.start()

def is_orchestrator_ready() -> bool:
    return _state.get("orchestrator") is not None

def get_orchestrator(block: bool = False, timeout: float = 3.0):
    if is_orchestrator_ready():
        return _state["orchestrator"]
    if not _state["initializing"]:
        init_orchestrator_background()
    if not block:
        return None
    # wait for readiness up to timeout
    start = time.time()
    while time.time() - start < timeout:
        if is_orchestrator_ready():
            return _state["orchestrator"]
        time.sleep(0.25)
    return None

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes pour debug."""
    if request.url.path.startswith("/api"):
        # Lire le body (attention: on ne peut le lire qu'une fois)
        body = await request.body()
        logger.info("=== Incoming request ===")
        logger.info("Method: %s", request.method)
        logger.info("Path: %s", request.url.path)
        logger.info("Headers: %s", dict(request.headers))
        logger.info("Body (raw): %s", body.decode('utf-8', errors='replace'))
        logger.info("========================")
        
        # Reconstruire la requête pour que FastAPI puisse la lire
        async def receive():
            return {"type": "http.request", "body": body}
        
        request._receive = receive
    
    response = await call_next(request)
    return response

# Start background init on startup (non-blocking)
@app.on_event("startup")
def startup_event():
    logger.info("=== Starting backend initialization ===")
    
    try:
        # Initialiser DB
        logger.info("Initializing database...")
        init_db()
        logger.info("✓ Database initialized")
        
        # ⭐ Créer un utilisateur admin par défaut si n'existe pas
        from backend.models.database import SessionLocal
        from backend.models.user import User, UserRole
        from backend.core.security import get_password_hash
        
        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.email == "admin@cleo.com").first()
            if not admin_user:
                admin_user = User(
                    email="admin@cleo.com",
                    username="admin",
                    full_name="CLEO Administrator",
                    hashed_password=get_password_hash("Admin123!"),
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                db.commit()
                logger.info("✓ Default admin user created (admin@cleo.com / Admin123!)")
        finally:
            db.close()
        
        # Initialiser Groq Client
        groq_api_key = os.getenv("GROQ_API_KEY", "GROQ_API_KEY")
        groq_client = GroqClient(api_key=groq_api_key)
        _state["groq_client"] = groq_client
        logger.info("✓ GroqClient initialized")
        
        # Initialiser agents (code existant)
        subject_agent = SubjectAgent(groq_client=groq_client)
        _state["subject_agent"] = subject_agent
        logger.info("✓ SubjectAgent initialized")
        
        content_agent = ContentAgent(groq_client=groq_client)
        _state["content_agent"] = content_agent
        logger.info("✓ ContentAgent initialized")
        
        quiz_agent = QuizAgent(groq_client=groq_client)
        _state["quiz_agent"] = quiz_agent
        logger.info("✓ QuizAgent initialized")
        
        eval_agent = EvaluationAgent(groq_client=groq_client)
        _state["evaluation_agent"] = eval_agent
        logger.info("✓ EvaluationAgent initialized")
        
        bloom_agent = BloomAgent()
        _state["bloom_agent"] = bloom_agent
        logger.info("✓ BloomAgent initialized")
        
        analytics_agent = AnalyticsAgent(groq_client=groq_client)
        _state["analytics_agent"] = analytics_agent
        logger.info("✓ AnalyticsAgent initialized")
        
        support_agent = SupportAgent(groq_client=groq_client)
        _state["support_agent"] = support_agent
        logger.info("✓ SupportAgent initialized")

        admin_agent = AdminAgent(groq_client=groq_client)
        _state["admin_agent"] = admin_agent
        logger.info("✓ AdminAgent initialized")
        
        logger.info("=== Backend initialization complete ===")
    
    except Exception as e:
        logger.exception("Failed to initialize backend: %s", e)

@app.get("/")
def root():
    return {
        "message": "CLEO API v2.0 - Adaptive Learning Platform with Authentication",
        "status": "running",
        "features": [
            "Subject Explorer", 
            "Adaptive Quiz", 
            "Dashboard Analytics", 
            "Emotion Support",
            "User Authentication",  # ⭐ NOUVEAU
            "User Profiles"  # ⭐ NOUVEAU
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# ⭐ Inclure les nouveaux routers auth et users
app.include_router(auth.router)
app.include_router(users.router)

# Routers existants
app.include_router(subjects.router)
app.include_router(content.router)
app.include_router(quiz.router)
app.include_router(dashboard.router)
app.include_router(emotion_support.router)
app.include_router(admin.router)
app.include_router(subscriptions.router)
app.include_router(stripe_payment.router)

# --- API models ---
# Modèle de requête pour /api/query
class QueryRequest(BaseModel):
    learner_id: str
    text: Optional[str] = None      # Frontend envoie "text"
    query: Optional[str] = None     # Backward compatibility
    mode: Optional[str] = "explain" # Mode (explain, quiz, etc.)
    top_k: Optional[int] = 3        # Nombre de résultats RAG
    
    class Config:
        extra = "allow"  # Accepte champs supplémentaires sans erreur

@app.post("/api/query")
def api_query(payload: QueryRequest):
    """Traite une requête utilisateur (chat)."""
    learner_id = payload.learner_id
    
    # Accepter "text" (frontend) ou "query" (backward compat)
    query = (payload.text or payload.query or "").strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Le champ 'text' ou 'query' est requis")
    
    logger.info("Processing query for learner=%s mode=%s: %s", learner_id, payload.mode, query[:100])
    
    orch = _state.get("orchestrator")
    if not orch:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        # Passer les paramètres additionnels si nécessaire
        result = orch.process_query(learner_id, query, mode=payload.mode, top_k=payload.top_k)
        logger.info("Query processed successfully")
        return result
    except Exception as e:
        logger.exception("Query processing failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
       
            
# --- Endpoints ---
@app.get("/health")
def health():
    ready = is_orchestrator_ready()
    return {
        "status": "ok",
        "orchestrator_ready": ready,
        "initializing": _state["initializing"],
        "init_error": _state["init_error"],
        "init_started_at": _state["init_started_at"],
        "init_finished_at": _state["init_finished_at"],
    }

@app.get("/status")
def status():
    # convenience endpoint for ready state
    return health()

    
@app.post("/api/emotion")
def api_emotion(payload: dict, request: Request):
    """
    Analyse l'émotion d'un texte.
    - Utilise le client de l'orchestrator si présent.
    - Sinon instancie un EmotionClient localement (lazy).
    """
    text = payload.get("text") if isinstance(payload, dict) else None
    if not text:
        raise HTTPException(status_code=400, detail="Le champ 'text' est requis")

    try:
        # Si orchestrator prêt et expose un emotion client, on l'utilise
        client = None
        if is_orchestrator_ready():
            orch = _state.get("orchestrator")
            client = getattr(orch, "emotion_client", None)

        # Sinon importer/instancier le client localement (lazy, peut être coûteux)
        if client is None:
            from backend.core.emotion import EmotionClient
            client = EmotionClient()

        result = client.analyze(text)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Emotion analysis failed: %s", e)
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse d'émotion")