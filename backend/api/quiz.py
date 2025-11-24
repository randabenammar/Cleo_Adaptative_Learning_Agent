from asyncio.log import logger
import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from backend.api.auth import get_current_active_user
from backend.schemas.quiz_schemas import HintRequest
from backend.models.subscription import Subscription
#from backend.middleware.quota_checker import check_quiz_quota, increment_quiz_usage
from backend.middleware.quota_checker import  check_quiz_quota, increment_ai_hint_usage, increment_quiz_usage  # ⭐ AJOUTER

from backend.models.database import get_db
from backend.models.question import Question
from backend.models.quiz_session import QuizSession
from backend.models.answer import Answer
from backend.models.subject import Subject
from backend.models.learner_progress import LearnerProgress
from backend.agents.quiz_agent import QuizAgent
from backend.agents.evaluation_agent import EvaluationAgent
from backend.agents.bloom_agent import BloomAgent
from backend.models.user import User
from backend.middleware.quota_checker import increment_ai_hint_usage
import logging 

logger = logging.getLogger("backend.app")
router = APIRouter(prefix="/api/quiz", tags=["quiz"])


# Dépendances pour récupérer les agents
def get_quiz_agent():
    from backend.app import _state
    agent = _state.get("quiz_agent")
    if not agent:
        raise HTTPException(status_code=503, detail="QuizAgent not initialized")
    return agent


def get_evaluation_agent():
    from backend.app import _state
    agent = _state.get("evaluation_agent")
    if not agent:
        raise HTTPException(status_code=503, detail="EvaluationAgent not initialized")
    return agent


def get_bloom_agent():
    from backend.app import _state
    agent = _state.get("bloom_agent")
    if not agent:
        raise HTTPException(status_code=503, detail="BloomAgent not initialized")
    return agent


# Modèles Pydantic
class QuizGenerateRequest(BaseModel):
    learner_id: str
    subject_id: int
    topic: str
    bloom_level: Optional[int] = None  # Si None, utilise niveau actuel de l'apprenant
    question_type: str = "mcq"  # mcq, open_ended, matching, true_false
    num_questions: int = 5
    difficulty: Optional[int] = None


class AnswerSubmitRequest(BaseModel):
    session_id: str
    question_id: str
    user_answer: Any  # Peut être str, bool, dict selon type de question
    time_taken_seconds: int


class QuizCompleteRequest(BaseModel):
    session_id: str


# ========================================
# MODIFIER generate_quiz
# ========================================

@router.post("/generate")
def generate_quiz(
    payload: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    subscription: Subscription = Depends(check_quiz_quota),
    quiz_agent: QuizAgent = Depends(get_quiz_agent),
    bloom_agent: BloomAgent = Depends(get_bloom_agent)
):
    """
    Génère un nouveau quiz adaptatif.
    Vérifie automatiquement les quotas avant génération.
    """
    try:
        logger.info(f"📝 Generating quiz for learner: {payload.learner_id}")
        
        # Vérifier limite de questions
        limits = subscription.get_limits()
        max_questions = limits["questions_per_quiz"]
        
        if payload.num_questions > max_questions:
            logger.warning(f"⚠️ Adjusting questions from {payload.num_questions} to {max_questions}")
            payload.num_questions = max_questions
        
        # Récupérer le sujet
        subject = db.query(Subject).filter(Subject.id == payload.subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        # Récupérer progression
        progress = db.query(LearnerProgress).filter(
            LearnerProgress.learner_id == payload.learner_id,
            LearnerProgress.subject_id == payload.subject_id
        ).first()
        
        # Déterminer niveau Bloom
        bloom_level = payload.bloom_level
        if bloom_level is None:
            bloom_level = progress.current_bloom_level if progress else 2
        
        # Déterminer difficulté
        difficulty = payload.difficulty
        if difficulty is None:
            difficulty_range = bloom_agent.get_difficulty_range(bloom_level)
            difficulty = difficulty_range[0]
        
        # Générer questions
        logger.info(f"🤖 Generating {payload.num_questions} questions...")
        questions = quiz_agent.generate_questions(
            subject=subject.name,
            topic=payload.topic,
            bloom_level=bloom_level,
            question_type=payload.question_type,
            num_questions=payload.num_questions,
            difficulty=difficulty
        )
        
        logger.info(f"✅ Generated {len(questions)} questions")
        
        # Créer session
        session_id = f"quiz_{uuid.uuid4().hex[:12]}"
        
        quiz_session = QuizSession(
            session_id=session_id,
            learner_id=payload.learner_id,
            subject_id=payload.subject_id,
            subject_name=subject.name,
            topic=payload.topic,
            bloom_level=bloom_level,
            question_type=payload.question_type,
            num_questions=payload.num_questions,
            total_questions=len(questions),
            questions_data=questions,
            initial_bloom_level=bloom_level,
            status="in_progress"
        )
        
        db.add(quiz_session)
        db.commit()
        db.refresh(quiz_session)
        
        logger.info(f"✅ Quiz session created: {session_id}")
        
        # Sauvegarder questions
        for q_data in questions:
            existing_q = db.query(Question).filter(
                Question.question_id == q_data.get("question_id")
            ).first()
            
            if not existing_q:
                new_question = Question(
                    question_id=q_data.get("question_id"),
                    subject_id=payload.subject_id,
                    subject_name=subject.name,
                    topic=payload.topic,
                    bloom_level=q_data.get("bloom_level"),
                    bloom_label=q_data.get("bloom_label"),
                    question_type=q_data.get("question_type"),
                    difficulty=q_data.get("difficulty"),
                    points=q_data.get("points", 10),
                    question_text=q_data.get("question_text"),
                    question_data=q_data
                )
                db.add(new_question)
        
        db.commit()
        
        return {
            "session": quiz_session.to_dict(),
            "questions": questions,
            "bloom_info": bloom_agent.get_level_info(bloom_level),
            "quota_info": {
                "quizzes_used": subscription.quizzes_this_month,
                "quizzes_limit": limits["quizzes_per_month"],
                "questions_per_quiz_limit": max_questions
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"❌ Error generating quiz: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating quiz: {str(e)}"
        )


@router.post("/submit-answer")
def submit_answer(
    payload: AnswerSubmitRequest,
    db: Session = Depends(get_db),
    eval_agent: EvaluationAgent = Depends(get_evaluation_agent)
):
    """
    Soumet et évalue une réponse.
    """
    try:
        # Récupérer session
        session = db.query(QuizSession).filter(
            QuizSession.session_id == payload.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")
        
        if session.status != "in_progress":
            raise HTTPException(status_code=400, detail="Quiz session is not active")
        
        # Trouver la question dans les données de session
        questions = session.questions_data or []
        question_data = next(
            (q for q in questions if q.get("question_id") == payload.question_id),
            None
        )
        
        if not question_data:
            raise HTTPException(status_code=404, detail="Question not found in session")
        
        # Évaluer selon le type de question
        question_type = question_data.get("question_type")
        
        if question_type == "mcq":
            evaluation = eval_agent.evaluate_mcq(question_data, payload.user_answer)
        elif question_type == "open_ended":
            evaluation = eval_agent.evaluate_open_ended(
                question_data, 
                payload.user_answer,
                use_ai=True
            )
        elif question_type == "true_false":
            # ⭐ S'assurer que c'est un boolean
            user_answer_bool = payload.user_answer
            if isinstance(user_answer_bool, str):
                user_answer_bool = user_answer_bool.lower() == 'true'
            evaluation = eval_agent.evaluate_true_false(question_data, user_answer_bool)
            
        elif question_type == "matching":  # ⭐ NOUVEAU
            evaluation = eval_agent.evaluate_matching(question_data, payload.user_answer)
        else:
            # Fallback pour autres types
            evaluation = {
                "is_correct": False,
                "points_earned": 0,
                "points_possible": question_data.get("points", 10),
                "feedback": "Evaluation not yet implemented for this question type"
            }
        
        # Récupérer question ID depuis DB
        db_question = db.query(Question).filter(
            Question.question_id == payload.question_id
        ).first()
        
        # Créer réponse
        answer = Answer(
            quiz_session_id=session.id,
            question_id=db_question.id if db_question else None,
            learner_id=session.learner_id,
            user_answer=str(payload.user_answer),
            is_correct=evaluation.get("is_correct"),
            points_earned=evaluation.get("points_earned"),
            points_possible=evaluation.get("points_possible"),
            score_percentage=evaluation.get("score_percentage"),
            feedback=evaluation.get("feedback"),
            explanation=evaluation.get("explanation"),
            evaluation_data=evaluation,
            time_taken_seconds=payload.time_taken_seconds,
            evaluation_method=evaluation.get("evaluation_method", "unknown"),
            confidence=evaluation.get("confidence", 0.5)
        )
        
        db.add(answer)
        
        # Mettre à jour session
        session.questions_answered += 1
        if evaluation.get("is_correct"):
            session.correct_answers += 1
        session.total_points_earned += evaluation.get("points_earned", 0)
        session.total_points_possible += evaluation.get("points_possible", 0)
        session.current_question_index += 1
        
        db.commit()
        db.refresh(answer)
        db.refresh(session)
        
        # Mettre à jour stats de la question
        if db_question:
            db_question.times_used += 1
            # Recalculer taux de succès
            total_answers = db.query(Answer).filter(
                Answer.question_id == db_question.id
            ).count()
            correct_answers = db.query(Answer).filter(
                Answer.question_id == db_question.id,
                Answer.is_correct == True
            ).count()
            db_question.avg_success_rate = correct_answers / max(total_answers, 1)
            db.commit()
        
        return {
            "answer": answer.to_dict(),
            "session": session.to_dict(),
            "evaluation": evaluation
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting answer: {str(e)}")


# ========================================
# MODIFIER complete_quiz
# ========================================

@router.post("/complete")
def complete_quiz(
    payload: QuizCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    eval_agent: EvaluationAgent = Depends(get_evaluation_agent)
):
    """
    Complète un quiz et détermine si changement de niveau Bloom.
    Incrémente automatiquement l'usage des quotas.
    """
    try:
        logger.info(f"🏁 Completing quiz session: {payload.session_id}")
        
        session = db.query(QuizSession).filter(
            QuizSession.session_id == payload.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")
        
        # Marquer comme complété
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        
        # Calculer temps total
        if session.started_at:
            time_diff = session.completed_at - session.started_at
            session.time_spent_seconds = int(time_diff.total_seconds())
        
        # Récupérer scores récents de l'apprenant
        recent_answers = db.query(Answer).filter(
            Answer.learner_id == session.learner_id,
            Answer.quiz_session_id == session.id
        ).all()
        
        recent_scores = [
            a.points_earned / a.points_possible 
            for a in recent_answers 
            if a.points_possible and a.points_possible > 0
        ]
        
        # Déterminer changement de niveau Bloom
        bloom_decision = eval_agent.determine_next_bloom_level(
            current_level=session.bloom_level,
            recent_scores=recent_scores,
            threshold_up=0.8,
            threshold_down=0.5
        )
        
        session.final_bloom_level = bloom_decision.get("new_level")
        session.level_changed = (session.final_bloom_level != session.initial_bloom_level)
        
        # Mettre à jour progression de l'apprenant
        progress = db.query(LearnerProgress).filter(
            LearnerProgress.learner_id == session.learner_id,
            LearnerProgress.subject_id == session.subject_id
        ).first()
        
        if progress:
            progress.current_bloom_level = session.final_bloom_level
            progress.last_activity_date = datetime.utcnow()
            
            # Ajouter aux modules complétés si niveau monté
            if session.level_changed and bloom_decision.get("action") == "level_up":
                completed = progress.completed_modules or []
                if session.bloom_level not in completed:
                    completed.append(session.bloom_level)
                progress.completed_modules = completed
            
            # Mettre à jour % de complétion
            progress.completion_percentage = min(
                ((session.final_bloom_level - 1) / 5) * 100,
                100
            )
        
        # ⭐ COMMIT #1 : Sauvegarder session et progress
        db.commit()
        db.refresh(session)
        
        # ⭐ INCRÉMENTER L'USAGE (après le premier commit)
        from backend.models.subscription import Subscription
        from backend.middleware.quota_checker import increment_quiz_usage
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        quota_info = None
        
        if subscription:
            logger.info(f"📈 Before increment: {subscription.quizzes_this_month}")
            
            # Incrémenter
            increment_quiz_usage(subscription, db)
            
            # Refresh pour obtenir la nouvelle valeur
            db.refresh(subscription)
            
            logger.info(f"📈 After increment: {subscription.quizzes_this_month}")
            
            # ⭐ CONSTRUIRE quota_info avec les NOUVELLES COLONNES
            limits = subscription.get_limits()
            quota_info = {
                "quizzes_used": subscription.quizzes_this_month,  # ⭐ Colonne, pas usage["quizzes_this_month"]
                "quizzes_limit": limits["quizzes_per_month"],
                "quizzes_remaining": limits["quizzes_per_month"] - subscription.quizzes_this_month
            }
        else:
            logger.warning(f"⚠️ No subscription found for user {current_user.id}")
        
        return {
            "session": session.to_dict(),
            "bloom_decision": bloom_decision,
            "final_score": {
                "points_earned": session.total_points_earned,
                "points_possible": session.total_points_possible,
                "percentage": (session.total_points_earned / session.total_points_possible * 100) if session.total_points_possible > 0 else 0,
                "correct_answers": session.correct_answers,
                "total_questions": session.total_questions
            },
            "quota_info": quota_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"❌ Error completing quiz: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error completing quiz: {str(e)}"
        )



@router.get("/session/{session_id}")
def get_quiz_session(session_id: str, db: Session = Depends(get_db)):
    """Récupère une session de quiz avec ses réponses."""
    session = db.query(QuizSession).filter(
        QuizSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    answers = db.query(Answer).filter(
        Answer.quiz_session_id == session.id
    ).all()
    
    return {
        "session": session.to_dict(),
        "answers": [a.to_dict() for a in answers]
    }


@router.get("/history/{learner_id}")
def get_quiz_history(
    learner_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Récupère l'historique des quiz d'un apprenant."""
    sessions = db.query(QuizSession).filter(
        QuizSession.learner_id == learner_id
    ).order_by(QuizSession.started_at.desc()).limit(limit).all()
    
    return {
        "learner_id": learner_id,
        "total_sessions": len(sessions),
        "sessions": [s.to_dict() for s in sessions]
    }

@router.get("/test-matching/{subject_name}/{topic}")
def test_matching_generation(
    subject_name: str,
    topic: str,
    quiz_agent: QuizAgent = Depends(get_quiz_agent)
):
    """Endpoint de test pour vérifier la génération de questions matching."""
    try:
        questions = quiz_agent.generate_questions(
            subject=subject_name,
            topic=topic,
            bloom_level=3,
            question_type="matching",
            num_questions=2,
            difficulty=3
        )
        
        return {
            "success": True,
            "num_questions": len(questions),
            "questions": questions
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }



@router.post("/ai-hint")
def get_ai_hint(
    question_id: int,
    subscription: Subscription = Depends(check_quiz_quota),  # ⭐ VÉRIFICATION
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Génère un indice IA pour une question.
    ⭐ Vérifie et consomme les quotas d'AI hints.
    """
    try:
        logger.info(f"💡 AI hint request for question {question_id}")
        
        # TODO: Générer un hint avec Groq
        hint = "This is a helpful hint generated by AI..."
        
        # ⭐ INCRÉMENTER L'USAGE
        increment_ai_hint_usage(subscription, db)
        
        return {
            "hint": hint,
            "current_usage": subscription.quizzes_this_month or 0,
            "hints_remaining": subscription.get_limits()["ai_hints_per_month"] - current_usage
        }
        
    except Exception as e:
        logger.exception(f"❌ Error generating AI hint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Ajouter cette route dans quiz.py






# Ajoutez cette route
@router.post("/get-hint")
def get_ai_hint(
    payload: HintRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Génère un AI hint pour aider l'utilisateur."""
    try:
        logger.info(f"💡 AI hint requested by {current_user.username}")
        logger.info(f"   Session: {payload.session_id}, Question: {payload.question_id}")
        
        # Récupérer subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        # Vérifier quota
        limits = subscription.get_limits()
        hints_limit = limits["ai_hints_per_month"]
        hints_used = subscription.ai_hints_this_month or 0
        
        logger.info(f"   Hints: {hints_used}/{hints_limit}")
        
        if hints_used >= hints_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "quota_exceeded",
                    "message": f"You've reached your monthly limit of {hints_limit} AI hints",
                    "current_usage": hints_used,
                    "limit": hints_limit,
                    "upgrade_to": "bronze" if subscription.tier.value == "free" else "silver",
                    "upgrade_url": "/pricing"
                }
            )
        
        # Récupérer la session
        session = db.query(QuizSession).filter(
            QuizSession.session_id == payload.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")
        
        # Trouver la question
        question_data = None
        for q in session.questions_data:
            if q.get("question_id") == payload.question_id:
                question_data = q
                break
        
        if not question_data:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Générer hint avec Groq
        hint_prompt = f"""You are a helpful AI tutor. A student is struggling with this question:

Question: {question_data.get("question_text")}
Type: {question_data.get("question_type")}

Provide a helpful hint (NOT the answer) that guides the student toward understanding.
The hint should:
- Be encouraging and supportive  
- Guide thinking without giving away the answer
- Be 2-3 sentences maximum

Hint:"""
        
        try:
            from groq import Groq
            import os
            
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a supportive AI tutor."},
                    {"role": "user", "content": hint_prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            hint_text = response.choices[0].message.content.strip()
            logger.info(f"✅ Hint generated: {hint_text[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ Groq error: {e}")
            hint_text = "Try to break down the problem into smaller parts and think about the key concepts involved."
        
        # Incrémenter usage
        from backend.middleware.quota_checker import increment_ai_hint_usage
        increment_ai_hint_usage(subscription, db)
        
        db.refresh(subscription)
        
        logger.info(f"✅ Hint delivered. New usage: {subscription.ai_hints_this_month}/{hints_limit}")
        
        return {
            "hint": hint_text,
            "usage": {
                "hints_used": subscription.ai_hints_this_month,
                "hints_limit": hints_limit,
                "hints_remaining": max(0, hints_limit - (subscription.ai_hints_this_month or 0))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error generating hint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating hint: {str(e)}"
        )