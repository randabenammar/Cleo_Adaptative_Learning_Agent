from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os
from pydantic import BaseModel
import json

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cleo.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Learner(Base):
    __tablename__ = "learners"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, default="anon")
    created_at = Column(DateTime, default=datetime.utcnow)
    profile_json = Column(Text, default="{}")  # JSON string: skills, memory, preferences

def init_db():
    Base.metadata.create_all(bind=engine)

# Simple DB helper
class LearnerCreate(BaseModel):
    id: str
    name: str = "anon"

class LearnerUpdate(BaseModel):
    profile_json: dict

def get_db():
    class DB:
        def create_learner(self, payload: LearnerCreate):
            db = SessionLocal()
            l = db.query(Learner).filter(Learner.id == payload.id).first()
            if l:
                db.close()
                return {"status": "exists", "id": payload.id}
            l = Learner(id=payload.id, name=payload.name, profile_json="{}")
            db.add(l); db.commit(); db.close()
            return {"status": "created", "id": payload.id}
        def get_learner(self, learner_id: str):
            db = SessionLocal()
            l = db.query(Learner).filter(Learner.id == learner_id).first()
            if not l:
                db.close()
                return {"error": "not_found"}
            res = {"id": l.id, "name": l.name, "profile": json.loads(l.profile_json or "{}"), "created_at": str(l.created_at)}
            db.close()
            return res
    return DB()