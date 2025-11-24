import datetime
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("cleo.orchestrator")
logger.setLevel(logging.INFO)


class Orchestrator:
    """
    Orchestrateur principal de CLEO : coordonne l'analyse d'émotion, 
    la génération de réponse via Groq, et la gestion du profil apprenant.
    """

    def __init__(self, emotion_client=None, groq_client=None):
        self.emotion_client = emotion_client
        self.groq_client = groq_client
        self._learners = {}  # Stockage en mémoire des profils
        logger.info("Orchestrator initialized with emotion_client=%s groq_client=%s", 
                    bool(emotion_client), bool(groq_client))

    def process_query(self, learner_id: str, query: str, mode: str = "explain", top_k: int = 3) -> Dict[str, Any]:
        """
        Traite une requête utilisateur complète.
        
        Args:
            learner_id: Identifiant unique de l'apprenant
            query: Question/requête de l'utilisateur
            mode: Mode de réponse ("explain", "quiz", "summarize", etc.)
            top_k: Nombre de documents RAG à récupérer (si applicable)
            
        Returns:
            dict: {"response": str, "emotion": dict, "learner_id": str}
        """
        try:
            logger.info("process_query: learner=%s mode=%s query=%s", learner_id, mode, query[:50])
            
            # 1) Analyse de l'émotion
            emotion_result = self._analyze_emotion(query)
            
            # 2) Récupération ou création du profil
            learner_profile = self._get_or_create_learner(learner_id)
            
            # 3) Construction du contexte pour le prompt (inclure le mode)
            context = self._build_context(learner_profile, emotion_result, query, mode)
            
            # 4) Génération de la réponse
            response_text = self._generate_response(context, query)
            
            # 5) Mise à jour du profil
            self._update_learner_profile(learner_id, query, response_text, emotion_result)
            
            return {
                "response": response_text,
                "emotion": emotion_result,
                "learner_id": learner_id,
                "mode": mode
            }
        
        except Exception as e:
            logger.exception("process_query failed for learner_id=%s: %s", learner_id, e)
            return {
                "response": "Je rencontre une difficulté technique. Veuillez réessayer.",
                "emotion": {"dominant_emotion": "neutre", "confidence": 0.0},
                "learner_id": learner_id
            }

    def _analyze_emotion(self, text: str) -> Dict[str, Any]:
        """Analyse l'émotion du texte."""
        if not self.emotion_client:
            logger.warning("EmotionClient not available")
            return {"dominant_emotion": "neutre", "confidence": 0.0, "source": "none"}
        
        try:
            result = self.emotion_client.analyze(text)
            logger.info("Emotion: %s (conf=%.2f)", 
                       result.get("dominant_emotion"), 
                       result.get("confidence", 0.0))
            return result
        except Exception as e:
            logger.warning("Emotion analysis failed: %s", e)
            return {"dominant_emotion": "neutre", "confidence": 0.0, "source": "error"}

    def _get_or_create_learner(self, learner_id: str) -> Dict[str, Any]:
        """Récupère ou crée un profil apprenant."""
        if learner_id not in self._learners:
            self._learners[learner_id] = {
                "learner_id": learner_id,
                "history": [],
                "preferences": {},
                "created_at": datetime.datetime.utcnow().isoformat()
            }
            logger.info("Created new learner profile: %s", learner_id)
        return self._learners[learner_id]

    def _build_context(self, learner_profile: Dict, emotion: Dict, query: str, mode: str = "explain") -> str:
        """Construit le contexte pour le prompt Groq."""
        emotion_label = emotion.get("dominant_emotion", "neutre")
        confidence = emotion.get("confidence", 0.0)
        
        # Adapter le prompt selon le mode
        mode_instructions = {
            "explain": "Provide a clear, detailed explanation with examples.",
            "quiz": "Create quiz questions based on the topic.",
            "summarize": "Provide a concise summary of the key points.",
            "define": "Give a precise definition with context."
        }
        instruction = mode_instructions.get(mode, mode_instructions["explain"])
        
        context = f"""You are CLEO, an adaptive learning assistant specialized in personalized education.

    Current context:
    - User emotion: {emotion_label} (confidence: {confidence:.2f})
    - Mode: {mode} - {instruction}
    - Adapt your tone based on emotion (encouraging if sad/frustrated, enthusiastic if happy)

    Guidelines:
    - Provide clear, educational responses
    - Use examples when helpful
    - Break down complex concepts
    - Encourage continuous learning"""

        # Historique récent
        history = learner_profile.get("history", [])
        if history:
            recent = history[-3:]
            context += "\n\nRecent conversation:"
            for idx, h in enumerate(recent, 1):
                context += f"\n{idx}. User: {h.get('query', '')[:100]}"
                context += f"\n   You: {h.get('response', '')[:100]}"
        
        return context

    def _generate_response(self, context: str, query: str) -> str:
        """Génère la réponse via GroqClient."""
        if not self.groq_client:
            logger.warning("GroqClient not available")
            return "Le service de génération de réponse n'est pas disponible. Vérifiez GROQ_API_KEY."
        
        try:
            full_prompt = f"{context}\n\nUser: {query}\n\nAssistant:"
            response = self.groq_client.chat(full_prompt)
            logger.info("Response generated (len=%d)", len(response))
            return response
        except Exception as e:
            logger.exception("Response generation failed: %s", e)
            return f"Erreur lors de la génération de la réponse: {str(e)}"

    def _update_learner_profile(self, learner_id: str, query: str, response: str, emotion: Dict):
        """Met à jour l'historique de l'apprenant."""
        if learner_id in self._learners:
            self._learners[learner_id]["history"].append({
                "query": query,
                "response": response,
                "emotion": emotion.get("dominant_emotion"),
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
            # Garder seulement les 50 derniers
            if len(self._learners[learner_id]["history"]) > 50:
                self._learners[learner_id]["history"] = self._learners[learner_id]["history"][-50:]