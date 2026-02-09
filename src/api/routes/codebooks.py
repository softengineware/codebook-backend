"""Codebook API routes."""
from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, UploadFile, status

from src.api.dependencies.auth import AuthDep
from src.core.errors import CodebookNotFoundError, ResourceNotFoundError
from src.models.codebook import CodebookType, CodebookUploadResponse
from src.models.job import JobCreate
from src.repositories.codebook_versions import CodebookVersionRepository
from src.repositories.codebooks import CodebookRepository
from src.repositories.jobs import JobRepository
from src.services.codebook_processor import CodebookProcessor
from src.services.csv_parser import parse_upload_file
from src.services.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Codebooks"])


def get_codebook_repository(db=Depends(get_supabase_client)) -> CodebookRepository:
    return CodebookRepository(db)


def get_version_repository(db=Depends(get_supabase_client)) -> CodebookVersionRepository:
    return CodebookVersionRepository(db)


def get_job_repository(db=Depends(get_supabase_client)) -> JobRepository:
    return JobRepository(db)


@router.post(
    "/clients/{client_id}/codebooks/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=dict,
)
async def upload_codebook(
    client_id: UUID,
    background_tasks: BackgroundTasks,
    auth: AuthDep,
    file: UploadFile = File(...),
    name: str = Form(...),
    type: CodebookType = Form(...),
    description: str = Form(None),
    db=Depends(get_supabase_client),
) -> dict:
    """Upload a CSV/Excel file to create a new codebook with AI analysis.

    Returns a job ID for polling the async processing status.
    """
    auth.require_client_access(str(client_id))

    # Parse the uploaded file
    items = await parse_upload_file(file)

    # Create a job record
    job_repo = JobRepository(db)
    job = job_repo.create_job(
        JobCreate(
            client_id=client_id,
            job_type="initial_analysis",
        )
    )

    # Start background processing
    processor = CodebookProcessor(db)
    background_tasks.add_task(
        processor.process_upload,
        job_id=job.id,
        client_id=client_id,
        codebook_name=name,
        codebook_type=type,
        description=description,
        items=items,
    )

    logger.info(f"Upload job {job.id} created for client {client_id}: {len(items)} items")

    return {
        "data": CodebookUploadResponse(
            job_id=job.id,
            status="pending",
            message=f"Processing {len(items)} items. Poll GET /v1/jobs/{job.id} for status.",
        ).model_dump()
    }


@router.get("/clients/{client_id}/codebooks")
def list_codebooks(
    client_id: UUID,
    auth: AuthDep,
    repo: Annotated[CodebookRepository, Depends(get_codebook_repository)],
    type: CodebookType | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    """List all codebooks for a client."""
    auth.require_client_access(str(client_id))
    codebooks = repo.list_codebooks(client_id=client_id, codebook_type=type, limit=limit)
    return {"data": codebooks}


@router.get("/codebooks/{codebook_id}")
def get_codebook(
    codebook_id: UUID,
    auth: AuthDep,
    codebook_repo: Annotated[CodebookRepository, Depends(get_codebook_repository)],
    version_repo: Annotated[CodebookVersionRepository, Depends(get_version_repository)],
) -> dict:
    """Get codebook details including active version info."""
    codebook = codebook_repo.get_codebook(codebook_id)
    if not codebook:
        raise CodebookNotFoundError(str(codebook_id))

    auth.require_client_access(str(codebook.client_id))

    # Find active version
    versions = version_repo.list_versions(codebook_id, limit=1)
    active_version = None
    for v in versions:
        if v.is_active:
            active_version = v
            break

    # If no active found in first result, get all and find active
    if active_version is None and versions:
        all_versions = version_repo.list_versions(codebook_id, limit=100)
        for v in all_versions:
            if v.is_active:
                active_version = v
                break

    result = codebook.model_dump()
    result["active_version"] = active_version.model_dump() if active_version else None

    return {"data": result}
