from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
import re

# Context pour hasher les mots de passe
# ⭐ Context pour hasher les mots de passe - Support Argon2 ET bcrypt
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],  # ⭐ CORRECTION : ajouter argon2
    deprecated="auto"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe correspond au hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash un mot de passe."""
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> Dict[str, any]:
    """
    Valide la force d'un mot de passe.
    
    Critères :
    - Minimum 6 caractères
    - Au moins une lettre majuscule
    - Au moins une lettre minuscule
    - Au moins un chiffre
    - (Optionnel) Au moins un caractère spécial
    
    Returns:
        Dict avec 'valid' (bool) et 'errors' (list)
    """
    errors = []
    
    # Longueur minimale
    if len(password) < 6:
        errors.append("Password must be at least 6 characters long")
    
    # Au moins une lettre minuscule
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Au moins une lettre majuscule
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Au moins un chiffre
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    # Optionnel : Au moins un caractère spécial
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     errors.append("Password must contain at least one special character")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT.
    """
    from backend.core.config import settings
    import logging
    logger = logging.getLogger("backend.app")
    
    to_encode = data.copy()
    
    # ⭐ DEBUG
    logger.info(f"🔑 Creating token with sub={data.get('sub')} (type: {type(data.get('sub'))})")
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # ⭐ Issued at
        "type": "access"
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        logger.info(f"✅ Token created successfully (length: {len(encoded_jwt)})")
        
        return encoded_jwt
    except Exception as e:
        logger.exception(f"❌ Error creating token: {e}")
        raise

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT de refresh (durée plus longue).
    """
    from backend.core.config import settings
    import logging
    logger = logging.getLogger("backend.app")
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh token valide 7 jours
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        logger.info(f"✅ Refresh token created (length: {len(encoded_jwt)})")
        
        return encoded_jwt
    except Exception as e:
        logger.exception(f"❌ Error creating refresh token: {e}")
        raise

def decode_access_token(token: str) -> Optional[dict]:
    """
    Décode un token JWT.
    """
    from backend.core.config import settings
    import logging
    logger = logging.getLogger("backend.app")
    
    try:
        logger.info(f"🔓 Decoding token (length: {len(token)})")
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        logger.info(f"✅ Token decoded successfully: sub={payload.get('sub')}")
        
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("❌ Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"❌ Invalid token: {e}")
        return None
    except Exception as e:
        logger.exception(f"❌ Error decoding token: {e}")
        return None