from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status

from backend.app.core.constants import STATUS_QUEUED, STATUS_RUNNING
from backend.app.schemas.investigation import InvestigationCreate, InvestigationRead
from backend.app.services.investigation_service import InvestigationService
from backend.app.workflows.investigation_workflow import InvestigationWorkflowService

router = APIRouter(prefix="/investigations", tags=["investigations"])

investigation_service = InvestigationService()
workflow_service = InvestigationWorkflowService(investigation_service)


@router.get("", response_model=list[InvestigationRead])
async def list_investigations(status_filter: str | None = Query(default=None, alias="status")) -> list[InvestigationRead]:
    filters = {"status": status_filter} if status_filter else {}
    return [InvestigationRead(**item) for item in await investigation_service.list_investigations(**filters)]


@router.post("", response_model=InvestigationRead, status_code=status.HTTP_201_CREATED)
async def create_investigation(payload: InvestigationCreate, background: BackgroundTasks) -> InvestigationRead:
    """Create the investigation and start the pipeline in the background. Poll GET /{id} for progress."""
    created = await workflow_service.create(
        title=payload.title, input_text=payload.input_text or payload.title,
        source_type=payload.source_type, description=payload.description,
    )
    background.add_task(workflow_service.run_workflow, created["id"])
    return InvestigationRead(**created)


@router.get("/{investigation_id}", response_model=InvestigationRead)
async def get_investigation(investigation_id: str) -> InvestigationRead:
    inv = await investigation_service.get_investigation(investigation_id)
    if not inv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Investigation {investigation_id} not found")
    return InvestigationRead(**inv)


@router.post("/{investigation_id}/run", response_model=InvestigationRead, status_code=status.HTTP_202_ACCEPTED)
async def run_investigation(investigation_id: str, background: BackgroundTasks) -> InvestigationRead:
    """(Re)run the pipeline for a stored investigation; previous results are replaced."""
    inv = await investigation_service.get_investigation(investigation_id)
    if not inv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Investigation {investigation_id} not found")
    if inv.get("status") == STATUS_RUNNING:
        raise HTTPException(status.HTTP_409_CONFLICT, "Investigation is already running")
    updated = await investigation_service.update_investigation_status(investigation_id, STATUS_QUEUED)
    background.add_task(workflow_service.run_workflow, investigation_id)
    return InvestigationRead(**(updated or inv))
