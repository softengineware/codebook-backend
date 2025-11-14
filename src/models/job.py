"""Job data models."""
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


JobType = Literal["initial_analysis", "refactor", "bulk_upload", "semantic_search", "export"]
JobStatus = Literal["pending", "running", "completed", "failed", "cancelled"]


class JobBase(BaseModel):
    """Base job model."""

    job_type: JobType
    result: dict[str, Any] | None = None


class JobCreate(JobBase):
    """Model for creating a new job."""

    client_id: UUID
    codebook_id: UUID | None = None


class Job(JobBase):
    """Complete job model."""

    id: UUID
    client_id: UUID
    codebook_id: UUID | None
    status: JobStatus
    progress: int = Field(0, ge=0, le=100)
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    created_by: str | None = None

    model_config = {"from_attributes": True}


class JobStatusResponse(BaseModel):
    """Response for job status query."""

    data: Job
