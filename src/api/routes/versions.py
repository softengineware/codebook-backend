"""Codebook version routes."""
from fastapi import APIRouter, status
from uuid import UUID

router = APIRouter(prefix="/codebooks/{codebook_id}/versions")


@router.get("", status_code=status.HTTP_200_OK)
async def list_versions(codebook_id: UUID) -> dict:
    """List all versions for a codebook (placeholder)."""
    return {
        "message": "List versions endpoint - to be implemented",
        "codebook_id": str(codebook_id),
        "data": [],
        "status": "not_implemented",
    }


@router.get("/{version_id}", status_code=status.HTTP_200_OK)
async def get_version(codebook_id: UUID, version_id: UUID) -> dict:
    """Get a specific version (placeholder)."""
    return {
        "message": "Get version endpoint - to be implemented",
        "codebook_id": str(codebook_id),
        "version_id": str(version_id),
        "status": "not_implemented",
    }


@router.post("/{version_id}/activate", status_code=status.HTTP_200_OK)
async def activate_version(codebook_id: UUID, version_id: UUID) -> dict:
    """Activate a specific version (placeholder)."""
    return {
        "message": "Activate version endpoint - to be implemented",
        "codebook_id": str(codebook_id),
        "version_id": str(version_id),
        "status": "not_implemented",
    }
