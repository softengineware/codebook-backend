"""Repository layer for jobs."""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.job import Job, JobCreate, JobStatus


class JobRepository:
    """Data access for jobs table."""

    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def create_job(self, data: JobCreate, status: JobStatus = "pending") -> Job:
        payload: dict[str, Any] = {
            "client_id": str(data.client_id),
            "job_type": data.job_type,
            "status": status,
        }
        if data.codebook_id is not None:
            payload["codebook_id"] = str(data.codebook_id)

        result = (
            self._db.table("jobs")
            .insert(payload)
            .select("*")
            .single()
            .execute()
        )
        return Job.model_validate(result.data)

    def get_job(self, job_id: UUID) -> Optional[Job]:
        result = (
            self._db.table("jobs")
            .select("*")
            .eq("id", str(job_id))
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return Job.model_validate(result.data)

    def update_job(
        self,
        job_id: UUID,
        *,
        status: JobStatus | None = None,
        progress: int | None = None,
        result_payload: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> Optional[Job]:
        update_data: dict[str, Any] = {}
        if status is not None:
            update_data["status"] = status
        if progress is not None:
            update_data["progress"] = progress
        if result_payload is not None:
            update_data["result"] = result_payload
        if error is not None:
            update_data["error"] = error

        if not update_data:
            return self.get_job(job_id)

        result = (
            self._db.table("jobs")
            .update(update_data)
            .eq("id", str(job_id))
            .select("*")
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return Job.model_validate(result.data)
