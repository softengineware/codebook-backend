"""Repository functions for clients."""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from supabase import Client as SupabaseClient

from src.models.client import Client, ClientCreate


class ClientRepository:
    """Data access layer for clients table."""

    def __init__(self, db: SupabaseClient) -> None:
        self._db = db

    def create_client(self, data: ClientCreate) -> Client:
        """Create a new client."""
        payload: dict[str, Any] = data.model_dump()

        result = (
            self._db.table("clients")
            .insert(payload)
            .select(
                "id, name, slug, contact_email, metadata, created_at, updated_at, deleted_at"
            )
            .single()
            .execute()
        )

        return Client.model_validate(result.data)

    def get_client(self, client_id: UUID) -> Optional[Client]:
        """Get a client by id, excluding soft-deleted ones."""
        result = (
            self._db.table("clients")
            .select(
                "id, name, slug, contact_email, metadata, created_at, updated_at, deleted_at"
            )
            .eq("id", str(client_id))
            .is_("deleted_at", "null")
            .maybe_single()
            .execute()
        )

        if not result.data:
            return None

        return Client.model_validate(result.data)

    def list_clients(self, limit: int = 50, cursor: Optional[str] = None) -> dict[str, Any]:
        """List clients with simple offset-based pagination for MVP.

        For MVP we ignore real cursor-based pagination and just return up to `limit` items.
        """
        query = (
            self._db.table("clients")
            .select(
                "id, name, slug, contact_email, metadata, created_at, updated_at, deleted_at"
            )
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
            .limit(limit)
        )

        # Cursor handling can be added later; for now just execute the query.
        result = query.execute()

        clients = [Client.model_validate(row) for row in result.data or []]

        pagination = {
            "next_cursor": None,
            "prev_cursor": None,
            "has_more": False,
            "total_count": len(clients),
        }

        return {"data": clients, "pagination": pagination}
