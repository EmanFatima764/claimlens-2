from __future__ import annotations

from typing import Any


class PDFClient:
    """Placeholder client for PDF parsing and document extraction."""

    async def extract_text(self, file_path: str) -> dict[str, Any]:
        return {
            "file_path": file_path,
            "pages": [],
            "status": "not_implemented",
        }
