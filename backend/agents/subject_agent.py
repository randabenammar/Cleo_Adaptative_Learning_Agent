import logging
from typing import Dict, Any, List
from backend.core.groq import GroqClient

logger = logging.getLogger("cleo.subject_agent")


class SubjectAgent:
    """
    Agent spécialisé dans la génération et gestion des sujets d'apprentissage.
    """
    
    def __init__(self, groq_client: GroqClient):
        self.groq_client = groq_client
        logger.info("SubjectAgent initialized")
    
    def get_all_subjects(self, db) -> List[Dict[str, Any]]:
        """
        Récupère tous les sujets de la base de données.
        """
        from backend.models.subject import Subject
        
        try:
            # ⭐ Forcer l'expiration du cache
            db.expire_all()
            
            subjects = db.query(Subject).all()
            logger.info(f"📚 Found {len(subjects)} subjects in DB")
            
            result = []
            for subject in subjects:
                try:
                    # ⭐ LOG chaque sujet traité
                    logger.info(f"  Processing: {subject.name} (ID: {subject.id})")
                    
                    # ⭐ Mapping des vrais attributs DB
                    subject_dict = {
                        "id": subject.id,
                        "name": subject.name,
                        "category": subject.category or "General",
                        "description": subject.summary or f"Learn {subject.name} concepts and skills",
                        "icon": self._get_icon_for_subject(subject.name, subject.category),
                        "difficulty_level": self._get_difficulty_level(subject.difficulty_rating) if subject.difficulty_rating else "intermediate",
                        "estimated_duration_hours": subject.estimated_duration_hours or 10,
                        "difficulty_rating": subject.difficulty_rating or 3.0
                    }
                    
                    result.append(subject_dict)
                    logger.info(f"    ✅ Added: {subject.name}")
                    
                except Exception as e:
                    # ⭐ LOG les erreurs individuelles
                    logger.exception(f"    ❌ Error processing subject {subject.name}: {e}")
                    continue
            
            logger.info(f"✅ Returning {len(result)} subjects")
            return result
            
        except Exception as e:
            logger.exception("Error fetching all subjects: %s", e)
            return []
        
    def _get_icon_for_subject(self, name: str, category: str = None) -> str:
        """Génère un emoji approprié pour le sujet."""
        name_lower = name.lower()
        category_lower = (category or "").lower()
        
        # Map basé sur le nom
        icon_map = {
            "math": "🔢", "mathematics": "🔢", "algebra": "🔢", "geometry": "📐", "calculus": "📊",
            "python": "🐍", "javascript": "💛", "java": "☕", "c++": "⚙️", "programming": "💻",
            "physics": "⚛️", "chemistry": "🧪", "biology": "🧬", "science": "🔬",
            "history": "📜", "geography": "🌍", "literature": "📚", "english": "📖",
            "art": "🎨", "music": "🎵", "design": "✨",
            "business": "💼", "economics": "💰", "finance": "💵",
            "machine learning": "🤖", "ai": "🤖", "data": "📊", "web": "🌐",
            "database": "🗄️", "network": "🔗", "security": "🔒"
        }
        
        for keyword, icon in icon_map.items():
            if keyword in name_lower:
                return icon
        
        # Map basé sur la catégorie
        category_map = {
            "stem": "🔬",
            "science": "🧪",
            "technology": "💻",
            "engineering": "⚙️",
            "mathematics": "🔢",
            "arts": "🎨",
            "humanities": "📚",
            "social": "👥",
            "business": "💼",
            "language": "🗣️"
        }
        
        for keyword, icon in category_map.items():
            if keyword in category_lower:
                return icon
        
        return "📚"  # Default icon
    
    def _get_difficulty_level(self, rating: float) -> str:
        """Convertit difficulty_rating (1-5) en difficulty_level."""
        if rating <= 2.0:
            return "beginner"
        elif rating <= 3.5:
            return "intermediate"
        else:
            return "advanced"
    
    def get_subject_with_progress(self, db, subject_id: int, learner_id: str) -> Dict[str, Any]:
        """
        Récupère un sujet avec le progrès de l'apprenant.
        """
        from backend.models.subject import Subject
        from backend.models.learner_progress import LearnerProgress
        from backend.models.quiz_session import QuizSession
        from sqlalchemy import func, case
        
        try:
            # Récupérer le sujet
            subject = db.query(Subject).filter(Subject.id == subject_id).first()
            
            if not subject:
                return None
            
            # Construire le dict du sujet avec les vraies colonnes
            subject_dict = {
                "id": subject.id,
                "name": subject.name,
                "category": subject.category or "General",
                "description": subject.summary or f"Learn {subject.name} concepts and skills",
                "icon": self._get_icon_for_subject(subject.name, subject.category),
                "difficulty_level": self._get_difficulty_level(subject.difficulty_rating) if subject.difficulty_rating else "intermediate",
                "estimated_duration_hours": subject.estimated_duration_hours or 10,
                "key_concepts": subject.key_concepts,
                "prerequisites": subject.prerequisites,
                "learning_objectives": subject.learning_objectives
            }
            
            # Récupérer la progression
            progress = db.query(LearnerProgress).filter(
                LearnerProgress.learner_id == learner_id,
                LearnerProgress.subject_id == subject_id
            ).first()
            
            # Stats des quiz sur ce sujet
            total_sessions = db.query(QuizSession).filter(
                QuizSession.learner_id == learner_id,
                QuizSession.subject_name == subject.name
            ).count()
            
            completed_sessions = db.query(QuizSession).filter(
                QuizSession.learner_id == learner_id,
                QuizSession.subject_name == subject.name,
                QuizSession.status == "completed"
            ).count()
            
            # Calculer score moyen
            avg_score_result = db.query(
                func.avg(
                    case(
                        (QuizSession.total_questions > 0,
                         (QuizSession.correct_answers * 100.0) / QuizSession.total_questions),
                        else_=0
                    )
                )
            ).filter(
                QuizSession.learner_id == learner_id,
                QuizSession.subject_name == subject.name,
                QuizSession.status == "completed",
                QuizSession.total_questions > 0
            ).scalar()
            
            avg_score = avg_score_result if avg_score_result is not None else 0
            
            return {
                "subject": subject_dict,
                "progress": {
                    "bloom_level": progress.current_bloom_level if progress else 1,
                    "mastery_score": progress.mastery_score if progress else 0,
                    "total_sessions": total_sessions,
                    "completed_sessions": completed_sessions,
                    "average_score": round(avg_score, 2)
                }
            }
        
        except Exception as e:
            logger.exception("Error fetching subject with progress: %s", e)
            return None