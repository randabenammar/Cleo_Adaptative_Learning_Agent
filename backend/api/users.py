from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.models.database import get_db
from backend.models.user import User
from backend.core.dependencies import get_current_user
from backend.core.security import get_password_hash, validate_password_strength

router = APIRouter(prefix="/api/users", tags=["users"])


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.get("/profile")
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Récupère le profil complet de l'utilisateur connecté."""
    return current_user.to_dict()


@router.put("/profile")
def update_my_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour le profil de l'utilisateur."""
    
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    
    if payload.bio is not None:
        current_user.bio = payload.bio
    
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    
    if payload.preferred_language is not None:
        current_user.preferred_language = payload.preferred_language
    
    if payload.timezone is not None:
        current_user.timezone = payload.timezone
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": current_user.to_dict()
    }


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change le mot de passe de l'utilisateur."""
    
    from backend.core.security import verify_password
    
    # Vérifier l'ancien mot de passe
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Valider le nouveau mot de passe
    is_valid, error_msg = validate_password_strength(payload.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Mettre à jour
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    
    return {
        "success": True,
        "message": "Password changed successfully"
    }


@router.get("/{username}")
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """Récupère le profil public d'un utilisateur par username."""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user.to_public_dict()