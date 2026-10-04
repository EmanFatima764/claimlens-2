from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InvestigationCreate(BaseModel):
    """Payload from the 'Create investigation' form.

    Tolerant of field naming: the claim text may arrive as input_text / claim / claim_text / description,
    and the input type as source_type / input_type. Falls back to the title if no text is given.
    """

    title: str = Field(min_length=1, max_length=300)
    input_text: Optional[str] = None
    description: Optional[str] = None
    source_type: str = "text"

    @model_validator(mode="before")
    @classmethod
    def _normalize(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        data = dict(data)
        pick = lambda *keys: next((str(data[k]).strip() for k in keys if data.get(k) and str(data[k]).strip()), None)  # noqa: E731
        data["input_text"] = pick("input_text", "claim", "claim_text", "description", "title")
        data["source_type"] = (pick("source_type", "input_type") or "text").lower()
        return data


class InvestigationRead(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    input_text: Optional[str] = None
    source_type: Optional[str] = None
    status: Optional[str] = None
    workflow_status: Optional[str] = None
    current_stage: Optional[str] = None
    stage_group: Optional[str] = None
    final_verdict: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
