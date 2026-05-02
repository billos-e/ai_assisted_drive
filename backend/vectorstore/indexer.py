from __future__ import annotations

from dataclasses import dataclass

from config import Settings
from vectorstore.chroma_client import ChromaRepository
from vectorstore.embedder import GeminiEmbedder


@dataclass(slots=True)
class RetrievedChunk:
    text: str
    file_id: str
    file_name: str
    folder_path: str
    chunk_index: int
    distance: float | None = None


class RepositoryIndexer:
    def __init__(self, settings: Settings, vectorstore: ChromaRepository, embedder: GeminiEmbedder) -> None:
        self._settings = settings
        self._vectorstore = vectorstore
        self._embedder = embedder

    def chunk_text(self, text: str) -> list[str]:
        words = text.split()
        if not words:
            return []

        chunk_size = self._settings.chunk_size_words
        overlap = min(self._settings.chunk_overlap_words, chunk_size - 1)
        step = max(chunk_size - overlap, 1)
        chunks: list[str] = []
        start = 0
        while start < len(words):
            chunk_words = words[start : start + chunk_size]
            if not chunk_words:
                break
            chunks.append(" ".join(chunk_words))
            if start + chunk_size >= len(words):
                break
            start += step
        return chunks

    def index_text(
        self,
        *,
        file_id: str,
        file_name: str,
        folder_path: str,
        mime_type: str,
        text: str,
    ) -> int:
        chunks = [chunk for chunk in self.chunk_text(text) if chunk.strip()]
        if not chunks:
            return 0

        embeddings = [self._embedder.embed_document(chunk) for chunk in chunks]
        ids = [f"{file_id}:{chunk_index}" for chunk_index in range(len(chunks))]
        metadatas = [
            {
                "drive_file_id": file_id,
                "file_name": file_name,
                "folder_path": folder_path,
                "chunk_index": chunk_index,
                "mime_type": mime_type,
            }
            for chunk_index in range(len(chunks))
        ]
        self._vectorstore.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        return len(chunks)

    def get_indexed_file_ids(self) -> set[str]:
        result = self._vectorstore.collection.get(include=["metadatas"])
        file_ids: set[str] = set()
        for metadata in result.get("metadatas", []) or []:
            if isinstance(metadata, dict):
                file_id = metadata.get("drive_file_id")
                if file_id:
                    file_ids.add(str(file_id))
        return file_ids

    def search(self, query: str, top_k: int) -> list[dict[str, str]]:
        embedding = self._embedder.embed_query(query)
        result = self._vectorstore.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        chunks: list[dict[str, str]] = []
        for document, metadata, distance in zip(documents, metadatas, distances, strict=False):
            if not document or not isinstance(metadata, dict):
                continue
            chunks.append(
                {
                    "text": document,
                    "file_id": str(metadata.get("drive_file_id", "")),
                    "file_name": str(metadata.get("file_name", "")),
                    "folder_path": str(metadata.get("folder_path", "")),
                    "chunk_index": str(metadata.get("chunk_index", "")),
                    "distance": str(distance),
                }
            )
        return chunks
