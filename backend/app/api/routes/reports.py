from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.investigation import InvestigationCreate, InvestigationRead
from backend.app.services.investigation_service import InvestigationService
from backend.app.workflows.investigation_workflow import InvestigationWorkflowService

router = APIRouter(prefix="/investigations", tags=["investigations"])

investigation_service = InvestigationService()
workflow_service = InvestigationWorkflowService(investigation_service)


@router.get("", response_model=list[InvestigationRead])
async def list_investigations(status: str | None = None) -> list[InvestigationRead]:
    """List investigations, optionally filtered by status."""
    filters: dict[str, str] = {}
    if status:
        filters["status"] = status
    investigations = await investigation_service.list_investigations(**filters)
    return [InvestigationRead(**item) for item in investigations]


@router.post("", response_model=InvestigationRead, status_code=status.HTTP_201_CREATED)
async def create_investigation(payload: InvestigationCreate) -> InvestigationRead:
    """Create a new investigation and trigger the workflow."""
    investigation = await workflow_service.start_investigation(
        title=payload.title,
        input_text=payload.description or payload.title,
        source_type=payload.source_type or "text",
    )
    return InvestigationRead(**investigation)


@router.get("/{investigation_id}", response_model=InvestigationRead)
async def get_investigation(investigation_id: str) -> InvestigationRead:
    """Get a single investigation record."""
    investigation = await investigation_service.get_investigation(investigation_id)
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation {investigation_id} not found",
        )
    return InvestigationRead(**investigation)


@router.post("/{investigation_id}/run", response_model=InvestigationRead)
async def run_investigation(investigation_id: str) -> InvestigationRead:
    """Trigger workflow execution for a stored investigation."""
    investigation = await investigation_service.get_investigation(investigation_id)
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation {investigation_id} not found",
        )

    updated = await investigation_service.update_investigation_status(
        investigation_id,
        "running",
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation {investigation_id} not found",
        )
    return InvestigationRead(**updated)
