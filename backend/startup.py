from __future__ import annotations

from .services import AppServices


def sync_repository_index(services: AppServices) -> None:
    indexed_file_ids = services.indexer.get_indexed_file_ids()
    for node in services.drive.walk_repository(services.settings.google_drive_root_folder_id):
        if node.type != "file" or node.id in indexed_file_ids:
            continue

        content = services.drive.download_bytes(node.id)
        extracted_text = services.extractor.extract_bytes(content=content, filename=node.name, mime_type=node.mime_type)
        if not extracted_text.strip():
            indexed_file_ids.add(node.id)
            continue

        services.indexer.index_text(
            file_id=node.id,
            file_name=node.name,
            folder_path=node.folder_path,
            mime_type=node.mime_type,
            text=extracted_text,
        )
        indexed_file_ids.add(node.id)
