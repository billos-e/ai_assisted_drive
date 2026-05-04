from __future__ import annotations

from dataclasses import dataclass

from chat.groq_client import GroqClient
from config import Settings
from drive.client import DriveClient
from extraction.dispatcher import TextExtractor
from vectorstore.chroma_client import ChromaRepository
from vectorstore.embedder import GeminiEmbedder
from vectorstore.indexer import RepositoryIndexer
from google import genai


@dataclass(slots=True)
class AppServices:
    settings: Settings
    drive: DriveClient
    extractor: TextExtractor
    indexer: RepositoryIndexer
    chat: GroqClient


def build_services(settings: Settings) -> AppServices:
    gemini_client = genai.Client(api_key=settings.gemini_api_key)
    chat = GroqClient(settings)
    embedder = GeminiEmbedder(settings, gemini_client)
    vectorstore = ChromaRepository(settings=settings, embedder=embedder)
    extractor = TextExtractor(settings=settings, groq_client=chat, gemini_client=gemini_client)
    indexer = RepositoryIndexer(settings=settings, vectorstore=vectorstore, embedder=embedder)
    drive = DriveClient(settings=settings)
    return AppServices(settings=settings, drive=drive, extractor=extractor, indexer=indexer, chat=chat)
