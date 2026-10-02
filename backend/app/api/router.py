from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.investigation import InvestigationRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{investigation_id}", response_model=InvestigationRead)
async def get_report(investigation_id: str) -> InvestigationRead:
    """Return a report payload for a completed investigation."""
    # Placeholder implementation until report generation is connected to the workflow.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Report generation is not implemented yet",
    )


@router.get("/{investigation_id}/export")
async def export_report(investigation_id: str, format: str = "pdf") -> dict[str, str]:
    """Export a report in a future supported format."""
    return {
        "investigation_id": investigation_id,
        "format": format,
        "status": "not_implemented",
    }
