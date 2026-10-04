from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.report import ChatRequest, ChatResponse, ReportRead
from backend.app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])
report_service = ReportService()


@router.get("/{investigation_id}", response_model=ReportRead)
async def get_report(investigation_id: str) -> ReportRead:
    """Full report payload. While the pipeline is still running, `verdict` is null - keep polling."""
    report = await report_service.build_report(investigation_id)
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Investigation {investigation_id} not found")
    return report


@router.post("/{investigation_id}/chat", response_model=ChatResponse)
async def chat_about_report(investigation_id: str, payload: ChatRequest) -> ChatResponse:
    """'Ask ClaimLens' - answers only from this investigation's evidence set."""
    answer = await report_service.chat(investigation_id, payload.question)
    if answer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Investigation {investigation_id} not found")
    return ChatResponse(answer=answer)


@router.get("/{investigation_id}/export")
async def export_report(investigation_id: str, format: str = "pdf") -> dict[str, str]:
    return {"investigation_id": investigation_id, "format": format, "status": "not_implemented"}
