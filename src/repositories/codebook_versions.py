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
        payload: dict[str, Any] = data.model_dump()
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
