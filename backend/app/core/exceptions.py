from __future__ import annotations


class ClaimLensError(Exception):
    """Base error used across ClaimLens backend services and integrations."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or "claimlens_error"
