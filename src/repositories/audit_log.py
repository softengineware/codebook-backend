"""Repository layer for audit log entries."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.audit import AuditEntry, AuditEntryCreate, AuditAction


class AuditLogRepository:
    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def create_entry(self, data: AuditEntryCreate) -> AuditEntry:
        payload = data.model_dump()
        result = (
            self._db.table("audit_log")
            .insert(payload)
            .select("*")
            .single()
            .execute()
        )
        return AuditEntry.model_validate(result.data)

    def list_entries(
        self,
        client_id: UUID,
        codebook_id: UUID | None = None,
        action_type: AuditAction | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        query = (
            self._db.table("audit_log")
            .select("*")
            .eq("client_id", str(client_id))
            .order("created_at", desc=True)
            .limit(limit)
        )
        if codebook_id:
            query = query.eq("codebook_id", str(codebook_id))
        if action_type:
            query = query.eq("action_type", action_type)

        result = query.execute()
        return [AuditEntry.model_validate(row) for row in result.data or []]

    def get_entry(self, entry_id: UUID) -> Optional[AuditEntry]:
        result = (
            self._db.table("audit_log")
            .select("*")
            .eq("id", str(entry_id))
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return AuditEntry.model_validate(result.data)
