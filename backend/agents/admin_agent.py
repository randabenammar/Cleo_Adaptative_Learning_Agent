import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, case

logger = logging.getLogger("cleo.admin_agent")


class AdminAgent:
    """
    Agent spécialisé pour les opérations d'administration et analytics globales.
    """
    
    def __init__(self, groq_client=None):
        self.groq_client = groq_client
        logger.info("AdminAgent initialized")
    
    def get_platform_stats(self, db) -> Dict[str, Any]:
        """
        Récupère les statistiques globales de la plateforme.
        """
        from backend.models.user import User
        from backend.models.quiz_session import QuizSession
        from backend.models.question import Question
        from backend.models.subject import Subject
        
        try:
            # Statistiques utilisateurs
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            verified_users = db.query(User).filter(User.is_verified == True).count()
            
            # Utilisateurs récents (derniers 7 jours)
            week_ago = datetime.utcnow() - timedelta(days=7)
            new_users_week = db.query(User).filter(User.created_at >= week_ago).count()
            
            # Utilisateurs actifs (dernière connexion < 30 jours)
            month_ago = datetime.utcnow() - timedelta(days=30)
            active_users_month = db.query(User).filter(
                User.last_login >= month_ago
            ).count() if db.query(User).filter(User.last_login != None).count() > 0 else 0
            
            # Statistiques quiz
            total_sessions = db.query(QuizSession).count()
            completed_sessions = db.query(QuizSession).filter(
                QuizSession.status == "completed"
            ).count()
            
            # ⭐ Calculer le score moyen à partir de correct_answers / total_questions
            # Utiliser CASE pour éviter division par zéro
            avg_score_result = db.query(
                func.avg(
                    case(
                        (QuizSession.total_questions > 0, 
                         (QuizSession.correct_answers * 100.0) / QuizSession.total_questions),
                        else_=0
                    )
                )
            ).filter(
                QuizSession.status == "completed",
                QuizSession.total_questions > 0
            ).scalar()
            
            avg_score = avg_score_result if avg_score_result is not None else 0
            
            # Questions et sujets
            total_questions = db.query(Question).count()
            total_subjects = db.query(Subject).count()
            
            # Activité récente (dernières 24h)
            day_ago = datetime.utcnow() - timedelta(days=1)
            sessions_24h = db.query(QuizSession).filter(
                QuizSession.started_at >= day_ago
            ).count()
            
            # Calculer growth_rate en sécurité
            growth_rate = 0
            if total_users > 0:
                growth_rate = (new_users_week / total_users * 100)
            
            # Calculer completion_rate en sécurité
            completion_rate = 0
            if total_sessions > 0:
                completion_rate = (completed_sessions / total_sessions * 100)
            
            return {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "verified": verified_users,
                    "new_this_week": new_users_week,
                    "active_last_month": active_users_month,
                    "growth_rate": round(growth_rate, 2)
                },
                "quizzes": {
                    "total_sessions": total_sessions,
                    "completed_sessions": completed_sessions,
                    "average_score": round(avg_score, 2),
                    "completion_rate": round(completion_rate, 2),
                    "sessions_24h": sessions_24h
                },
                "content": {
                    "total_questions": total_questions,
                    "total_subjects": total_subjects
                }
            }
        
        except Exception as e:
            logger.exception("Error getting platform stats: %s", e)
            return {
                "users": {
                    "total": 0,
                    "active": 0,
                    "verified": 0,
                    "new_this_week": 0,
                    "active_last_month": 0,
                    "growth_rate": 0
                },
                "quizzes": {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "average_score": 0,
                    "completion_rate": 0,
                    "sessions_24h": 0
                },
                "content": {
                    "total_questions": 0,
                    "total_subjects": 0
                }
            }
    
    def get_user_analytics(self, db, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Récupère des analytics détaillées sur les utilisateurs.
        """
        from backend.models.user import User
        from backend.models.quiz_session import QuizSession
        from sqlalchemy import desc, case
        
        try:
            users_query = db.query(User).order_by(desc(User.created_at)).limit(limit).offset(offset)
            users = users_query.all()
            
            user_list = []
            for user in users:
                # Sessions de cet utilisateur
                user_sessions = db.query(QuizSession).filter(
                    QuizSession.learner_id == f"user_{user.id}"
                ).count()
                
                user_completed = db.query(QuizSession).filter(
                    QuizSession.learner_id == f"user_{user.id}",
                    QuizSession.status == "completed"
                ).count()
                
                # ⭐ Moyenne calculée avec correct_answers / total_questions
                user_avg_result = db.query(
                    func.avg(
                        case(
                            (QuizSession.total_questions > 0,
                             (QuizSession.correct_answers * 100.0) / QuizSession.total_questions),
                            else_=0
                        )
                    )
                ).filter(
                    QuizSession.learner_id == f"user_{user.id}",
                    QuizSession.status == "completed",
                    QuizSession.total_questions > 0
                ).scalar()
                
                user_avg = user_avg_result if user_avg_result is not None else 0
                
                user_list.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "stats": {
                        "total_sessions": user_sessions,
                        "completed_sessions": user_completed,
                        "average_score": round(user_avg, 2)
                    }
                })
            
            total_users = db.query(User).count()
            
            return {
                "users": user_list,
                "total": total_users,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_users
            }
        
        except Exception as e:
            logger.exception("Error getting user analytics: %s", e)
            return {"users": [], "total": 0}
    
    def get_recent_activity(self, db, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère l'activité récente de la plateforme.
        """
        from backend.models.quiz_session import QuizSession
        from backend.models.user import User
        from sqlalchemy import desc, case
        
        try:
            recent_sessions = db.query(QuizSession).order_by(
                desc(QuizSession.started_at)
            ).limit(limit).all()
            
            activities = []
            for session in recent_sessions:
                learner_id = session.learner_id
                user_id = int(learner_id.replace("user_", "")) if learner_id.startswith("user_") else None
                
                user = None
                if user_id:
                    user = db.query(User).filter(User.id == user_id).first()
                
                # ⭐ Calculer le score
                score = 0
                if session.total_questions and session.total_questions > 0:
                    score = (session.correct_answers / session.total_questions) * 100
                
                activities.append({
                    "type": "quiz_session",
                    "user": {
                        "id": user.id if user else None,
                        "username": user.username if user else "Unknown",
                        "avatar_url": user.avatar_url if user else None
                    },
                    "data": {
                        "subject": session.subject_name,
                        "score": round(score, 2),
                        "status": session.status,
                        "bloom_level": session.bloom_level or session.initial_bloom_level or 1
                    },
                    "timestamp": session.started_at.isoformat() if session.started_at else None
                })
            
            return activities
        
        except Exception as e:
            logger.exception("Error getting recent activity: %s", e)
            return []
    
    def get_subject_analytics(self, db) -> List[Dict[str, Any]]:
        """
        Analytics par sujet.
        """
        from backend.models.subject import Subject
        from backend.models.quiz_session import QuizSession
        from sqlalchemy import case
        
        try:
            subjects = db.query(Subject).all()
            
            subject_stats = []
            for subject in subjects:
                sessions_count = db.query(QuizSession).filter(
                    QuizSession.subject_name == subject.name
                ).count()
                
                completed_count = db.query(QuizSession).filter(
                    QuizSession.subject_name == subject.name,
                    QuizSession.status == "completed"
                ).count()
                
                # ⭐ Score moyen calculé
                avg_score_result = db.query(
                    func.avg(
                        case(
                            (QuizSession.total_questions > 0,
                             (QuizSession.correct_answers * 100.0) / QuizSession.total_questions),
                            else_=0
                        )
                    )
                ).filter(
                    QuizSession.subject_name == subject.name,
                    QuizSession.status == "completed",
                    QuizSession.total_questions > 0
                ).scalar()
                
                avg_score = avg_score_result if avg_score_result is not None else 0
                
                subject_stats.append({
                    "id": subject.id,
                    "name": subject.name,
                    "icon": subject.icon,
                    "total_sessions": sessions_count,
                    "completed_sessions": completed_count,
                    "average_score": round(avg_score, 2),
                    "popularity": sessions_count
                })
            
            subject_stats.sort(key=lambda x: x["popularity"], reverse=True)
            
            return subject_stats
        
        except Exception as e:
            logger.exception("Error getting subject analytics: %s", e)
            return []
    
    def suspend_user(self, db, user_id: int, reason: str) -> Dict[str, Any]:
        """Suspend un utilisateur."""
        from backend.models.user import User
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            if user.role == "admin":
                return {"success": False, "error": "Cannot suspend admin users"}
            
            user.is_active = False
            db.commit()
            
            logger.info(f"User {user.username} suspended. Reason: {reason}")
            
            return {
                "success": True,
                "message": f"User {user.username} has been suspended",
                "user": user.to_dict()
            }
        
        except Exception as e:
            db.rollback()
            logger.exception("Error suspending user: %s", e)
            return {"success": False, "error": str(e)}
    
    def activate_user(self, db, user_id: int) -> Dict[str, Any]:
        """Réactive un utilisateur."""
        from backend.models.user import User
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            user.is_active = True
            db.commit()
            
            logger.info(f"User {user.username} activated")
            
            return {
                "success": True,
                "message": f"User {user.username} has been activated",
                "user": user.to_dict()
            }
        
        except Exception as e:
            db.rollback()
            logger.exception("Error activating user: %s", e)
            return {"success": False, "error": str(e)}
    
    def change_user_role(self, db, user_id: int, new_role: str) -> Dict[str, Any]:
        """Change le rôle d'un utilisateur."""
        from backend.models.user import User
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            if new_role not in ["student", "teacher", "admin"]:
                return {"success": False, "error": "Invalid role"}
            
            old_role = user.role
            user.role = new_role
            db.commit()
            
            logger.info(f"User {user.username} role changed from {old_role} to {new_role}")
            
            return {
                "success": True,
                "message": f"User role changed from {old_role} to {new_role}",
                "user": user.to_dict()
            }
        
        except Exception as e:
            db.rollback()
            logger.exception("Error changing user role: %s", e)
            return {"success": False, "error": str(e)}