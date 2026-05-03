from __future__ import annotations

import asyncio
import json
import mimetypes
from functools import lru_cache
from collections.abc import Iterator

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config import Settings, get_settings
from schemas import ChatStreamRequest, DriveFolderCreateRequest, DriveItem, DriveUploadResponse, DriveDeleteResponse, DriveOpenResponse, SettingsResponse, SettingsUpdate
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
        try:
            services = get_services(request)
            items = services.drive.list_folder(folder_id)
            return [DriveItem(id=item.id, name=item.name, type=item.type, mime_type=item.mime_type) for item in items]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list folder: {str(e)}")

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
        try:
            services = get_services(request)
            created = services.drive.create_folder(name=payload.name, folder_id=payload.folder_id)
            return DriveUploadResponse(id=created.id, name=created.name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create folder: {str(e)}")

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
        try:
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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    @app.delete("/drive/{file_id}", response_model=DriveDeleteResponse)
    def drive_delete(file_id: str, request: Request) -> DriveDeleteResponse:
        """
        Delete a file or folder from Google Drive.

        Args:
            file_id: The ID of the file or folder to delete.
            request: The request object.

        Returns:
            A response confirming the deletion.
        """
        try:
            services = get_services(request)
            if not file_id:
                raise HTTPException(status_code=400, detail="file_id cannot be empty")
            services.drive.delete_file(file_id)
            deleted_chunks = services.indexer.delete_file_chunks(file_id)
            return DriveDeleteResponse(
                message=f"File {file_id} successfully deleted and {deleted_chunks} indexed chunks removed",
                deleted_id=file_id,
            )
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    @app.get("/drive/{file_id}/open", response_model=DriveOpenResponse)
    def drive_open(file_id: str, request: Request) -> DriveOpenResponse:
        """
        Get the Google Drive URL to open a file.

        Args:
            file_id: The ID of the file to open.
            request: The request object.

        Returns:
            A response with the Google Drive URL for the file.
        """
        try:
            services = get_services(request)
            if not file_id:
                raise HTTPException(status_code=400, detail="file_id cannot be empty")
            url = services.drive.get_file_url(file_id)
            return DriveOpenResponse(url=url)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get file URL: {str(e)}")

    @app.post("/chat/stream")
    def chat_stream(payload: ChatStreamRequest, request: Request) -> StreamingResponse:
        """
        Handle the chat streaming.

        Args:
            payload: The request payload.
            request: The request object.

        Returns:
            A streaming response with the chat answer and sources.
        """
        try:
            services = get_services(request)
            if not payload.message.strip():
                raise HTTPException(status_code=400, detail="Message cannot be empty")

            chunks = services.indexer.search(payload.message, payload.top_k)

            def stream() -> Iterator[str]:
                # Stream the chat response tokens
                yield from services.chat.stream_answer(question=payload.message, context_chunks=chunks, history=payload.history)
                
                # After the main response, send sources
                # Deduplicate sources by source_path and chunk_index, filter by distance and limit count
                seen_sources = set()
                sources = []
                max_distance = services.settings.sources_max_distance
                max_sources = services.settings.sources_max_count
                
                for chunk in chunks:
                    if len(sources) >= max_sources:
                        break
                    
                    try:
                        distance = chunk.get("distance")
                        if isinstance(distance, str):
                            distance = float(distance)
                        
                        # Filter by max distance threshold
                        if distance > max_distance:
                            continue
                        
                        source_key = (chunk.get("source_path", ""), chunk.get("chunk_index", ""))
                        if source_key not in seen_sources:
                            seen_sources.add(source_key)
                            sources.append({
                                "source_path": chunk.get("source_path", ""),
                                "file_name": chunk.get("file_name", ""),
                                "file_id": chunk.get("file_id", ""),
                                "chunk_index": int(chunk.get("chunk_index", 0)),
                                "distance": distance,
                            })
                    except (ValueError, TypeError):
                        pass
                
                # Send sources separator and data
                import json
                yield f"\n[SOURCES_SEPARATOR]\n{json.dumps(sources)}"

            return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")

    @app.get("/settings", response_model=SettingsResponse)
    def get_settings_route(request: Request) -> SettingsResponse:
        """
        Get the application settings.

        Args:
            request: The request object.

        Returns:
            The application settings.
        """
        try:
            services = get_services(request)
            return SettingsResponse(
                google_account=services.drive.get_user_email(),
                root_folder_id=services.settings.google_drive_root_folder_id,
                indexed_files_count=len(services.indexer.get_indexed_file_ids()),
                selected_model=services.settings.groq_chat_model,
                number_of_sources=services.settings.retrieval_top_k,
                response_language=services.settings.response_language,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

    @app.patch("/settings", response_model=SettingsResponse)
    def patch_settings_route(payload: SettingsUpdate, request: Request) -> SettingsResponse:
        """
        Update the application settings.

        Args:
            payload: The settings to update.
            request: The request object.

        Returns:
            The updated application settings.
        """
        try:
            services = get_services(request)
            settings = services.settings

            if payload.root_folder_id is not None:
                settings.google_drive_root_folder_id = payload.root_folder_id
            if payload.selected_model is not None:
                settings.groq_chat_model = payload.selected_model
            if payload.number_of_sources is not None:
                settings.retrieval_top_k = payload.number_of_sources
            if payload.response_language is not None:
                settings.response_language = payload.response_language

            # Rebuild services to apply changes
            request.app.state.services = build_services(settings)
            
            # Re-fetch services to get the new ones
            new_services = get_services(request)

            return SettingsResponse(
                google_account=new_services.drive.get_user_email(),
                root_folder_id=new_services.settings.google_drive_root_folder_id,
                indexed_files_count=len(new_services.indexer.get_indexed_file_ids()),
                selected_model=new_services.settings.groq_chat_model,
                number_of_sources=new_services.settings.retrieval_top_k,
                response_language=new_services.settings.response_language,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

    return app


app = create_app()
