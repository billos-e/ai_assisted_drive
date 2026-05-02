from __future__ import annotations

from services import AppServices


def sync_repository_index(services: AppServices) -> None:
    indexed_file_ids = services.indexer.get_indexed_file_ids()
    drive_files = []
    drive_file_ids: set[str] = set()

    for node in services.drive.walk_repository(services.settings.google_drive_root_folder_id):
        if node.type != "file":
            continue
        drive_files.append(node)
        drive_file_ids.add(node.id)

    # Remove orphaned vectors for files deleted directly from Drive (outside this API).
    orphaned_file_ids = indexed_file_ids - drive_file_ids
    if orphaned_file_ids:
        services.indexer.delete_files_chunks(orphaned_file_ids)

    for node in drive_files:
        if node.id in indexed_file_ids:
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
