import logging
import json
from typing import Dict, Any, Optional
from difflib import SequenceMatcher

logger = logging.getLogger("cleo.evaluation_agent")


class EvaluationAgent:
    """
    Agent spécialisé dans l'évaluation automatique des réponses
    avec feedback personnalisé et détection de niveau Bloom.
    """
    
    def __init__(self, groq_client):
        self.groq_client = groq_client
        logger.info("EvaluationAgent initialized")
    
    def evaluate_mcq(self, question: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
        """Évalue une question MCQ."""
        correct_answer = question.get("correct_answer", "")
        is_correct = user_answer.upper() == correct_answer.upper()
        
        points_earned = question.get("points", 10) if is_correct else 0
        
        return {
            "is_correct": is_correct,
            "points_earned": points_earned,
            "points_possible": question.get("points", 10),
            "correct_answer": correct_answer,
            "explanation": question.get("explanation", ""),
            "feedback": self._get_mcq_feedback(is_correct, question),
            "confidence": 1.0 if is_correct else 0.0
        }
    
    def evaluate_open_ended(
        self,
        question: Dict[str, Any],
        user_answer: str,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """Évalue une question ouverte."""
        if use_ai and self.groq_client:
            return self._evaluate_open_with_ai(question, user_answer)
        else:
            return self._evaluate_open_simple(question, user_answer)
    
    def _evaluate_open_with_ai(self, question: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
        """Évaluation IA pour questions ouvertes."""
        sample_answer = question.get("sample_answer", "")
        keywords = question.get("keywords", [])
        bloom_level = question.get("bloom_level", 2)
        
        prompt = f"""You are an expert educational evaluator. Assess the following student answer.

Question: {question.get('question_text')}

Sample/Model Answer: {sample_answer}

Student's Answer: {user_answer}

Expected Keywords: {', '.join(keywords)}
Bloom Level: {bloom_level}

Evaluate the answer and provide a JSON response:
{{
  "score_percentage": 85,
  "is_correct": true,
  "strengths": ["Strength 1", "Strength 2"],
  "weaknesses": ["Area for improvement"],
  "missing_concepts": ["Concept not mentioned"],
  "feedback": "Constructive feedback for the student",
  "suggestions": "How to improve the answer"
}}

Be fair, constructive, and educational. Score from 0-100."""

        try:
            response = self.groq_client.chat(prompt, max_tokens=600)
            
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            eval_result = json.loads(json_str)
            
            # Calculer points
            score_pct = eval_result.get("score_percentage", 0) / 100
            points_possible = question.get("points", 15)
            points_earned = round(score_pct * points_possible, 1)
            
            return {
                "is_correct": eval_result.get("is_correct", score_pct >= 0.7),
                "points_earned": points_earned,
                "points_possible": points_possible,
                "score_percentage": eval_result.get("score_percentage"),
                "feedback": eval_result.get("feedback"),
                "strengths": eval_result.get("strengths", []),
                "weaknesses": eval_result.get("weaknesses", []),
                "missing_concepts": eval_result.get("missing_concepts", []),
                "suggestions": eval_result.get("suggestions"),
                "confidence": 0.85,
                "evaluation_method": "ai"
            }
        
        except Exception as e:
            logger.exception("AI evaluation failed, falling back to simple: %s", e)
            return self._evaluate_open_simple(question, user_answer)
    
    def _evaluate_open_simple(self, question: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
        """Évaluation simple basée sur mots-clés."""
        keywords = question.get("keywords", [])
        sample_answer = question.get("sample_answer", "")
        min_words = question.get("min_words", 20)
        
        user_lower = user_answer.lower()
        word_count = len(user_answer.split())
        
        # Vérifier présence de mots-clés
        keywords_found = sum(1 for kw in keywords if kw.lower() in user_lower)
        keyword_score = keywords_found / max(len(keywords), 1)
        
        # Vérifier longueur
        length_score = min(word_count / max(min_words, 1), 1.0)
        
        # Similarité avec réponse modèle
        similarity = SequenceMatcher(None, user_lower, sample_answer.lower()).ratio()
        
        # Score final
        final_score = (keyword_score * 0.5 + length_score * 0.2 + similarity * 0.3)
        
        points_possible = question.get("points", 15)
        points_earned = round(final_score * points_possible, 1)
        
        is_correct = final_score >= 0.6
        
        feedback_parts = []
        if keyword_score < 0.5:
            missing_kw = [kw for kw in keywords if kw.lower() not in user_lower]
            feedback_parts.append(f"Missing key concepts: {', '.join(missing_kw)}")
        if word_count < min_words:
            feedback_parts.append(f"Answer too brief ({word_count} words, expected {min_words}+)")
        if is_correct:
            feedback_parts.append("Good understanding demonstrated!")
        
        return {
            "is_correct": is_correct,
            "points_earned": points_earned,
            "points_possible": points_possible,
            "score_percentage": round(final_score * 100, 1),
            "feedback": " ".join(feedback_parts) if feedback_parts else "Answer needs improvement",
            "keywords_found": keywords_found,
            "keywords_total": len(keywords),
            "word_count": word_count,
            "confidence": 0.6,
            "evaluation_method": "keyword_matching"
        }
    
    def evaluate_true_false(self, question: Dict[str, Any], user_answer: bool) -> Dict[str, Any]:
        """Évalue une question vrai/faux."""
        correct_answer = question.get("correct_answer", False)
        is_correct = user_answer == correct_answer
        
        points_earned = question.get("points", 5) if is_correct else 0
        
        return {
            "is_correct": is_correct,
            "points_earned": points_earned,
            "points_possible": question.get("points", 5),
            "correct_answer": correct_answer,
            "explanation": question.get("explanation", ""),
            "feedback": "Correct!" if is_correct else f"Incorrect. The answer is {correct_answer}.",
            "confidence": 1.0
        }
    
    def _get_mcq_feedback(self, is_correct: bool, question: Dict[str, Any]) -> str:
        """Génère feedback pour MCQ."""
        if is_correct:
            return "✅ Excellent! " + question.get("explanation", "You got it right!")
        else:
            return "❌ Not quite. " + question.get("explanation", "Review the concept and try again.")
    
    def evaluate_matching(self, question: Dict[str, Any], user_matches: list) -> Dict[str, Any]:
        """
        Évalue une question de matching.
        
        Args:
            question: La question avec correct_matches
            user_matches: Liste de dicts [{"left": "L1", "right": "R1"}, ...]
            
        Returns:
            dict avec évaluation
        """
        correct_matches = question.get("correct_matches", [])
        
        if not correct_matches:
            logger.warning("No correct_matches defined for matching question")
            return {
                "is_correct": False,
                "points_earned": 0,
                "points_possible": question.get("points", 20),
                "feedback": "Unable to evaluate: no correct answers defined",
                "confidence": 0.0
            }
        
        # Convertir en sets pour comparaison
        correct_set = set()
        for match in correct_matches:
            correct_set.add((match.get("left"), match.get("right")))
        
        user_set = set()
        for match in user_matches:
            user_set.add((match.get("left"), match.get("right")))
        
        # Compter les matchs corrects
        correct_count = len(correct_set.intersection(user_set))
        total_count = len(correct_matches)
        
        # Calculer score
        score_percentage = (correct_count / total_count) * 100 if total_count > 0 else 0
        is_correct = correct_count == total_count
        
        points_possible = question.get("points", 20)
        points_earned = (correct_count / total_count) * points_possible if total_count > 0 else 0
        
        # Feedback
        if is_correct:
            feedback = f"✅ Perfect! All {total_count} matches are correct!"
        elif correct_count > 0:
            feedback = f"Partially correct: {correct_count}/{total_count} matches are right. Review the incorrect ones."
        else:
            feedback = "None of the matches are correct. Review the concepts and try again."
        
        return {
            "is_correct": is_correct,
            "points_earned": round(points_earned, 1),
            "points_possible": points_possible,
            "score_percentage": round(score_percentage, 1),
            "feedback": feedback,
            "correct_count": correct_count,
            "total_count": total_count,
            "confidence": 1.0,
            "evaluation_method": "exact_match"
        }

    def determine_next_bloom_level(
        self,
        current_level: int,
        recent_scores: list,
        threshold_up: float = 0.8,
        threshold_down: float = 0.5
    ) -> Dict[str, Any]:
        """
        Détermine s'il faut changer de niveau Bloom.
        
        Args:
            current_level: Niveau actuel (1-6)
            recent_scores: Liste des scores récents (0.0-1.0)
            threshold_up: Seuil pour monter de niveau
            threshold_down: Seuil pour descendre
            
        Returns:
            dict avec new_level, action, reason
        """
        if not recent_scores or len(recent_scores) < 3:
            return {
                "new_level": current_level,
                "action": "maintain",
                "reason": "Not enough data yet"
            }
        
        avg_score = sum(recent_scores) / len(recent_scores)
        
        if avg_score >= threshold_up and current_level < 6:
            return {
                "new_level": current_level + 1,
                "action": "level_up",
                "reason": f"Excellent performance ({avg_score:.1%})! Ready for next level.",
                "avg_score": avg_score
            }
        elif avg_score < threshold_down and current_level > 1:
            return {
                "new_level": current_level - 1,
                "action": "level_down",
                "reason": f"Let's reinforce fundamentals ({avg_score:.1%}). Don't worry, this is normal!",
                "avg_score": avg_score
            }
        else:
            return {
                "new_level": current_level,
                "action": "maintain",
                "reason": f"Good progress ({avg_score:.1%}). Keep practicing at this level.",
                "avg_score": avg_score
            }