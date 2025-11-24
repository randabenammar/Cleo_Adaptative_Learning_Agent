from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field

from backend.models.database import get_db
from backend.models.subject import Subject
from backend.models.user import User
from backend.agents.subject_agent import SubjectAgent
from backend.api.auth import get_current_active_user
from backend.models.subscription import Subscription
from backend.api.auth import get_current_active_user
import logging 

logger = logging.getLogger("backend.app")
router = APIRouter(prefix="/api/subjects", tags=["subjects"])


def get_subject_agent():
    from backend.app import _state
    agent = _state.get("subject_agent")
    if not agent:
        raise HTTPException(status_code=500, detail="SubjectAgent not initialized")
    return agent


# Pydantic Models
class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    summary: Optional[str] = None
    key_concepts: Optional[List[str]] = []
    prerequisites: Optional[List[str]] = []
    learning_objectives: Optional[List[str]] = []
    estimated_duration_hours: Optional[int] = 10
    difficulty_rating: Optional[float] = Field(default=3.0, ge=1.0, le=5.0)


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    summary: Optional[str] = None
    key_concepts: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    estimated_duration_hours: Optional[int] = None
    difficulty_rating: Optional[float] = Field(None, ge=1.0, le=5.0)


class GenerateSubjectsRequest(BaseModel):
    interests: Optional[str] = None
    level: Optional[str] = "beginner"
    count: Optional[int] = 5


# ============================================================================
# PUBLIC ROUTES
# ============================================================================

@router.get("/list")
def list_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Liste les sujets disponibles selon les favoris de l'utilisateur.
    """
    try:
        logger.info(f"📚 Subjects request from: {current_user.username}")
        
        # Récupérer subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            # Pas de subscription = afficher tous pour sélection
            all_subjects = db.query(Subject).order_by(Subject.name).all()
            return {
                "subjects": [s.to_dict() for s in all_subjects],
                "locked_subjects": [],
                "access_limit": 2,
                "needs_favorites_selection": True,
                "message": "Please select your 2 favorite subjects to continue"
            }
        
        # Récupérer limites
        limits = subscription.get_limits()
        max_subjects = limits["subjects_access"]
        
        # Récupérer favoris
        favorite_ids = subscription.get_favorite_subjects()
        
        # Récupérer tous les sujets
        all_subjects = db.query(Subject).order_by(Subject.name).all()
        
        logger.info(f"   Tier: {subscription.tier.value}, Max: {max_subjects}, Favorites: {favorite_ids}")
        
        # ⭐ LOGIQUE PRINCIPALE
        if max_subjects >= 999:
            # Illimité (PREMIUM)
            logger.info(f"   ✅ Unlimited access")
            return {
                "subjects": [s.to_dict() for s in all_subjects],
                "locked_subjects": [],
                "access_limit": max_subjects,
                "has_favorites": len(favorite_ids) > 0,
                "needs_favorites_selection": False
            }
        
        elif len(favorite_ids) == 0:
            # FREE mais pas encore de favoris → AFFICHER TOUS pour qu'il choisisse
            logger.info(f"   ⚠️ No favorites set, showing all for selection")
            return {
                "subjects": [s.to_dict() for s in all_subjects],
                "locked_subjects": [],
                "access_limit": max_subjects,
                "has_favorites": False,
                "needs_favorites_selection": True,
                "message": f"Please select your {max_subjects} favorite subjects"
            }
        
        else:
            # FREE et favoris définis → Filtrer par favoris
            available_subjects = [s for s in all_subjects if s.id in favorite_ids]
            locked_subjects = [s for s in all_subjects if s.id not in favorite_ids]
            
            logger.info(f"   🎯 Showing {len(available_subjects)} favorite subjects: {favorite_ids}")
            
            return {
                "subjects": [s.to_dict() for s in available_subjects],
                "locked_subjects": [s.to_dict() for s in locked_subjects],
                "access_limit": max_subjects,
                "has_favorites": True,
                "favorite_ids": favorite_ids,
                "needs_favorites_selection": False,
                "can_change_favorites": True
            }
        
    except Exception as e:
        logger.exception(f"❌ Error listing subjects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing subjects: {str(e)}"
        )

    
@router.get("/all")
def get_all_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère TOUS les sujets (pour la sélection de favoris)."""
    try:
        all_subjects = db.query(Subject).order_by(Subject.name).all()
        return {"subjects": [s.to_dict() for s in all_subjects]}
    except Exception as e:
        logger.exception(f"❌ Error fetching all subjects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching subjects: {str(e)}"
        )


@router.post("/generate")
def generate_subjects(
    payload: GenerateSubjectsRequest,
    learner_id: str = Query(...),
    db: Session = Depends(get_db),
    subject_agent: SubjectAgent = Depends(get_subject_agent)
):
    """Génère des suggestions de sujets personnalisées."""
    try:
        subjects = subject_agent.get_all_subjects(db)
        limited_subjects = subjects[:payload.count] if payload.count else subjects
        
        return {
            "success": True,
            "subjects": limited_subjects,
            "message": f"Found {len(limited_subjects)} subjects"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating subjects: {str(e)}")


@router.get("/{subject_id}/detail")
def get_subject_detail(
    subject_id: int,
    learner_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    subject_agent: SubjectAgent = Depends(get_subject_agent)
):
    """Récupère les détails d'un sujet avec le progrès de l'apprenant."""
    try:
        if not learner_id:
            learner_id = "guest"
            
        subject_details = subject_agent.get_subject_with_progress(db, subject_id, learner_id)
        
        if not subject_details:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        return {
            "success": True,
            **subject_details
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching subject detail: {str(e)}")


# ============================================================================
# ADMIN ROUTES (CRUD)
# ============================================================================

def require_admin(current_user: User = Depends(get_current_active_user)):
    """Vérifie que l'utilisateur est admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Créer un nouveau sujet (Admin only)."""
    import json
    import logging
    logger = logging.getLogger("backend.app")
    
    try:
        logger.info(f"Creating subject: {subject_data.name}")
        
        # Vérifier si le sujet existe déjà
        existing = db.query(Subject).filter(Subject.name == subject_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subject '{subject_data.name}' already exists"
            )
        
        # Créer le sujet
        new_subject = Subject(
            name=subject_data.name,
            category=subject_data.category,
            summary=subject_data.summary,
            key_concepts=json.dumps(subject_data.key_concepts) if subject_data.key_concepts else None,
            prerequisites=json.dumps(subject_data.prerequisites) if subject_data.prerequisites else None,
            learning_objectives=json.dumps(subject_data.learning_objectives) if subject_data.learning_objectives else None,
            estimated_duration_hours=subject_data.estimated_duration_hours,
            difficulty_rating=subject_data.difficulty_rating
        )
        
        db.add(new_subject)
        db.commit()
        db.refresh(new_subject)
        
        logger.info(f"✅ Subject created: {new_subject.id}")
        
        return {
            "success": True,
            "message": f"Subject '{new_subject.name}' created successfully",
            "subject": new_subject.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Error creating subject: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating subject: {str(e)}"
        )


@router.put("/{subject_id}")
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Mettre à jour un sujet (Admin only)."""
    import json
    import logging
    logger = logging.getLogger("backend.app")
    
    try:
        logger.info(f"Updating subject ID: {subject_id}")
        
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found"
            )
        
        # Mettre à jour les champs fournis
        update_data = subject_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field in ['key_concepts', 'prerequisites', 'learning_objectives']:
                if value is not None:
                    setattr(subject, field, json.dumps(value))
            else:
                setattr(subject, field, value)
        
        db.commit()
        db.refresh(subject)
        
        logger.info(f"✅ Subject updated: {subject.name}")
        
        return {
            "success": True,
            "message": f"Subject '{subject.name}' updated successfully",
            "subject": subject.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Error updating subject: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating subject: {str(e)}"
        )


@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Supprimer un sujet (Admin only)."""
    import logging
    logger = logging.getLogger("backend.app")
    
    try:
        logger.info(f"Deleting subject ID: {subject_id}")
        
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found"
            )
        
        subject_name = subject.name
        
        db.delete(subject)
        db.commit()
        
        logger.info(f"✅ Subject deleted: {subject_name}")
        
        return {
            "success": True,
            "message": f"Subject '{subject_name}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Error deleting subject: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting subject: {str(e)}"
        )
    
@router.get("/{subject_id}/content")
def get_subject_content(
    subject_id: int,
    learner_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Récupère le contenu adaptatif d'un sujet.
    """
    from backend.app import _state
    content_agent = _state.get("content_agent")
    
    if not content_agent:
        raise HTTPException(status_code=500, detail="ContentAgent not initialized")
    
    try:
        if not learner_id:
            learner_id = "guest"
            
        content = content_agent.get_adaptive_content(db, subject_id, learner_id)
        return {
            "success": True,
            "content": content
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching content: {str(e)}")