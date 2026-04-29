from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd


def extract_spreadsheet_bytes(content: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(BytesIO(content))
        return frame.to_csv(index=False)

    sheets = pd.read_excel(BytesIO(content), sheet_name=None)
    rendered_sheets: list[str] = []
    for sheet_name, frame in sheets.items():
        rendered_sheets.append(f"[Sheet: {sheet_name}]\n{frame.to_csv(index=False)}")
    return "\n\n".join(rendered_sheets)
