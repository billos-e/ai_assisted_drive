from __future__ import annotations

from functools import lru_cache

import google.generativeai as genai

from ..config import Settings


class GeminiEmbedder:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        genai.configure(api_key=settings.gemini_api_key)

    def embed(self, text: str) -> list[float]:
        response = genai.embed_content(model=self._settings.embedding_model, content=text)
        embedding = getattr(response, "embedding", None)
        if embedding is None and isinstance(response, dict):
            embedding = response.get("embedding")
        if hasattr(embedding, "values"):
            return list(embedding.values)
        if isinstance(embedding, dict) and "values" in embedding:
            return list(embedding["values"])
        if isinstance(response, dict) and "embedding" in response and isinstance(response["embedding"], dict):
            values = response["embedding"].get("values")
            if values is not None:
                return list(values)
        raise RuntimeError("Unexpected Gemini embedding response")
