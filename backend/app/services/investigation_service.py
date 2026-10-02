from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.investigations import router as investigations_router
from backend.app.api.routes.reports import router as reports_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(investigations_router)
api_router.include_router(reports_router)
