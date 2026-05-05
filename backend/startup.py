from __future__ import annotations

from services import AppServices


def build_drive_structure_text(services: AppServices) -> str:
    """Generate a human-readable text representation of the Drive structure.
    
    Uses full paths to make hierarchies explicit for the model.
    Format:
    # Google Drive Repository Structure
    
    /RootFolder/ (folder)
    /RootFolder/subfolder/ (folder)
    /RootFolder/subfolder/file.txt (file)
    /RootFile.txt (file)
    """
    lines = ["# Google Drive Repository Structure\n"]
    
    def walk_with_paths(folder_id: str | None = None, current_path: str = "/") -> None:
        """Walk the repository and emit full paths for each item."""
        items = services.drive.list_folder(folder_id)
        for item in items:
            # Build the full path
            if current_path == "/":
                item_path = f"/{item.name}"
            else:
                item_path = f"{current_path}{item.name}"
            
            # Add trailing slash for folders
            if item.type == "folder":
                item_path += "/"
                lines.append(f"{item_path} (folder)")
                # Recursively walk subfolder
                walk_with_paths(item.id, item_path)
            else:
                lines.append(f"{item_path} (file)")
    
    try:
        walk_with_paths(services.settings.google_drive_root_folder_id, "/")
    except Exception as e:
        lines.append(f"\n[Error building structure: {str(e)}]")
    
    return "\n".join(lines)


def index_drive_structure(services: AppServices) -> None:
    """Index the Drive directory structure as a searchable document.
    
    This makes the model aware of the file/folder hierarchy for queries like:
    - "Where is the X file?"
    - "What files are in the Y folder?"
    """
    try:
        structure_text = build_drive_structure_text(services)
        if not structure_text.strip():
            return
        
        # Index as a special virtual file
        services.indexer.index_text(
            file_id="__drive_structure__",
            file_name="Drive Repository Structure",
            folder_path="/",
            mime_type="text/plain",
            text=structure_text,
        )
        print("[STARTUP] Drive structure indexed successfully")
    except Exception as e:
        print(f"[STARTUP WARNING] Failed to index drive structure: {str(e)}")


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
    
    # After indexing all files, refresh and index the Drive structure for directory queries
    # First remove old structure if it exists
    services.indexer.delete_file_chunks("__drive_structure__")
    index_drive_structure(services)
