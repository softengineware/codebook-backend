"""Job status API routes."""
from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies.auth import AuthDep
from src.core.errors import JobNotFoundError
from src.repositories.jobs import JobRepository
from src.services.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Jobs"])


def get_job_repository(db=Depends(get_supabase_client)) -> JobRepository:
    return JobRepository(db)


@router.get("/jobs/{job_id}")
def get_job_status(
    job_id: UUID,
    auth: AuthDep,
    repo: Annotated[JobRepository, Depends(get_job_repository)],
) -> dict:
    """Get the current status of a processing job."""
    job = repo.get_job(job_id)
    if not job:
        raise JobNotFoundError(str(job_id))

    auth.require_client_access(str(job.client_id))

    return {"data": job.model_dump()}
