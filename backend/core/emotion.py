import os
import logging
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Charge .env si nécessaire (sûr même si app.py fait déjà le load)
load_dotenv()

logger = logging.getLogger("cleo.emotion")
logger.setLevel(logging.INFO)

# Accepte plusieurs noms d'env pour compatibilité
HF_API_KEY = os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HUGGING_FACE_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "nateraw/bert-base-uncased-emotion")
# Par défaut utilisons le Router URL recommandé par Hugging Face
HF_API_URL = os.getenv("HF_API_URL", f"https://router.huggingface.co/hf-inference/{HF_MODEL}")
HF_TIMEOUT = int(os.getenv("HF_TIMEOUT", "15"))

def _router_url_for_model(model: str) -> str:
    return f"https://router.huggingface.co/hf-inference/{model}"

class EmotionClient:
    """
    Client d'émotion utilisant uniquement l'API Hugging Face Router (online).
    - nécessite HF_API_KEY dans .env (ou HUGGINGFACE_API_KEY)
    - renvoie un dict normalisé et gère 401/404/410 sans lever d'exception 500
    """

    def __init__(self, hf_api_key: Optional[str] = None, hf_api_url: Optional[str] = None, hf_model: Optional[str] = None):
        self.hf_api_key = hf_api_key or HF_API_KEY
        self.hf_model = hf_model or HF_MODEL
        self.hf_api_url = hf_api_url or HF_API_URL
        logger.info("EmotionClient init: model=%s api_url=%s HF_key_set=%s", self.hf_model, self.hf_api_url, bool(self.hf_api_key))

    def _call_url(self, url: str, text: str) -> Optional[requests.Response]:
        headers = {"Content-Type": "application/json"}
        if self.hf_api_key:
            headers["Authorization"] = f"Bearer {self.hf_api_key}"
        try:
            resp = requests.post(url, headers=headers, json={"inputs": text}, timeout=HF_TIMEOUT)
            return resp
        except requests.exceptions.RequestException as e:
            logger.warning("HF inference request exception for url=%s: %s", url, e)
            return None

    def analyze(self, text: str) -> Dict[str, Any]:
        text = (text or "").strip()
        if not text:
            return {"dominant_emotion": "neutre", "confidence": 0.0, "raw": None, "source": "none", "note": "empty text"}

        tried_urls = []
        # 1) essayer l'URL configurée (HF_API_URL), puis router (fallback si jamais)
        for attempt in range(2):
            url = self.hf_api_url if attempt == 0 else _router_url_for_model(self.hf_model)
            tried_urls.append(url)
            logger.info("Calling HF Router (attempt %d) url=%s", attempt + 1, url)
            resp = self._call_url(url, text)
            if resp is None:
                logger.warning("No response from HF at url=%s (network/timeout)", url)
                continue

            logger.info("HF response: status=%s url=%s", resp.status_code, url)

            if resp.status_code == 401:
                logger.warning("HF unauthorized (401) for url=%s - check HF_API_KEY", url)
                return {"dominant_emotion": "neutre", "confidence": 0.0, "raw": resp.text, "source": "hf", "note": "unauthorized_401", "tried_urls": tried_urls}
            if resp.status_code == 404:
                logger.warning("HF model not found (404) for url=%s", url)
                if attempt == 0:
                    # essayer router au prochain tour
                    continue
                return {"dominant_emotion": "neutre", "confidence": 0.0, "raw": resp.text, "source": "hf", "note": "model_not_found_404", "tried_urls": tried_urls}
            if resp.status_code == 410:
                logger.warning("HF model gone (410) for url=%s", url)
                if attempt == 0:
                    continue
                return {"dominant_emotion": "neutre", "confidence": 0.0, "raw": resp.text, "source": "hf", "note": "model_gone_410", "tried_urls": tried_urls}

            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.warning("HF raise_for_status error for url=%s: %s", url, e)
                if attempt == 0:
                    continue
                return {"dominant_emotion": "neutre", "confidence": 0.0, "raw": resp.text, "source": "hf", "note": f"http_error_{resp.status_code}", "tried_urls": tried_urls}

            # parse JSON success
            try:
                data = resp.json()
            except Exception as e:
                logger.exception("Invalid JSON from HF: %s", e)
                return {"dominant_emotion": "neutre", "confidence": 0.0, "raw": resp.text, "source": "hf", "note": "invalid_json", "tried_urls": tried_urls}

            # normaliser formes communes
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                best = max(data, key=lambda x: x.get("score", 0.0))
                label = best.get("label")
                score = float(best.get("score", 0.0))
                dominant = self._map_label(label)
                return {"dominant_emotion": dominant, "confidence": score, "raw": data, "source": "hf", "model": self.hf_model, "tried_urls": tried_urls}
            if isinstance(data, dict):
                label = data.get("label") or data.get("emotion") or None
                score = data.get("score") or 0.0
                dominant = self._map_label(label)
                return {"dominant_emotion": dominant, "confidence": float(score or 0.0), "raw": data, "source": "hf", "model": self.hf_model, "tried_urls": tried_urls}
            # normaliser formes communes
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                best = max(data, key=lambda x: x.get("score", 0.0))
                label = best.get("label")
                score = float(best.get("score", 0.0))
                dominant = self._map_label(label)
                return {"dominant_emotion": dominant, "confidence": score, "raw": data, "source": "hf", "model": self.hf_model, "tried_urls": tried_urls}

            # ✅ ajout : gérer le cas [ [ {...}, {...} ] ]
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list) and len(data[0]) > 0 and isinstance(data[0][0], dict):
                inner = data[0]
                best = max(inner, key=lambda x: x.get("score", 0.0))
                label = best.get("label")
                score = float(best.get("score", 0.0))
                dominant = self._map_label(label)
                return {"dominant_emotion": dominant, "confidence": score, "raw": inner, "source": "hf", "model": self.hf_model, "tried_urls": tried_urls}

            if isinstance(data, dict):
                label = data.get("label") or data.get("emotion") or None
                score = data.get("score") or 0.0
                dominant = self._map_label(label)
                return {"dominant_emotion": dominant, "confidence": float(score or 0.0), "raw": data, "source": "hf", "model": self.hf_model, "tried_urls": tried_urls}

            logger.warning("HF returned unexpected data shape: %s", type(data))
            return {"dominant_emotion": "neutre", "confidence": 0.0, "raw": data, "source": "hf", "note": "unexpected_shape", "tried_urls": tried_urls}

        # si on arrive ici -> fallback heuristique
        logger.warning("HF inference attempts failed for urls: %s", tried_urls)
        t = text.lower()
        if any(w in t for w in ["happy", "joy", "glad", "great", "amazing", "excited"]):
            return {"dominant_emotion": "happy", "confidence": 0.6, "raw": None, "source": "fallback", "tried_urls": tried_urls}
        if any(w in t for w in ["sad", "unhappy", "depressed", "angry", "frustrated"]):
            return {"dominant_emotion": "sad", "confidence": 0.6, "raw": None, "source": "fallback", "tried_urls": tried_urls}
        return {"dominant_emotion": "neutre", "confidence": 0.2, "raw": None, "source": "fallback", "tried_urls": tried_urls}

    def _map_label(self, label: Optional[str]) -> str:
        if not label:
            return "neutre"
        l = str(label).lower()
        if any(k in l for k in ["joy", "happy", "positive", "excited", "love", "surprise"]):
            return "happy"
        if any(k in l for k in ["sad", "sadness", "angry", "anger", "fear", "negative", "disgust"]):
            if "angry" in l or "anger" in l:
                return "angry"
            return "sad"
        return "neutre"