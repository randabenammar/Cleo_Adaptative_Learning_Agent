from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field

from backend.models.database import get_db
from backend.models.user import User, UserRole
from backend.agents.admin_agent import AdminAgent
from backend.api.auth import get_current_active_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


def get_admin_agent():
    from backend.app import _state
    agent = _state.get("admin_agent")
    if not agent:
        raise HTTPException(status_code=500, detail="AdminAgent not initialized")
    return agent


def require_admin(current_user: User = Depends(get_current_active_user)):
    """Vérifie que l'utilisateur est admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============================================================================
# Pydantic Models
# ============================================================================

class UserUpdateRole(BaseModel):
    role: str = Field(..., pattern="^(student|teacher|admin)$")  # ⭐ CORRIGÉ


class UserSuspend(BaseModel):
    reason: str = Field(..., min_length=5)


# ============================================================================
# STATS (déjà existants)
# ============================================================================

@router.get("/stats")
def get_platform_stats(
    db: Session = Depends(get_db),
    admin_agent: AdminAgent = Depends(get_admin_agent),
    current_user: User = Depends(require_admin)
):
    """Récupère les statistiques globales de la plateforme."""
    try:
        stats = admin_agent.get_platform_stats(db)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users")
def get_all_users(
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
    role: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    admin_agent: AdminAgent = Depends(get_admin_agent),
    current_user: User = Depends(require_admin)
):
    """Récupère la liste de tous les utilisateurs avec filtres."""
    try:
        analytics = admin_agent.get_user_analytics(db, limit=limit, offset=offset)
        
        users = analytics.get("users", [])
        
        # Filtrer par recherche
        if search:
            search_lower = search.lower()
            users = [u for u in users if 
                    search_lower in u["username"].lower() or 
                    search_lower in u["email"].lower() or
                    (u.get("full_name") and search_lower in u["full_name"].lower())]
        
        # Filtrer par rôle
        if role:
            users = [u for u in users if u["role"] == role]
        
        # Filtrer par statut actif
        if is_active is not None:
            users = [u for u in users if u["is_active"] == is_active]
        
        return {
            "success": True,
            "users": users,
            "total": len(users),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Récupère les détails complets d'un utilisateur."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return {
            "success": True,
            "user": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role_data: UserUpdateRole,
    db: Session = Depends(get_db),
    admin_agent: AdminAgent = Depends(get_admin_agent),
    current_user: User = Depends(require_admin)
):
    """Change le rôle d'un utilisateur."""
    result = admin_agent.change_user_role(db, user_id, role_data.role)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to change role")
        )
    
    return result


@router.put("/users/{user_id}/suspend")
def suspend_user(
    user_id: int,
    suspend_data: UserSuspend,
    db: Session = Depends(get_db),
    admin_agent: AdminAgent = Depends(get_admin_agent),
    current_user: User = Depends(require_admin)
):
    """Suspend un utilisateur."""
    result = admin_agent.suspend_user(db, user_id, suspend_data.reason)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to suspend user")
        )
    
    return result


@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_agent: AdminAgent = Depends(get_admin_agent),
    current_user: User = Depends(require_admin)
):
    """Réactive un utilisateur suspendu."""
    result = admin_agent.activate_user(db, user_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to activate user")
        )
    
    return result


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Supprime un utilisateur (Admin only)."""
    import logging
    logger = logging.getLogger("backend.app")
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Empêcher la suppression du dernier admin
        if user.role == "admin":
            admin_count = db.query(User).filter(User.role == "admin").count()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last admin user"
                )
        
        # Empêcher l'auto-suppression
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        username = user.username
        
        db.delete(user)
        db.commit()
        
        logger.info(f"✅ User deleted by admin: {username}")
        
        return {
            "success": True,
            "message": f"User '{username}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )