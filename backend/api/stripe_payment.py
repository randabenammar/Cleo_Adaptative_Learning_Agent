"""
API pour les paiements Stripe.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import stripe
import os
import logging
from datetime import datetime, timedelta  # ⭐ IMPORTANT
import json
import hmac
import hashlib
from backend.models.database import get_db
from backend.models.user import User
from backend.models.subscription import Subscription, SubscriptionPlan, SubscriptionTier, SubscriptionStatus
from backend.api.auth import get_current_active_user

logger = logging.getLogger("backend.app")
router = APIRouter(prefix="/api/payment", tags=["payment"])

# Configurer Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")






class CreateCheckoutRequest(BaseModel):
    tier: str  # "bronze", "silver", "gold", "platinum"

@router.post("/create-checkout-session")
def create_checkout_session(
    payload: CreateCheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Créer une session de paiement Stripe Checkout.
    """
    try:
        logger.info(f"💳 Creating checkout session for {current_user.username} - {payload.tier}")
        
        # Récupérer le plan demandé
        try:
            tier_enum = SubscriptionTier(payload.tier.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {payload.tier}"
            )
        
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == tier_enum
        ).first()
        
        if not plan or not plan.stripe_price_id_monthly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan not found or not configured: {payload.tier}"
            )
        
        # Vérifier l'abonnement actuel
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if subscription and subscription.tier == tier_enum:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already subscribed to this plan"
            )
        
        # Créer ou récupérer le customer Stripe
        if subscription and subscription.stripe_customer_id:
            customer_id = subscription.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.full_name or current_user.username,
                metadata={
                    "user_id": current_user.id,
                    "username": current_user.username
                }
            )
            customer_id = customer.id
            
            if subscription:
                subscription.stripe_customer_id = customer_id
                db.commit()
        
        # ⭐ Créer la session Checkout
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': plan.stripe_price_id_monthly,
                    'quantity': 1,
                }
            ],
            mode='subscription',
            success_url=f"{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/pricing?canceled=true",
            metadata={
                "user_id": current_user.id,
                "tier": payload.tier
            }
        )
        
        logger.info(f"✅ Checkout session created: {checkout_session.id}")
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
        
    except stripe.error.StripeError as e:
        logger.exception(f"❌ Stripe error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error creating checkout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating checkout: {str(e)}"
        )

@router.get("/verify-session/{session_id}")
def verify_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Vérifier le statut d'une session de paiement et mettre à jour la subscription.
    """
    try:
        # Récupérer la session Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        logger.info(f"🔍 Verifying session: {session_id}")
        logger.info(f"   Payment status: {session.payment_status}")
        logger.info(f"   Customer: {session.get('customer')}")
        logger.info(f"   Subscription: {session.get('subscription')}")
        logger.info(f"   Metadata: {session.metadata}")
        
        if session.payment_status == "paid":
            logger.info(f"✅ Payment confirmed as PAID")
            
            # ⭐ RÉCUPÉRER LES MÉTADONNÉES
            metadata = session.metadata or {}
            user_id = metadata.get('user_id')
            tier = metadata.get('tier')
            
            logger.info(f"   📋 Metadata extracted - user_id: {user_id}, tier: {tier}")
            
            if not user_id or not tier:
                logger.error(f"❌ Missing metadata! user_id={user_id}, tier={tier}")
                return {
                    "status": "error",
                    "message": "Missing metadata in session"
                }
            
            # Vérifier que c'est bien l'utilisateur actuel
            if int(user_id) != current_user.id:
                logger.error(f"❌ User mismatch! Session user: {user_id}, Current user: {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This payment session belongs to another user"
                )
            
            # ⭐ RÉCUPÉRER LA SUBSCRIPTION
            subscription = db.query(Subscription).filter(
                Subscription.user_id == current_user.id
            ).first()
            
            if not subscription:
                logger.error(f"❌ No subscription found for user {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No subscription found"
                )
            
            # ⭐ CONVERTIR LE TIER
            try:
                tier_enum = SubscriptionTier(tier.lower())
                logger.info(f"   ✓ Tier converted: {tier} → {tier_enum}")
            except ValueError:
                logger.error(f"❌ Invalid tier value: {tier}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid tier: {tier}"
                )
            
            # ⭐ METTRE À JOUR LA SUBSCRIPTION
            old_tier = subscription.tier.value
            logger.info(f"   📝 Updating subscription: {old_tier} → {tier_enum.value}")
            
            subscription.tier = tier_enum
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.stripe_subscription_id = session.get('subscription')
            subscription.stripe_customer_id = session.get('customer')
            subscription.start_date = datetime.utcnow()
            subscription.updated_at = datetime.utcnow()
            
            # Réinitialiser les quotas
            subscription.quizzes_this_month = 0
            subscription.questions_this_month = 0
            subscription.ai_hints_this_month = 0
            subscription.usage_reset_date = datetime.utcnow().replace(day=1)
            
            # Enregistrer le montant payé
            amount_paid = session.get('amount_total', 0) / 100  # Convertir centimes en dollars
            subscription.amount_paid = (subscription.amount_paid or 0) + amount_paid
            
            db.commit()
            db.refresh(subscription)
            
            logger.info(f"✅ SUBSCRIPTION SUCCESSFULLY UPDATED!")
            logger.info(f"   Old tier: {old_tier}")
            logger.info(f"   New tier: {tier_enum.value}")
            logger.info(f"   Status: {subscription.status.value}")
            logger.info(f"   Stripe Sub ID: {subscription.stripe_subscription_id}")
            
            return {
                "status": "success",
                "payment_status": session.payment_status,
                "subscription": subscription.to_dict(),
                "message": f"Successfully upgraded from {old_tier.upper()} to {tier_enum.value.upper()}!",
                "upgraded": True
            }
        
        else:
            logger.warning(f"⚠️ Payment not completed. Status: {session.payment_status}")
            return {
                "status": "pending",
                "payment_status": session.payment_status,
                "message": "Payment not completed yet"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error verifying session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying session: {str(e)}"
        )

@router.get("/portal")
def create_portal_session(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Créer une session Stripe Customer Portal (gérer abonnement).
    """
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription or not subscription.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Stripe customer found"
            )
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        portal_session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=f"{frontend_url}/dashboard"
        )
        
        return {"portal_url": portal_session.url}
        
    except Exception as e:
        logger.exception(f"❌ Error creating portal session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating portal session: {str(e)}"
        )




# Ajouter cette route à la fin du fichier

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook Stripe pour gérer les événements de paiement.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    if not webhook_secret:
        logger.warning("⚠️ STRIPE_WEBHOOK_SECRET not configured, skipping verification")
        # En développement, on peut continuer sans vérification
        event = json.loads(payload)
    else:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.error(f"❌ Invalid payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"❌ Invalid signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Gérer les différents événements
    event_type = event['type']
    logger.info(f"🔔 Webhook received: {event_type}")
    
    try:
        if event_type == 'checkout.session.completed':
            # Paiement réussi
            session = event['data']['object']
            await handle_checkout_completed(session, db)
            
        elif event_type == 'customer.subscription.created':
            # Abonnement créé
            subscription_obj = event['data']['object']
            await handle_subscription_created(subscription_obj, db)
            
        elif event_type == 'customer.subscription.updated':
            # Abonnement mis à jour
            subscription_obj = event['data']['object']
            await handle_subscription_updated(subscription_obj, db)
            
        elif event_type == 'customer.subscription.deleted':
            # Abonnement annulé
            subscription_obj = event['data']['object']
            await handle_subscription_deleted(subscription_obj, db)
            
        elif event_type == 'invoice.payment_succeeded':
            # Paiement d'une facture réussi
            invoice = event['data']['object']
            await handle_invoice_paid(invoice, db)
            
        elif event_type == 'invoice.payment_failed':
            # Paiement échoué
            invoice = event['data']['object']
            await handle_invoice_failed(invoice, db)
        
        else:
            logger.info(f"ℹ️ Unhandled event type: {event_type}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.exception(f"❌ Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# Webhook Handlers
# ========================================

async def handle_checkout_completed(session, db: Session):
    """Gérer la completion d'un checkout."""
    logger.info(f"✅ Checkout completed: {session['id']}")
    
    # Récupérer les métadonnées
    user_id = session['metadata'].get('user_id')
    tier = session['metadata'].get('tier')
    
    if not user_id or not tier:
        logger.warning("⚠️ Missing metadata in session")
        return
    
    # Récupérer l'abonnement Stripe
    stripe_subscription_id = session.get('subscription')
    customer_id = session.get('customer')
    
    # Mettre à jour la subscription dans la DB
    subscription = db.query(Subscription).filter(
        Subscription.user_id == int(user_id)
    ).first()
    
    if not subscription:
        logger.warning(f"⚠️ No subscription found for user {user_id}")
        return
    
    try:
        tier_enum = SubscriptionTier(tier.lower())
    except ValueError:
        logger.error(f"❌ Invalid tier: {tier}")
        return
    
    # ⭐ Mettre à jour le tier
    subscription.tier = tier_enum
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.stripe_subscription_id = stripe_subscription_id
    subscription.stripe_customer_id = customer_id
    subscription.start_date = datetime.utcnow()
    
    # Réinitialiser les quotas
    subscription.quizzes_this_month = 0
    subscription.questions_this_month = 0
    subscription.ai_hints_this_month = 0
    subscription.usage_reset_date = datetime.utcnow().replace(day=1)
    
    db.commit()
    
    logger.info(f"✅ Subscription updated: User {user_id} → {tier_enum.value.upper()}")


async def handle_subscription_created(subscription_obj, db: Session):
    """Gérer la création d'un abonnement."""
    logger.info(f"🆕 Subscription created: {subscription_obj['id']}")
    
    customer_id = subscription_obj.get('customer')
    
    # Trouver l'utilisateur via le customer_id
    subscription = db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()
    
    if subscription:
        subscription.stripe_subscription_id = subscription_obj['id']
        subscription.status = SubscriptionStatus.ACTIVE
        db.commit()
        logger.info(f"✅ Subscription linked to user")


async def handle_subscription_updated(subscription_obj, db: Session):
    """Gérer la mise à jour d'un abonnement."""
    logger.info(f"🔄 Subscription updated: {subscription_obj['id']}")
    
    stripe_sub_id = subscription_obj['id']
    status = subscription_obj['status']
    
    # Trouver la subscription
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_sub_id
    ).first()
    
    if not subscription:
        logger.warning(f"⚠️ Subscription not found: {stripe_sub_id}")
        return
    
    # Mettre à jour le statut
    if status == 'active':
        subscription.status = SubscriptionStatus.ACTIVE
    elif status == 'canceled':
        subscription.status = SubscriptionStatus.CANCELLED
    elif status == 'past_due':
        subscription.status = SubscriptionStatus.PENDING
    
    db.commit()
    logger.info(f"✅ Subscription status updated: {status}")


async def handle_subscription_deleted(subscription_obj, db: Session):
    """Gérer l'annulation d'un abonnement."""
    logger.info(f"❌ Subscription deleted: {subscription_obj['id']}")
    
    stripe_sub_id = subscription_obj['id']
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_sub_id
    ).first()
    
    if subscription:
        # Downgrade vers FREE
        subscription.tier = SubscriptionTier.FREE
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.end_date = datetime.utcnow()
        
        db.commit()
        logger.info(f"✅ User downgraded to FREE")


async def handle_invoice_paid(invoice, db: Session):
    """Gérer le paiement d'une facture."""
    logger.info(f"💰 Invoice paid: {invoice['id']}")
    
    customer_id = invoice.get('customer')
    amount_paid = invoice.get('amount_paid', 0) / 100  # Convertir en dollars
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()
    
    if subscription:
        subscription.amount_paid += amount_paid
        db.commit()
        logger.info(f"✅ Amount recorded: ${amount_paid}")


async def handle_invoice_failed(invoice, db: Session):
    """Gérer l'échec d'un paiement."""
    logger.error(f"❌ Invoice failed: {invoice['id']}")
    
    customer_id = invoice.get('customer')
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_customer_id == customer_id
    ).first()
    
    if subscription:
        subscription.status = SubscriptionStatus.PENDING
        db.commit()
        logger.warning(f"⚠️ Subscription marked as pending due to payment failure")