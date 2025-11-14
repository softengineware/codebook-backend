"""Repository layer for embedding metadata tables."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.embedding import CSIEmbedding, CSIEmbeddingBase, ItemEmbedding, ItemEmbeddingBase


class ItemEmbeddingRepository:
    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def upsert_embedding(self, data: ItemEmbeddingBase) -> ItemEmbedding:
        payload = data.model_dump()
        result = (
            self._db.table("item_embeddings")
            .upsert(payload, on_conflict="item_id")
            .select("*")
            .single()
            .execute()
        )
        return ItemEmbedding.model_validate(result.data)

    def get_by_item(self, item_id: UUID) -> Optional[ItemEmbedding]:
        result = (
            self._db.table("item_embeddings")
            .select("*")
            .eq("item_id", str(item_id))
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return ItemEmbedding.model_validate(result.data)


class CSIEmbeddingRepository:
    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def upsert_embedding(self, data: CSIEmbeddingBase) -> CSIEmbedding:
        payload = data.model_dump()
        result = (
            self._db.table("csi_embeddings")
            .upsert(payload, on_conflict="csi_code")
            .select("*")
            .single()
            .execute()
        )
        return CSIEmbedding.model_validate(result.data)

    def get_by_code(self, csi_code: str) -> Optional[CSIEmbedding]:
        result = (
            self._db.table("csi_embeddings")
            .select("*")
            .eq("csi_code", csi_code)
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return CSIEmbedding.model_validate(result.data)
