"""Repository layer for LLM usage records."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.llm_usage import LLMUsage, LLMUsageCreate, OperationType


class LLMUsageRepository:
    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def record_usage(self, data: LLMUsageCreate) -> LLMUsage:
        payload = data.model_dump()
        result = (
            self._db.table("llm_usage")
            .insert(payload)
            .select("*")
            .single()
            .execute()
        )
        return LLMUsage.model_validate(result.data)

    def list_usage(
        self,
        client_id: UUID,
        operation_type: OperationType | None = None,
        limit: int = 100,
    ) -> list[LLMUsage]:
        query = (
            self._db.table("llm_usage")
            .select("*")
            .eq("client_id", str(client_id))
            .order("created_at", desc=True)
            .limit(limit)
        )
        if operation_type:
            query = query.eq("operation_type", operation_type)

        result = query.execute()
        return [LLMUsage.model_validate(row) for row in result.data or []]

    def get_usage(self, usage_id: UUID) -> Optional[LLMUsage]:
        result = (
            self._db.table("llm_usage")
            .select("*")
            .eq("id", str(usage_id))
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return LLMUsage.model_validate(result.data)
