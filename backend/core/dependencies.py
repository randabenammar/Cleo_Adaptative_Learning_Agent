from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from backend.models.database import get_db
from backend.models.user import User
from backend.core.security import decode_access_token

security = HTTPBearer()
logger = logging.getLogger("backend.app")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Récupère l'utilisateur courant depuis le JWT token.
    """
    token = credentials.credentials
    
    logger.info(f"Attempting to decode token: {token[:20]}...")
    
    payload = decode_access_token(token)
    if payload is None:
        logger.error("Failed to decode token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Token decoded successfully. Payload: {payload}")
    
    if payload.get("type") != "access":
        logger.error(f"Invalid token type: {payload.get('type')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        logger.error("No user_id in token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    logger.info(f"Looking for user with id: {user_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    logger.info(f"✅ User found: {user.username} (role: {user.role})")
    
    if not user.is_active:
        logger.error(f"User inactive: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Vérifie que l'utilisateur est actif."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Vérifie que l'utilisateur est admin."""
    logger.info(f"Checking admin access for: {current_user.username} (role: {current_user.role})")
    
    if current_user.role != "admin":
        logger.warning(f"❌ Access denied: {current_user.username} is '{current_user.role}', not 'admin'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions. Your role: {current_user.role}"
        )
    
    logger.info(f"✅ Admin access granted for: {current_user.username}")
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Récupère l'utilisateur s'il est connecté, sinon None."""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")
            if user_id:
                return db.query(User).filter(User.id == user_id).first()
    except:
        pass
    
    return None