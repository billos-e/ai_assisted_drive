from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from ..chat.groq_client import GroqClient


def extract_audio_video_bytes(content: bytes, filename: str, mime_type: str, groq_client: GroqClient) -> str:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        raise RuntimeError("ffmpeg is required for audio/video extraction")

    suffix = Path(filename).suffix or ".bin"
    source_handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    source_path = Path(source_handle.name)
    source_handle.write(content)
    source_handle.close()

    audio_path: Path | None = None
    try:
        input_path = source_path
        if mime_type.startswith("video/") or suffix.lower() in {".mp4", ".mov", ".mkv", ".avi", ".webm"}:
            audio_handle = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            audio_path = Path(audio_handle.name)
            audio_handle.close()
            subprocess.run(
                [
                    ffmpeg_path,
                    "-y",
                    "-i",
                    str(source_path),
                    "-vn",
                    "-acodec",
                    "pcm_s16le",
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    str(audio_path),
                ],
                check=True,
                capture_output=True,
            )
            input_path = audio_path
        return groq_client.transcribe_audio_file(str(input_path))
    finally:
        if source_path.exists():
            source_path.unlink(missing_ok=True)
        if audio_path is not None and audio_path.exists():
            audio_path.unlink(missing_ok=True)
