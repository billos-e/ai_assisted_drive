from __future__ import annotations

import asyncio
import mimetypes
from functools import lru_cache
from collections.abc import Iterator

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config import Settings, get_settings
from schemas import ChatStreamRequest, DriveFolderCreateRequest, DriveItem, DriveUploadResponse
from services import AppServices, build_services
from startup import sync_repository_index


@lru_cache(maxsize=1)
def get_app_services() -> AppServices:
    """
    Get the application services.

    This function is cached to ensure that the services are only built once.

    Returns:
        The application services.
    """
    settings = get_settings()
    return build_services(settings)


def get_services(request: Request) -> AppServices:
    """
    Get the application services from the request.

    Args:
        request: The request object.

    Returns:
        The application services.
    """
    services = getattr(request.app.state, "services", None)
    if services is None:
        raise RuntimeError("Application services are not initialized")
    return services


def create_app() -> FastAPI:
    """
    Create the FastAPI application.

    This function creates the FastAPI application, adds the middleware, initializes the services,
    and defines the routes.

    Returns:
        The FastAPI application.
    """
    settings = get_settings()
    app = FastAPI(
        title="AI Assisted Drive Backend",
        version="0.1.0",
        servers=[{"url": settings.api_base_url}],
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.services = build_services(settings)

    @app.on_event("startup")
    async def run_startup_index() -> None:
        """Run the startup index synchronization."""
        await asyncio.to_thread(sync_repository_index, app.state.services)

    @app.get("/health")
    def health() -> dict[str, str]:
        """
        Health check endpoint.

        Returns:
            A dictionary with the status.
        """
        return {"status": "ok"}

    @app.get("/drive/list", response_model=list[DriveItem])
    def drive_list(request: Request, folder_id: str | None = Query(default=None)) -> list[DriveItem]:
        """
        List the content of a folder in the drive.

        Args:
            request: The request object.
            folder_id: The ID of the folder to list.

        Returns:
            A list of drive items.
        """
        services = get_services(request)
        items = services.drive.list_folder(folder_id)
        return [DriveItem(id=item.id, name=item.name, type=item.type, mime_type=item.mime_type) for item in items]

    @app.post("/drive/folder", response_model=DriveUploadResponse)
    def drive_folder(payload: DriveFolderCreateRequest, request: Request) -> DriveUploadResponse:
        """
        Create a new folder in the drive.

        Args:
            payload: The request payload.
            request: The request object.

        Returns:
            The created folder information.
        """
        services = get_services(request)
        created = services.drive.create_folder(name=payload.name, folder_id=payload.folder_id)
        return DriveUploadResponse(id=created.id, name=created.name)

    @app.post("/drive/upload", response_model=DriveUploadResponse)
    async def drive_upload(
        request: Request,
        file: UploadFile = File(...),
        folder_id: str | None = Form(default=None),
    ) -> DriveUploadResponse:
        """
        Upload a file to the drive, extracts its content and indexes it.

        Args:
            request: The request object.
            file: The file to upload.
            folder_id: The ID of the folder to upload the file to.

        Returns:
            The uploaded file information.
        """
        services = get_services(request)
        content = await file.read()
        if len(content) > services.settings.max_upload_size_bytes:
            raise HTTPException(status_code=413, detail="File exceeds 100 MB limit")

        content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
        created = services.drive.upload_bytes(
            filename=file.filename or "untitled",
            content=content,
            folder_id=folder_id,
            mime_type=content_type,
        )

        extracted_text = services.extractor.extract_bytes(content=content, filename=created.name, mime_type=created.mime_type)
        if extracted_text.strip():
            services.indexer.index_text(
                file_id=created.id,
                file_name=created.name,
                folder_path=services.drive.get_folder_path(folder_id),
                mime_type=created.mime_type,
                text=extracted_text,
            )

        return DriveUploadResponse(id=created.id, name=created.name)

    @app.post("/chat/stream")
    def chat_stream(payload: ChatStreamRequest, request: Request) -> StreamingResponse:
        """
        Handle the chat streaming.

        Args:
            payload: The request payload.
            request: The request object.

        Returns:
            A streaming response with the chat answer.
        """
        services = get_services(request)
        if not payload.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        chunks = services.indexer.search(payload.message, payload.top_k)

        def stream() -> Iterator[str]:
            yield from services.chat.stream_answer(question=payload.message, context_chunks=chunks, history=payload.history)

        return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")

    return app


app = create_app()
