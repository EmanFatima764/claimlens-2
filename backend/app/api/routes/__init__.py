"""API route registry for ClaimLens backend."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
