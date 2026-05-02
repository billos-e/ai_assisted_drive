from __future__ import annotations

import io
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal

from fastapi import UploadFile
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from config import Settings


@dataclass(slots=True)
class DriveNode:
    id: str
    name: str
    mime_type: str
    type: Literal["file", "folder"]
    folder_path: str = "/"


class DriveClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        token_info = settings.google_token_info
        credentials = OAuthCredentials.from_authorized_user_info(
            token_info,
            scopes=["https://www.googleapis.com/auth/drive.file"],
        )
        # Ensure credentials are valid / refreshed before use
        if not credentials.valid and credentials.refresh_token:
            credentials.refresh(Request())
        self._service = build("drive", "v3", credentials=credentials, cache_discovery=False)

    def list_folder(self, folder_id: str | None = None) -> list[DriveNode]:
        parent_id = folder_id or self._settings.google_drive_root_folder_id
        query = f"'{parent_id}' in parents and trashed = false"
        request = self._service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageSize=1000,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        )
        items: list[DriveNode] = []
        while request is not None:
            response = request.execute()
            for item in response.get("files", []):
                mime_type = item.get("mimeType", "")
                items.append(
                    DriveNode(
                        id=item["id"],
                        name=item.get("name", ""),
                        mime_type=mime_type,
                        type="folder" if mime_type == "application/vnd.google-apps.folder" else "file",
                    )
                )
            request = self._service.files().list_next(request, response)
        return items

    def create_folder(self, name: str, folder_id: str | None = None) -> DriveNode:
        parent_id = folder_id or self._settings.google_drive_root_folder_id
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        created = self._service.files().create(
            body=metadata,
            fields="id, name, mimeType",
            supportsAllDrives=True,
        ).execute()
        return DriveNode(
            id=created["id"],
            name=created.get("name", name),
            mime_type=created.get("mimeType", "application/vnd.google-apps.folder"),
            type="folder",
        )

    def upload_bytes(
        self,
        *,
        filename: str,
        content: bytes,
        folder_id: str | None = None,
        mime_type: str | None = None,
    ) -> DriveNode:
        parent_id = folder_id or self._settings.google_drive_root_folder_id
        guessed_mime_type = mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=guessed_mime_type, resumable=True)
        created = self._service.files().create(
            body={"name": filename, "parents": [parent_id]},
            media_body=media,
            fields="id, name, mimeType",
            supportsAllDrives=True,
        ).execute()
        return DriveNode(
            id=created["id"],
            name=created.get("name", filename),
            mime_type=created.get("mimeType", guessed_mime_type),
            type="file",
        )

    def get_metadata(self, file_id: str) -> dict[str, str]:
        return self._service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, parents",
            supportsAllDrives=True,
        ).execute()

    def get_folder_path(self, folder_id: str | None = None) -> str:
        target_id = folder_id or self._settings.google_drive_root_folder_id
        if target_id == self._settings.google_drive_root_folder_id:
            return "/"

        parts: list[str] = []
        current_id = target_id
        while current_id and current_id != self._settings.google_drive_root_folder_id:
            metadata = self._service.files().get(
                fileId=current_id,
                fields="id, name, parents",
                supportsAllDrives=True,
            ).execute()
            name = metadata.get("name")
            if name:
                parts.append(name)
            parents = metadata.get("parents") or []
            if not parents:
                break
            current_id = parents[0]

        return "/" + "/".join(reversed(parts)) if parts else "/"

    def download_bytes(self, file_id: str) -> bytes:
        metadata = self.get_metadata(file_id)
        mime_type = metadata.get("mimeType", "")
        if mime_type == "application/vnd.google-apps.folder":
            raise ValueError("Cannot download a folder")

        request = self._build_download_request(file_id, mime_type)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue()

    def walk_repository(self, folder_id: str | None = None, current_path: str = "/") -> Iterator[DriveNode]:
        for item in self.list_folder(folder_id):
            if item.type == "folder":
                child_path = self._join_path(current_path, item.name)
                yield DriveNode(
                    id=item.id,
                    name=item.name,
                    mime_type=item.mime_type,
                    type="folder",
                    folder_path=child_path,
                )
                yield from self.walk_repository(item.id, child_path)
            else:
                yield DriveNode(
                    id=item.id,
                    name=item.name,
                    mime_type=item.mime_type,
                    type="file",
                    folder_path=current_path or "/",
                )

    def _build_download_request(self, file_id: str, mime_type: str):
        export_mime_type = self._export_mime_type(mime_type)
        if export_mime_type is not None:
            return self._service.files().export_media(fileId=file_id, mimeType=export_mime_type)
        return self._service.files().get_media(fileId=file_id, supportsAllDrives=True)

    @staticmethod
    def _join_path(parent: str, name: str) -> str:
        parent = parent.rstrip("/")
        if not parent:
            return f"/{name}"
        return f"{parent}/{name}"

    def delete_file(self, file_id: str) -> None:
        """
        Delete a file or folder from Google Drive.

        Args:
            file_id: The ID of the file or folder to delete.

        Raises:
            ValueError: If the file_id is not provided.
            Exception: If the deletion fails due to API errors.
        """
        if not file_id:
            raise ValueError("file_id cannot be empty")
        
        try:
            self._service.files().delete(
                fileId=file_id,
                supportsAllDrives=True,
            ).execute()
        except Exception as e:
            raise Exception(f"Failed to delete file {file_id}: {str(e)}")

    def get_file_url(self, file_id: str) -> str:
        """
        Get the Google Drive web view URL for a file.

        Args:
            file_id: The ID of the file.

        Returns:
            The Google Drive URL for the file.

        Raises:
            ValueError: If the file_id is not provided.
            Exception: If fetching metadata fails due to API errors.
        """
        if not file_id:
            raise ValueError("file_id cannot be empty")
        
        try:
            metadata = self._service.files().get(
                fileId=file_id,
                fields="webViewLink",
                supportsAllDrives=True,
            ).execute()
            url = metadata.get("webViewLink")
            if not url:
                raise ValueError(f"Could not retrieve URL for file {file_id}")
            return url
        except Exception as e:
            raise Exception(f"Failed to get file URL for {file_id}: {str(e)}")

    @staticmethod
    def _export_mime_type(mime_type: str) -> str | None:
        export_map = {
            "application/vnd.google-apps.document": "text/plain",
            "application/vnd.google-apps.spreadsheet": "text/csv",
            "application/vnd.google-apps.presentation": "text/plain",
            "application/vnd.google-apps.drawing": "image/png",
        }
        return export_map.get(mime_type)
