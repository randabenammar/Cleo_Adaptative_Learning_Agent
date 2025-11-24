import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("cleo.support_agent")


class SupportAgent:
    """
    Agent spécialisé dans le soutien émotionnel automatique.
    Détecte les signaux de détresse et propose interventions personnalisées.
    """
    
    # Seuils d'intervention
    STRESS_THRESHOLD = 0.6  # Score stress > 60%
    CONSECUTIVE_ERRORS_THRESHOLD = 3
    LOW_CONFIDENCE_THRESHOLD = 0.4
    FRUSTRATION_THRESHOLD = 0.5
    
    def __init__(self, groq_client=None):
        self.groq_client = groq_client
        logger.info("SupportAgent initialized")
    
    def should_intervene(
        self,
        recent_emotions: List[Dict[str, Any]],
        recent_answers: List[Dict[str, Any]],
        learner_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Détermine si une intervention est nécessaire.
        
        Returns:
            dict avec should_intervene (bool), reason (str), severity (str)
        """
        reasons = []
        severity = "low"
        
        # 1. Analyser émotions récentes
        if recent_emotions:
            avg_stress = sum(e.get('stress', 0) for e in recent_emotions) / len(recent_emotions)
            avg_frustration = sum(e.get('angry', 0) + e.get('disgust', 0) for e in recent_emotions) / len(recent_emotions) / 2
            avg_sadness = sum(e.get('sad', 0) for e in recent_emotions) / len(recent_emotions)
            
            if avg_stress > self.STRESS_THRESHOLD:
                reasons.append(f"High stress detected ({avg_stress:.0%})")
                severity = "high"
            
            if avg_frustration > self.FRUSTRATION_THRESHOLD:
                reasons.append(f"Frustration detected ({avg_frustration:.0%})")
                severity = "medium" if severity == "low" else severity
            
            if avg_sadness > 0.5:
                reasons.append(f"Low mood detected ({avg_sadness:.0%})")
                severity = "medium" if severity == "low" else severity
        
        # 2. Analyser performance récente
        if recent_answers:
            # Erreurs consécutives
            consecutive_errors = 0
            for answer in reversed(recent_answers):
                if not answer.get('is_correct'):
                    consecutive_errors += 1
                else:
                    break
            
            if consecutive_errors >= self.CONSECUTIVE_ERRORS_THRESHOLD:
                reasons.append(f"{consecutive_errors} consecutive errors")
                severity = "high"
            
            # Temps excessif sur questions
            long_answers = [a for a in recent_answers if a.get('time_taken_seconds', 0) > 120]
            if len(long_answers) >= 2:
                reasons.append("Taking unusually long on questions")
                severity = "medium" if severity == "low" else severity
        
        # 3. Contexte apprenant (fatigue, temps d'étude)
        if learner_context:
            study_duration = learner_context.get('session_duration_minutes', 0)
            if study_duration > 60:
                reasons.append("Long study session (>60 min)")
                severity = "medium" if severity == "low" else severity
        
        should_intervene = len(reasons) > 0
        
        return {
            "should_intervene": should_intervene,
            "reasons": reasons,
            "severity": severity,
            "intervention_type": self._determine_intervention_type(reasons)
        }
    
    def _determine_intervention_type(self, reasons: List[str]) -> str:
        """Détermine le type d'intervention selon les raisons."""
        reasons_str = " ".join(reasons).lower()
        
        if "stress" in reasons_str or "long session" in reasons_str:
            return "stress_management"
        elif "consecutive errors" in reasons_str:
            return "encouragement_learning"
        elif "frustration" in reasons_str:
            return "motivational"
        elif "low mood" in reasons_str or "sad" in reasons_str:
            return "emotional_support"
        else:
            return "general_support"
    
    def generate_support_message(
        self,
        intervention_type: str,
        learner_name: str = "there",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Génère un message de soutien personnalisé.
        """
        if self.groq_client:
            return self._generate_ai_support_message(intervention_type, learner_name, context)
        else:
            return self._get_template_support_message(intervention_type, learner_name)
    
    def _generate_ai_support_message(
        self,
        intervention_type: str,
        learner_name: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Génère message via IA."""
        
        type_instructions = {
            "stress_management": "The learner is showing signs of stress. Provide calming, supportive advice and suggest taking a break.",
            "encouragement_learning": "The learner is struggling with questions. Provide encouragement and remind them that mistakes are part of learning.",
            "motivational": "The learner is frustrated. Provide motivation and perspective on their progress.",
            "emotional_support": "The learner seems down. Provide empathetic, uplifting support.",
            "general_support": "Provide general encouragement and check-in."
        }
        
        instruction = type_instructions.get(intervention_type, type_instructions["general_support"])
        
        context_str = ""
        if context:
            context_str = f"\nContext: {context.get('current_subject', 'N/A')} - Bloom Level {context.get('bloom_level', 'N/A')}"
        
        prompt = f"""You are CLEO, an empathetic AI learning companion. A learner named {learner_name} needs emotional support.

Situation: {instruction}{context_str}

Generate a supportive response in JSON format:
{{
  "message": "A warm, empathetic message (2-3 sentences)",
  "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"],
  "encouragement": "A brief encouraging statement",
  "recommended_action": "break" or "continue" or "review"
}}

Be genuine, supportive, and actionable. Use a warm, friendly tone."""

        try:
            response = self.groq_client.chat(prompt, max_tokens=400)
            
            import json
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            data["intervention_type"] = intervention_type
            
            logger.info("AI support message generated for type: %s", intervention_type)
            return data
        
        except Exception as e:
            logger.exception("Failed to generate AI support message: %s", e)
            return self._get_template_support_message(intervention_type, learner_name)
    
    def _get_template_support_message(self, intervention_type: str, learner_name: str) -> Dict[str, Any]:
        """Messages template si IA indisponible."""
        
        templates = {
            "stress_management": {
                "message": f"Hey {learner_name}, I notice you might be feeling stressed. Remember, learning is a marathon, not a sprint. It's totally okay to take a breather! 🌸",
                "suggestions": [
                    "Take a 5-minute break and stretch",
                    "Try the 4-7-8 breathing technique",
                    "Get some water and walk around"
                ],
                "encouragement": "Your well-being matters more than any quiz. Come back refreshed!",
                "recommended_action": "break"
            },
            "encouragement_learning": {
                "message": f"{learner_name}, I see you're working through some challenging questions. That's exactly how learning happens! Every mistake is a step forward. 💪",
                "suggestions": [
                    "Review the explanation for the previous question",
                    "Break down the problem into smaller parts",
                    "Remember: confusion means you're learning!"
                ],
                "encouragement": "You're doing great by persisting. Growth happens outside the comfort zone!",
                "recommended_action": "continue"
            },
            "motivational": {
                "message": f"{learner_name}, feeling frustrated is completely normal when tackling new concepts. You're challenging yourself, and that's admirable! 🌟",
                "suggestions": [
                    "Look back at how far you've come",
                    "Focus on one concept at a time",
                    "Celebrate small wins along the way"
                ],
                "encouragement": "Every expert was once a beginner. You're on the right path!",
                "recommended_action": "continue"
            },
            "emotional_support": {
                "message": f"Hey {learner_name}, I'm here for you. Learning can be tough sometimes, but you're not alone in this journey. 💙",
                "suggestions": [
                    "Be kind to yourself - you're doing your best",
                    "Talk to someone you trust",
                    "Take a break if you need one"
                ],
                "encouragement": "Your effort and dedication are what truly matter. I believe in you!",
                "recommended_action": "break"
            },
            "general_support": {
                "message": f"Hi {learner_name}! Just checking in. How are you feeling about your learning today? 😊",
                "suggestions": [
                    "Keep up the consistent effort",
                    "Take breaks when needed",
                    "Remember why you started this journey"
                ],
                "encouragement": "You're making progress, even if it doesn't always feel like it!",
                "recommended_action": "continue"
            }
        }
        
        template = templates.get(intervention_type, templates["general_support"])
        template["intervention_type"] = intervention_type
        return template
    
    def get_stress_relief_techniques(self) -> List[Dict[str, Any]]:
        """Retourne des techniques de gestion du stress."""
        return [
            {
                "id": "breathing_478",
                "name": "4-7-8 Breathing",
                "description": "Breathe in for 4, hold for 7, exhale for 8",
                "duration_seconds": 60,
                "icon": "🫁",
                "steps": [
                    "Sit comfortably and close your eyes",
                    "Breathe in through your nose for 4 seconds",
                    "Hold your breath for 7 seconds",
                    "Exhale slowly through your mouth for 8 seconds",
                    "Repeat 3-4 times"
                ]
            },
            {
                "id": "progressive_relaxation",
                "name": "Progressive Muscle Relaxation",
                "description": "Tense and release muscle groups",
                "duration_seconds": 120,
                "icon": "💪",
                "steps": [
                    "Start with your toes - tense for 5 seconds, then release",
                    "Move to your calves, thighs, and work your way up",
                    "Include shoulders, neck, and facial muscles",
                    "Notice the difference between tension and relaxation"
                ]
            },
            {
                "id": "grounding_54321",
                "name": "5-4-3-2-1 Grounding",
                "description": "Use your senses to stay present",
                "duration_seconds": 90,
                "icon": "🌿",
                "steps": [
                    "Name 5 things you can see",
                    "Name 4 things you can touch",
                    "Name 3 things you can hear",
                    "Name 2 things you can smell",
                    "Name 1 thing you can taste"
                ]
            },
            {
                "id": "desk_stretch",
                "name": "Quick Desk Stretches",
                "description": "Stretch away tension in 2 minutes",
                "duration_seconds": 120,
                "icon": "🧘",
                "steps": [
                    "Neck rolls: 5 in each direction",
                    "Shoulder shrugs: 10 times",
                    "Wrist circles: 10 in each direction",
                    "Stand up and reach for the ceiling",
                    "Touch your toes (or as far as comfortable)"
                ]
            },
            {
                "id": "positive_affirmations",
                "name": "Positive Affirmations",
                "description": "Reset your mindset with affirmations",
                "duration_seconds": 60,
                "icon": "✨",
                "steps": [
                    "Say: 'I am capable of learning new things'",
                    "Say: 'Mistakes help me grow'",
                    "Say: 'I am doing my best, and that's enough'",
                    "Say: 'I believe in my ability to succeed'",
                    "Take a deep breath and smile"
                ]
            }
        ]
    
    def get_motivational_quotes(self) -> List[str]:
        """Retourne des citations motivationnelles."""
        return [
            "The expert in anything was once a beginner. - Helen Hayes",
            "Mistakes are proof that you are trying.",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
            "You don't have to be great to start, but you have to start to be great. - Zig Ziglar",
            "Learning is a treasure that will follow its owner everywhere.",
            "The beautiful thing about learning is that nobody can take it away from you. - B.B. King",
            "Don't let what you cannot do interfere with what you can do. - John Wooden",
            "It always seems impossible until it's done. - Nelson Mandela"
        ]