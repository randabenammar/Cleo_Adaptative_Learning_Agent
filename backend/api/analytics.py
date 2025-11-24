# Créer un nouveau fichier si pas existant
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from backend.models.database import get_db
from backend.models.user import User
from backend.models.subscription import Subscription
from backend.api.auth import get_current_active_user

logger = logging.getLogger("backend.app")
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/export/pdf")
def export_pdf(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export des données en PDF (feature premium)."""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        # ⭐ Vérifier si l'export est autorisé
        limits = subscription.get_limits()
        if not limits["can_export_data"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "feature_locked",
                    "message": "Data export is a premium feature",
                    "required_tier": "bronze",
                    "upgrade_url": "/pricing"
                }
            )
        
        # TODO: Implémenter la génération PDF
        return {"message": "PDF export coming soon"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error exporting PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting data: {str(e)}"
        )