"""Repository layer for codebook versions."""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.version import CodebookVersion, CodebookVersionCreate


class CodebookVersionRepository:
    """Access to codebook_versions table."""

    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def create_version(self, data: CodebookVersionCreate) -> CodebookVersion:
        payload: dict[str, Any] = {
            "codebook_id": str(data.codebook_id),
            "version_number": data.version_number,
        }
        # Add optional fields if present
        if data.label is not None:
            payload["label"] = data.label
        if data.notes is not None:
            payload["notes"] = data.notes
        if data.rules_snapshot is not None:
            payload["rules_snapshot"] = data.rules_snapshot
        if data.analysis_summary is not None:
            payload["analysis_summary"] = data.analysis_summary
        if data.analysis_details is not None:
            payload["analysis_details"] = data.analysis_details
        if data.prompt_version is not None:
            payload["prompt_version"] = data.prompt_version
        payload["is_active"] = data.is_active
        if data.created_by is not None:
            payload["created_by"] = data.created_by

        result = (
            self._db.table("codebook_versions")
            .insert(payload)
            .select("*")
            .single()
            .execute()
        )
        return CodebookVersion.model_validate(result.data)

    def get_version(self, version_id: UUID) -> Optional[CodebookVersion]:
        result = (
            self._db.table("codebook_versions")
            .select("*")
            .eq("id", str(version_id))
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return CodebookVersion.model_validate(result.data)

    def list_versions(self, codebook_id: UUID, limit: int = 50) -> list[CodebookVersion]:
        result = (
            self._db.table("codebook_versions")
            .select("*")
            .eq("codebook_id", str(codebook_id))
            .order("version_number", desc=True)
            .limit(limit)
            .execute()
        )
        return [CodebookVersion.model_validate(row) for row in result.data or []]

    def set_active_version(self, codebook_id: UUID, version_id: UUID) -> None:
        # deactivate others
        self._db.table("codebook_versions").update({"is_active": False}).eq("codebook_id", str(codebook_id)).execute()
        # activate target
        self._db.table("codebook_versions").update({"is_active": True}).eq("id", str(version_id)).execute()
