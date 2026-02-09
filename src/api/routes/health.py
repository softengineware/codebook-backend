"""Health check endpoint."""
from fastapi import APIRouter

from src.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
    }
