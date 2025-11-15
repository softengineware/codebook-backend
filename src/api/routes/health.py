"""Health check routes."""
from fastapi import APIRouter, status

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Construction Codebook AI Backend",
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK, tags=["Health"])
async def readiness_check() -> dict:
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "service": "Construction Codebook AI Backend",
    }
