from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DriveItemType = Literal["file", "folder"]


class DriveItem(BaseModel):
    id: str
    name: str
    type: DriveItemType
    mime_type: str


class DriveFolderCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    folder_id: str | None = Field(default=None, min_length=1)


class DriveUploadResponse(BaseModel):
    id: str
    name: str


class Source(BaseModel):
    """Represents a source document chunk."""
    source_path: str
    file_name: str
    file_id: str
    chunk_index: int
    distance: float


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    sources: list[Source] = Field(default_factory=list)


class ChatStreamRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)


class DriveDeleteResponse(BaseModel):
    message: str
    deleted_id: str


class DriveOpenResponse(BaseModel):
    url: str


class SettingsResponse(BaseModel):
    google_account: str
    root_folder_id: str
    indexed_files_count: int
    selected_model: str
    number_of_sources: int
    response_language: str


class SettingsUpdate(BaseModel):
    root_folder_id: str | None = None
    selected_model: str | None = None
    number_of_sources: int | None = None
    response_language: str | None = None
