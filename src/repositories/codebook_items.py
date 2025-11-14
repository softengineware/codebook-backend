"""Repository layer for codebook items."""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.codebook_item import CodebookItem


class CodebookItemRepository:
    """Access to codebook_items table."""

    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def bulk_insert_items(self, items: list[dict[str, Any]]) -> list[CodebookItem]:
        if not items:
            return []

        result = (
            self._db.table("codebook_items")
            .insert(items)
            .select("*")
            .execute()
        )
        return [CodebookItem.model_validate(row) for row in result.data or []]

    def list_items(
        self,
        version_id: UUID,
        limit: int = 100,
        csi_division: str | None = None,
        application: str | None = None,
    ) -> list[CodebookItem]:
        query = (
            self._db.table("codebook_items")
            .select("*")
            .eq("version_id", str(version_id))
            .order("created_at", desc=True)
            .limit(limit)
        )
        if csi_division:
            query = query.eq("csi_division", csi_division)
        if application:
            query = query.eq("application", application)

        result = query.execute()
        return [CodebookItem.model_validate(row) for row in result.data or []]

    def get_item(self, item_id: UUID) -> Optional[CodebookItem]:
        result = (
            self._db.table("codebook_items")
            .select("*")
            .eq("id", str(item_id))
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return CodebookItem.model_validate(result.data)
