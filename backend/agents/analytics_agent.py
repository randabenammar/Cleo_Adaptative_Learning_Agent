import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger("cleo.analytics_agent")


class AnalyticsAgent:
    """
    Agent spécialisé dans l'analyse des données d'apprentissage
    et la génération de recommandations personnalisées.
    """
    
    def __init__(self, groq_client=None):
        self.groq_client = groq_client
        logger.info("AnalyticsAgent initialized")
    
    def generate_learner_analytics(
        self,
        learner_id: str,
        db_session
    ) -> Dict[str, Any]:
        """
        Génère des analytics complètes pour un apprenant.
        
        Returns:
            dict avec toutes les métriques et insights
        """
        from backend.models.quiz_session import QuizSession
        from backend.models.answer import Answer
        from backend.models.learner_progress import LearnerProgress
        
        # Récupérer toutes les sessions de quiz
        sessions = db_session.query(QuizSession).filter(
            QuizSession.learner_id == learner_id
        ).all()
        
        if not sessions:
            return self._get_empty_analytics(learner_id)
        
        # Récupérer toutes les réponses
        all_answers = db_session.query(Answer).filter(
            Answer.learner_id == learner_id
        ).all()
        
        # Récupérer progression par sujet
        progress_records = db_session.query(LearnerProgress).filter(
            LearnerProgress.learner_id == learner_id
        ).all()
        
        # Calculer métriques globales
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.status == "completed"])
        total_questions_answered = sum(s.questions_answered for s in sessions)
        total_correct = sum(s.correct_answers for s in sessions)
        total_time_minutes = sum(s.time_spent_seconds or 0 for s in sessions) / 60
        
        overall_accuracy = (total_correct / total_questions_answered * 100) if total_questions_answered > 0 else 0
        
        # Analyse par niveau Bloom
        bloom_stats = self._analyze_bloom_levels(sessions, all_answers)
        
        # Analyse par sujet
        subject_stats = self._analyze_by_subject(sessions, progress_records)
        
        # Analyse temporelle
        temporal_stats = self._analyze_temporal_patterns(sessions)
        
        # Analyse émotionnelle (si données disponibles)
        emotion_stats = self._analyze_emotions(all_answers)
        
        # Strengths & Weaknesses
        strengths_weaknesses = self._identify_strengths_weaknesses(
            bloom_stats, subject_stats, all_answers
        )
        
        # Générer recommandations
        recommendations = self._generate_recommendations(
            bloom_stats, subject_stats, strengths_weaknesses, progress_records
        )
        
        return {
            "learner_id": learner_id,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "total_questions_answered": total_questions_answered,
                "total_correct": total_correct,
                "overall_accuracy": round(overall_accuracy, 1),
                "total_time_minutes": round(total_time_minutes, 1),
                "average_session_duration": round(total_time_minutes / max(completed_sessions, 1), 1)
            },
            "bloom_stats": bloom_stats,
            "subject_stats": subject_stats,
            "temporal_stats": temporal_stats,
            "emotion_stats": emotion_stats,
            "strengths": strengths_weaknesses["strengths"],
            "weaknesses": strengths_weaknesses["weaknesses"],
            "recommendations": recommendations
        }
    
    def _analyze_bloom_levels(self, sessions, answers) -> Dict[str, Any]:
        """Analyse performance par niveau Bloom."""
        bloom_data = {i: {"total": 0, "correct": 0, "accuracy": 0.0} for i in range(1, 7)}
        
        for answer in answers:
            if hasattr(answer, 'question') and answer.question:
                level = answer.question.bloom_level
                if 1 <= level <= 6:
                    bloom_data[level]["total"] += 1
                    if answer.is_correct:
                        bloom_data[level]["correct"] += 1
        
        # Calculer accuracy
        for level in bloom_data:
            total = bloom_data[level]["total"]
            if total > 0:
                bloom_data[level]["accuracy"] = round(
                    (bloom_data[level]["correct"] / total) * 100, 1
                )
        
        # Niveau actuel moyen
        recent_sessions = sorted(sessions, key=lambda s: s.started_at, reverse=True)[:5]
        avg_bloom = sum(s.bloom_level for s in recent_sessions) / max(len(recent_sessions), 1)
        
        return {
            "by_level": bloom_data,
            "current_average_level": round(avg_bloom, 1),
            "highest_mastered": max([l for l, d in bloom_data.items() if d["accuracy"] >= 80], default=1),
            "needs_improvement": [l for l, d in bloom_data.items() if d["total"] > 0 and d["accuracy"] < 60]
        }
    
    def _analyze_by_subject(self, sessions, progress_records) -> List[Dict[str, Any]]:
        """Analyse performance par sujet."""
        subject_data = {}
        
        for session in sessions:
            subject = session.subject_name
            if subject not in subject_data:
                subject_data[subject] = {
                    "subject_name": subject,
                    "sessions_count": 0,
                    "total_questions": 0,
                    "correct_answers": 0,
                    "total_time_minutes": 0,
                    "current_bloom_level": 1,
                    "completion_percentage": 0
                }
            
            subject_data[subject]["sessions_count"] += 1
            subject_data[subject]["total_questions"] += session.questions_answered
            subject_data[subject]["correct_answers"] += session.correct_answers
            subject_data[subject]["total_time_minutes"] += (session.time_spent_seconds or 0) / 60
        
        # Ajouter progression
        for progress in progress_records:
            if progress.subject and progress.subject.name in subject_data:
                subject_data[progress.subject.name]["current_bloom_level"] = progress.current_bloom_level
                subject_data[progress.subject.name]["completion_percentage"] = progress.completion_percentage
        
        # Calculer accuracy
        for subject in subject_data.values():
            if subject["total_questions"] > 0:
                subject["accuracy"] = round(
                    (subject["correct_answers"] / subject["total_questions"]) * 100, 1
                )
            else:
                subject["accuracy"] = 0.0
            subject["total_time_minutes"] = round(subject["total_time_minutes"], 1)
        
        return list(subject_data.values())
    
    def _analyze_temporal_patterns(self, sessions) -> Dict[str, Any]:
        """Analyse patterns temporels."""
        if not sessions:
            return {"daily_activity": [], "weekly_trend": "stable", "most_active_time": "N/A"}
        
        # Activité par jour (7 derniers jours)
        now = datetime.utcnow()
        daily_activity = []
        
        for i in range(7):
            date = now - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            sessions_that_day = [
                s for s in sessions
                if s.started_at and s.started_at.date() == date.date()
            ]
            
            daily_activity.append({
                "date": date_str,
                "day_name": date.strftime("%A"),
                "sessions": len(sessions_that_day),
                "questions": sum(s.questions_answered for s in sessions_that_day),
                "time_minutes": sum((s.time_spent_seconds or 0) / 60 for s in sessions_that_day)
            })
        
        daily_activity.reverse()
        
        # Tendance (simple: comparer première moitié vs seconde moitié)
        if len(sessions) >= 4:
            mid = len(sessions) // 2
            first_half_avg = sum(s.questions_answered for s in sessions[:mid]) / mid
            second_half_avg = sum(s.questions_answered for s in sessions[mid:]) / (len(sessions) - mid)
            
            if second_half_avg > first_half_avg * 1.2:
                trend = "increasing"
            elif second_half_avg < first_half_avg * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "daily_activity": daily_activity,
            "weekly_trend": trend,
            "total_days_active": len(set(s.started_at.date() for s in sessions if s.started_at))
        }
    
    def _analyze_emotions(self, answers) -> Dict[str, Any]:
        """Analyse historique émotionnel."""
        # Pour l'instant, simplifié (à enrichir avec vraies données émotionnelles)
        emotions = []
        for answer in answers:
            if hasattr(answer, 'evaluation_data') and answer.evaluation_data:
                # Extraire émotion si présente
                pass
        
        return {
            "dominant_emotions": [],
            "emotion_timeline": [],
            "stress_indicators": []
        }
    
    def _identify_strengths_weaknesses(
        self, bloom_stats, subject_stats, answers
    ) -> Dict[str, List[str]]:
        """Identifie forces et faiblesses."""
        strengths = []
        weaknesses = []
        
        # Bloom levels
        bloom_by_level = bloom_stats["by_level"]
        for level, data in bloom_by_level.items():
            if data["total"] >= 3:  # Au moins 3 questions
                if data["accuracy"] >= 80:
                    bloom_labels = {1: "Remember", 2: "Understand", 3: "Apply", 4: "Analyze", 5: "Evaluate", 6: "Create"}
                    strengths.append(f"Excellent mastery of Bloom Level {level} ({bloom_labels[level]})")
                elif data["accuracy"] < 50:
                    bloom_labels = {1: "Remember", 2: "Understand", 3: "Apply", 4: "Analyze", 5: "Evaluate", 6: "Create"}
                    weaknesses.append(f"Needs improvement at Bloom Level {level} ({bloom_labels[level]})")
        
        # Subjects
        for subject in subject_stats:
            if subject["total_questions"] >= 5:
                if subject["accuracy"] >= 85:
                    strengths.append(f"Strong performance in {subject['subject_name']}")
                elif subject["accuracy"] < 60:
                    weaknesses.append(f"Struggles with {subject['subject_name']} concepts")
        
        # Question types (si disponible)
        if answers:
            type_performance = {}
            for answer in answers:
                if hasattr(answer, 'question') and answer.question:
                    qtype = answer.question.question_type
                    if qtype not in type_performance:
                        type_performance[qtype] = {"total": 0, "correct": 0}
                    type_performance[qtype]["total"] += 1
                    if answer.is_correct:
                        type_performance[qtype]["correct"] += 1
            
            for qtype, data in type_performance.items():
                if data["total"] >= 3:
                    accuracy = (data["correct"] / data["total"]) * 100
                    if accuracy >= 85:
                        strengths.append(f"Excels at {qtype.replace('_', ' ')} questions")
                    elif accuracy < 50:
                        weaknesses.append(f"Difficulty with {qtype.replace('_', ' ')} questions")
        
        return {
            "strengths": strengths[:5],  # Top 5
            "weaknesses": weaknesses[:5]
        }
    
    def _generate_recommendations(
        self, bloom_stats, subject_stats, strengths_weaknesses, progress_records
    ) -> List[Dict[str, str]]:
        """Génère recommandations personnalisées."""
        recommendations = []
        
        # Recommandation Bloom
        needs_improvement = bloom_stats.get("needs_improvement", [])
        if needs_improvement:
            level = needs_improvement[0]
            bloom_labels = {1: "Remember", 2: "Understand", 3: "Apply", 4: "Analyze", 5: "Evaluate", 6: "Create"}
            recommendations.append({
                "type": "bloom_level",
                "priority": "high",
                "title": f"Focus on Bloom Level {level} ({bloom_labels[level]})",
                "description": f"Practice more questions at this cognitive level to strengthen foundational skills.",
                "action": "Start a quiz targeting this level"
            })
        
        # Recommandation Sujet
        if subject_stats:
            lowest_accuracy = min(subject_stats, key=lambda s: s.get("accuracy", 100))
            if lowest_accuracy["accuracy"] < 70 and lowest_accuracy["total_questions"] > 0:
                recommendations.append({
                    "type": "subject_review",
                    "priority": "medium",
                    "title": f"Review {lowest_accuracy['subject_name']}",
                    "description": f"Your accuracy is {lowest_accuracy['accuracy']}%. Revisit key concepts and practice more.",
                    "action": "Explore subject materials"
                })
        
        # Recommandation progression
        current_avg = bloom_stats.get("current_average_level", 1)
        if current_avg >= 2 and bloom_stats["by_level"].get(int(current_avg), {}).get("accuracy", 0) >= 75:
            recommendations.append({
                "type": "level_up",
                "priority": "high",
                "title": "Ready for Next Level!",
                "description": f"You're performing well at Level {int(current_avg)}. Challenge yourself with Level {int(current_avg)+1} questions.",
                "action": "Take advanced quiz"
            })
        
        # Recommandation temps d'étude
        recommendations.append({
            "type": "study_habit",
            "priority": "low",
            "title": "Maintain Consistency",
            "description": "Try to practice daily, even for 15 minutes. Consistent learning improves retention.",
            "action": "Set daily reminder"
        })
        
        return recommendations[:4]  # Top 4
    
    def _get_empty_analytics(self, learner_id: str) -> Dict[str, Any]:
        """Analytics vides pour nouvel apprenant."""
        return {
            "learner_id": learner_id,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_sessions": 0,
                "completed_sessions": 0,
                "total_questions_answered": 0,
                "total_correct": 0,
                "overall_accuracy": 0.0,
                "total_time_minutes": 0.0,
                "average_session_duration": 0.0
            },
            "bloom_stats": {
                "by_level": {i: {"total": 0, "correct": 0, "accuracy": 0.0} for i in range(1, 7)},
                "current_average_level": 1.0,
                "highest_mastered": 1,
                "needs_improvement": []
            },
            "subject_stats": [],
            "temporal_stats": {
                "daily_activity": [],
                "weekly_trend": "no_data",
                "total_days_active": 0
            },
            "emotion_stats": {},
            "strengths": ["Just getting started!"],
            "weaknesses": [],
            "recommendations": [
                {
                    "type": "getting_started",
                    "priority": "high",
                    "title": "Start Your Learning Journey",
                    "description": "Explore subjects and take your first quiz to begin building your learning profile.",
                    "action": "Browse subjects"
                }
            ]
        }