from __future__ import annotations

import hashlib
import json
from typing import Any

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SemanticCache:
    """In-memory cache with optional semantic similarity when embeddings are available."""

    def __init__(self, threshold: float = 0.92) -> None:
        self._entries: list[dict[str, Any]] = []
        self._exact: dict[str, dict[str, Any]] = {}
        self._threshold = threshold
        self._encoder = None
        try:
            from sentence_transformers import SentenceTransformer

            self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            logger.info("Semantic similarity disabled (sentence-transformers not installed).")

    def _key(self, question: str) -> str:
        return hashlib.sha256(question.strip().lower().encode()).hexdigest()

    def get(self, question: str) -> dict[str, Any] | None:
        if not settings.SEMANTIC_CACHE_ENABLED:
            return None
        key = self._key(question)
        if key in self._exact:
            logger.info("Exact cache hit")
            return self._exact[key]

        if self._encoder is None:
            return None

        from sentence_transformers.util import cos_sim

        q_emb = self._encoder.encode(question)
        for entry in self._entries:
            sim = float(cos_sim(q_emb, entry["embedding"])[0][0])
            if sim >= self._threshold:
                logger.info("Semantic cache hit (similarity=%.3f)", sim)
                return entry["payload"]
        return None

    def set(self, question: str, payload: dict[str, Any]) -> None:
        if not settings.SEMANTIC_CACHE_ENABLED:
            return
        self._exact[self._key(question)] = payload
        if self._encoder is not None:
            self._entries.append(
                {
                    "embedding": self._encoder.encode(question),
                    "payload": payload,
                }
            )
            if len(self._entries) > 200:
                self._entries.pop(0)
