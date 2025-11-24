import os
import logging
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("cleo.groq")
logger.setLevel(logging.INFO)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "30"))


class GroqClient:
    """Client pour l'API Groq (génération de réponses)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        self.api_url = GROQ_API_URL
        self.model = GROQ_MODEL
        logger.info("GroqClient initialized: api_key_set=%s model=%s", bool(self.api_key), self.model)

    def chat(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Envoie un prompt à Groq et retourne la réponse.
        
        Args:
            prompt: Le prompt complet (contexte + question)
            max_tokens: Nombre max de tokens dans la réponse
            
        Returns:
            str: La réponse générée
        """
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=GROQ_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            # Extraire le contenu de la réponse
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                logger.warning("Empty response from Groq")
                return "Désolé, je n'ai pas pu générer une réponse."
            
            return content.strip()
        
        except requests.exceptions.HTTPError as e:
            logger.error("Groq HTTP error: %s - %s", e.response.status_code, e.response.text)
            if e.response.status_code == 401:
                return "Erreur d'authentification Groq. Vérifiez GROQ_API_KEY."
            return f"Erreur Groq ({e.response.status_code})"
        
        except Exception as e:
            logger.exception("Groq request failed: %s", e)
            return f"Erreur lors de l'appel à Groq: {str(e)}"