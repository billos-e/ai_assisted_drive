from __future__ import annotations

from pathlib import Path

from chat.groq_client import GroqClient
from config import Settings
from extraction.audio_video import extract_audio_video_bytes
from extraction.docx import extract_docx_bytes
from extraction.pdf import extract_pdf_bytes
from extraction.pptx import extract_pptx_bytes
from extraction.spreadsheet import extract_spreadsheet_bytes
from extraction.text import extract_text_bytes


class TextExtractor:
    def __init__(self, settings: Settings, groq_client: GroqClient) -> None:
        self._settings = settings
        self._groq_client = groq_client

    def extract_bytes(self, *, content: bytes, filename: str, mime_type: str) -> str:
        extension = Path(filename).suffix.lower()
        mime_type = (mime_type or "").lower()

        if mime_type == "application/pdf" or extension == ".pdf":
            return extract_pdf_bytes(content, self._settings.ocr_languages)

        if mime_type in {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        } or extension == ".docx":
            return extract_docx_bytes(content)

        if mime_type in {
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint",
        } or extension == ".pptx":
            return extract_pptx_bytes(content)

        if mime_type in {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/csv",
        } or extension in {".xlsx", ".xls", ".csv"}:
            return extract_spreadsheet_bytes(content, filename)

        if mime_type.startswith("audio/") or mime_type.startswith("video/") or extension in {
            ".mp3",
            ".wav",
            ".m4a",
            ".flac",
            ".aac",
            ".mp4",
            ".mov",
            ".mkv",
            ".avi",
            ".webm",
        }:
            return extract_audio_video_bytes(content, filename, mime_type, self._groq_client)

        if mime_type.startswith("text/") or extension in {
            ".txt",
            ".md",
            ".rst",
            ".csv",
            ".py",
            ".js",
            ".ts",
            ".json",
            ".xml",
            ".html",
            ".htm",
            ".css",
            ".yml",
            ".yaml",
            ".log",
        }:
            return extract_text_bytes(content)

        return ""
