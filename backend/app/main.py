from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="ClaimLens 2.0 backend for evidence intelligence workflows",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health endpoint used by checks and deployment systems."""
    return {"status": "ok", "service": settings.app_name}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} backend is running"}
