from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from backend.models.database import get_db
from backend.models.user import User, UserRole
from backend.core.security import verify_password, get_password_hash, create_access_token
from backend.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# OAuth2 scheme pour extraire le token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# ============================================================================
# Pydantic Models
# ============================================================================

class UserSignUp(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.STUDENT


class UserSignIn(BaseModel):
    email_or_username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ============================================================================
# Dependency Functions
# ============================================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Récupère l'utilisateur actuel à partir du token JWT.
    """
    import jwt
    from jwt.exceptions import InvalidTokenError
    import logging
    logger = logging.getLogger("backend.app")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        logger.info(f"🔐 Validating token (length: {len(token) if token else 0})")
        
        # ⭐ Vérifier que le token n'est pas vide
        if not token or token == "undefined" or token == "null":
            logger.warning("❌ Token is empty or invalid string")
            raise credentials_exception
        
        # Décoder le token
        from backend.core.config import settings
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        
        logger.info(f"✅ Token decoded: user_id={user_id}")
        
        if user_id is None:
            logger.warning("❌ No 'sub' in token payload")
            raise credentials_exception
        
        token_data = TokenData(user_id=int(user_id))
        
    except jwt.ExpiredSignatureError:
        logger.warning("❌ Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"❌ Invalid token: {e}")
        raise credentials_exception
    except Exception as e:
        logger.exception(f"❌ Error validating token: {e}")
        raise credentials_exception
    
    # Récupérer l'utilisateur de la DB
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        logger.warning(f"❌ User not found in DB: id={token_data.user_id}")
        raise credentials_exception
    
    logger.info(f"✅ User authenticated: {user.username} (ID: {user.id})")
    
    return user
    
    


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Vérifie que l'utilisateur est actif.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# ============================================================================
# Routes
# ============================================================================

@router.post("/signup", response_model=Token)
def sign_up(user_data: UserSignUp, db: Session = Depends(get_db)):
    """
    Créer un nouveau compte utilisateur.
    """
    import logging
    logger = logging.getLogger("backend.app")
    
    try:
        # Vérifier si l'email existe déjà
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Vérifier si le username existe déjà
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Créer le nouvel utilisateur
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role or UserRole.STUDENT,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"✅ New user created: {new_user.username} (ID: {new_user.id})")
        
        # Créer le token d'accès
        access_token = create_access_token(data={"sub": str(new_user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": new_user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/signin", response_model=Token)
def sign_in(credentials: UserSignIn, db: Session = Depends(get_db)):
    """
    Se connecter avec email/username et mot de passe.
    """
    import logging
    logger = logging.getLogger("backend.app")
    
    try:
        # Chercher l'utilisateur par email ou username
        user = db.query(User).filter(
            (User.email == credentials.email_or_username) |
            (User.username == credentials.email_or_username)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password"
            )
        
        # Vérifier le mot de passe
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password"
            )
        
        # Vérifier si l'utilisateur est actif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is suspended"
            )
        
        # Mettre à jour last_login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ User logged in: {user.username} (ID: {user.id})")
        
        # Créer le token d'accès
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error during signin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error signing in: {str(e)}"
        )


@router.post("/token", response_model=Token)
def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint OAuth2 standard pour obtenir un token.
    Compatible avec FastAPI's automatic docs.
    """
    credentials = UserSignIn(
        email_or_username=form_data.username,
        password=form_data.password
    )
    return sign_in(credentials, db)


@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère les informations de l'utilisateur actuellement connecté.
    """
    return {
        "success": True,
        "user": current_user.to_dict()
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    """
    Déconnexion (côté serveur on ne fait rien, le client supprime le token).
    """
    import logging
    logger = logging.getLogger("backend.app")
    logger.info(f"User logged out: {current_user.username}")
    
    return {
        "success": True,
        "message": "Logged out successfully"
    }

# Ajouter à la fin du fichier auth.py

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)


@router.put("/profile")
def update_profile(
    updates: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour le profil de l'utilisateur connecté.
    """
    import logging
    logger = logging.getLogger("backend.app")
    
    try:
        logger.info(f"📝 Profile update request from: {current_user.username}")
        
        # Vérifier si le nouvel email existe déjà
        if updates.email and updates.email != current_user.email:
            existing_email = db.query(User).filter(
                User.email == updates.email,
                User.id != current_user.id
            ).first()
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
        
        # Vérifier si le nouveau username existe déjà
        if updates.username and updates.username != current_user.username:
            existing_username = db.query(User).filter(
                User.username == updates.username,
                User.id != current_user.id
            ).first()
            
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Mettre à jour les champs fournis
        update_data = updates.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"✅ Profile updated for: {current_user.username}")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": current_user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )


@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère les informations de l'utilisateur actuellement connecté.
    """
    return {
        "success": True,
        "user": current_user.to_dict()
    }