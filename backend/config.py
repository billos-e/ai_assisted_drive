from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    google_client_id: str = Field(alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(alias="GOOGLE_CLIENT_SECRET")
    google_token_json: str = Field(alias="GOOGLE_TOKEN_JSON")
    google_drive_root_folder_id: str = Field(alias="GOOGLE_DRIVE_ROOT_FOLDER_ID")
    gemini_api_key: str = Field(alias="GEMINI_API_KEY")
    groq_api_key: str = Field(alias="GROQ_API_KEY")
    api_base_url: str = Field(default="http://127.0.0.1:8000", alias="API_BASE_URL")
    chroma_path: str = Field(default=str(BASE_DIR / "chroma_db"), alias="CHROMA_PATH")

    @field_validator("chroma_path", mode="before")
    @classmethod
    def resolve_chroma_path(cls, v: str) -> str:
        """Convert relative paths to absolute paths relative to backend directory."""
        path = Path(v)
        if not path.is_absolute():
            path = BASE_DIR / path
        return str(path)

    chroma_collection_name: str = "drive_repository"
    embedding_model: str = "gemini-embedding-2"
    groq_chat_model: str = "llama-3.3-70b-versatile"
    groq_whisper_model: str = "whisper-large-v3"
    max_upload_size_mb: int = 100
    ocr_languages: tuple[str, str] = ("fra", "eng")
    chunk_size_words: int = 500
    chunk_overlap_words: int = 50
    retrieval_top_k: int = 5

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def service_account_info(self) -> dict[str, Any]:
        raise AttributeError("service_account_info is removed. Use google_token_info for OAuth2 migration.")

    @property
    def google_token_info(self) -> dict[str, Any]:
        """Parse `GOOGLE_TOKEN_JSON` environment variable into a dict.

        The variable is expected to contain the JSON content of the token file
        produced by the OAuth2 flow (the same structure returned by
        `Credentials.to_json()` from `google-auth-oauthlib`).
        """
        raw = self.google_token_json.strip()
        while raw and raw[0] in {'"', "'"} and raw[-1] == raw[0]:
            raw = raw[1:-1].strip()
        raw = raw.rstrip("% ").strip()
        return json.loads(raw)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
