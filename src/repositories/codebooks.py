"""Repository layer for codebooks."""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.codebook import Codebook, CodebookCreate, CodebookType


class CodebookRepository:
    """Data access layer for the codebooks table."""

    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def create_codebook(self, client_id: UUID, data: CodebookCreate) -> Codebook:
        payload: dict[str, Any] = {
            "client_id": str(client_id),
            **data.model_dump(),
        }

        result = (
            self._db.table("codebooks")
            .insert(payload)
            .select("*")
            .single()
            .execute()
        )
        return Codebook.model_validate(result.data)

    def get_codebook(self, codebook_id: UUID) -> Optional[Codebook]:
        result = (
            self._db.table("codebooks")
            .select("*")
            .eq("id", str(codebook_id))
            .is_("deleted_at", "null")
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return Codebook.model_validate(result.data)

    def list_codebooks(
        self,
        client_id: UUID,
        codebook_type: CodebookType | None = None,
        limit: int = 50,
    ) -> list[Codebook]:
        query = (
            self._db.table("codebooks")
            .select("*")
            .eq("client_id", str(client_id))
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
            .limit(limit)
        )
        if codebook_type:
            query = query.eq("type", codebook_type)

        result = query.execute()
        return [Codebook.model_validate(row) for row in result.data or []]

    def update_codebook(self, codebook_id: UUID, data: dict[str, Any]) -> Optional[Codebook]:
        if not data:
            return self.get_codebook(codebook_id)

        result = (
            self._db.table("codebooks")
            .update(data)
            .eq("id", str(codebook_id))
            .select("*")
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return Codebook.model_validate(result.data)

    def soft_delete(self, codebook_id: UUID) -> None:
        self._db.table("codebooks").update({"deleted_at": "now()"}).eq("id", str(codebook_id)).execute()
