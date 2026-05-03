from __future__ import annotations

from dataclasses import dataclass

from chat.groq_client import GroqClient
from config import Settings
from drive.client import DriveClient
from extraction.dispatcher import TextExtractor
from vectorstore.chroma_client import ChromaRepository
from vectorstore.embedder import GeminiEmbedder
from vectorstore.indexer import RepositoryIndexer


@dataclass(slots=True)
class AppServices:
    settings: Settings
    drive: DriveClient
    extractor: TextExtractor
    indexer: RepositoryIndexer
    chat: GroqClient


def build_services(settings: Settings) -> AppServices:
    chat = GroqClient(settings)
    embedder = GeminiEmbedder(settings)
    vectorstore = ChromaRepository(settings=settings, embedder=embedder)
    extractor = TextExtractor(settings=settings, groq_client=chat)
    indexer = RepositoryIndexer(settings=settings, vectorstore=vectorstore, embedder=embedder)
    drive = DriveClient(settings=settings)
    return AppServices(settings=settings, drive=drive, extractor=extractor, indexer=indexer, chat=chat)
