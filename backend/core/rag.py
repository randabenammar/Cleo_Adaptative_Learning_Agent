"""
RAG wrapper avec chargement lazy du modèle d'embeddings et du client Chroma.
But: éviter les téléchargements/initialisations lourdes lors de l'import du module.
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import local au besoin (lazy)
_EMB_MODEL_ENV = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_pdf_db")
_DEFAULT_COLLECTION = "adaptive_learning_kb"

class RAG:
    def __init__(self, embedding_model_name: str = _EMB_MODEL_ENV, collection_name: str = _DEFAULT_COLLECTION):
        # Ne pas instancier SentenceTransformer ni Chromadb ici — faire lazy.
        self._embedding_model_name = embedding_model_name
        self._collection_name = collection_name
        self.embedding_model = None
        self.client = None
        self.collection = None

    def _ensure_embedding(self):
        if self.embedding_model is None:
            # Import gourmand placé ici
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(self._embedding_model_name)

    def _ensure_chroma(self):
        if self.client is None:
            # Import et création de client Chromadb ici (lazy)
            import chromadb
            # Using PersistentClient if available
            try:
                from chromadb.config import Settings
                self.client = chromadb.PersistentClient(path=_CHROMA_PATH)
            except Exception:
                # fallback to in-memory client
                self.client = chromadb.Client()
            # create/get collection
            try:
                self.collection = self.client.get_collection(name=self._collection_name)
            except Exception:
                self.collection = self.client.create_collection(name=self._collection_name)

    def add_documents(self, docs: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        # Ensure model + client available
        self._ensure_embedding()
        self._ensure_chroma()
        embeddings = self.embedding_model.encode(docs, convert_to_numpy=True).tolist()
        ids = [f"doc_{int(datetime.utcnow().timestamp())}_{i}" for i in range(len(docs))]
        self.collection.add(embeddings=embeddings, documents=docs, metadatas=metadatas or [{}]*len(docs), ids=ids)

    def retrieve(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        # If no collection or empty, return empty list quickly
        # Prepare model & client lazily
        self._ensure_embedding()
        self._ensure_chroma()
        # If collection has no docs, avoid querying
        try:
            count = self.collection.count()
        except Exception:
            count = 0
        if count == 0:
            return []
        q_emb = self.embedding_model.encode([query], convert_to_numpy=True).tolist()
        results = self.collection.query(query_embeddings=q_emb, n_results=n_results)
        formatted = []
        # results expected structure: documents, metadatas, distances
        docs = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0] if results.get('distances') else [1.0]*len(docs)
        for i, doc in enumerate(docs):
            distance = distances[i] if i < len(distances) else 1.0
            formatted.append({
                "content": doc,
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "distance": distance,
                "relevance": max(0, 1 - distance)
            })
        return formatted