from __future__ import annotations

import chromadb

from ..config import Settings
from .embedder import GeminiEmbedder


class ChromaRepository:
    def __init__(self, settings: Settings, embedder: GeminiEmbedder) -> None:
        self._settings = settings
        self._embedder = embedder
        self._client = chromadb.PersistentClient(path=settings.chroma_path)
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def collection(self):
        return self._collection
