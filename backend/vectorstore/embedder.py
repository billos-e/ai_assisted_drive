from __future__ import annotations

from google import genai

from config import Settings


class GeminiEmbedder:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def _embedding_values(self, response: object) -> list[float]:
        embeddings = getattr(response, "embeddings", None)
        if embeddings is None and isinstance(response, dict):
            embeddings = response.get("embeddings")
        if isinstance(embeddings, list) and embeddings:
            first_embedding = embeddings[0]
            if hasattr(first_embedding, "values"):
                return list(first_embedding.values)
            if isinstance(first_embedding, dict) and "values" in first_embedding:
                return list(first_embedding["values"])
        raise RuntimeError("Unexpected Gemini embedding response")

    def embed_document(self, text: str) -> list[float]:
        response = self._client.models.embed_content(
            model=self._settings.embedding_model,
            contents=[f"title: none | text: {text}"],
        )
        return self._embedding_values(response)

    def embed_query(self, text: str) -> list[float]:
        response = self._client.models.embed_content(
            model=self._settings.embedding_model,
            contents=[f"task: search result | query: {text}"],
        )
        return self._embedding_values(response)
