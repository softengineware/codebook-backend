"""Job monitoring routes."""
from fastapi import APIRouter, status
from uuid import UUID

router = APIRouter(prefix="/jobs")


@router.get("/{job_id}", status_code=status.HTTP_200_OK)
async def get_job_status(job_id: UUID) -> dict:
    """Get job status (placeholder)."""
    return {
        "message": "Get job status endpoint - to be implemented",
        "job_id": str(job_id),
        "status": "not_implemented",
    }


@router.get("", status_code=status.HTTP_200_OK)
async def list_jobs() -> dict:
    """List all jobs (placeholder)."""
    return {
        "message": "List jobs endpoint - to be implemented",
        "data": [],
        "status": "not_implemented",
    }


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(job_id: UUID) -> None:
    """Cancel a running job (placeholder)."""
    pass
