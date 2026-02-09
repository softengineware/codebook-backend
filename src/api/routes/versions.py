"""Codebook version API routes."""
from __future__ import annotations

import csv
import io
import json
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from src.api.dependencies.auth import AuthDep
from src.core.errors import ResourceNotFoundError
from src.repositories.codebook_items import CodebookItemRepository
from src.repositories.codebook_versions import CodebookVersionRepository
from src.services.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Versions"])


def get_version_repository(db=Depends(get_supabase_client)) -> CodebookVersionRepository:
    return CodebookVersionRepository(db)


def get_item_repository(db=Depends(get_supabase_client)) -> CodebookItemRepository:
    return CodebookItemRepository(db)


@router.get("/codebook-versions/{version_id}/items")
def list_version_items(
    version_id: UUID,
    auth: AuthDep,
    item_repo: Annotated[CodebookItemRepository, Depends(get_item_repository)],
    version_repo: Annotated[CodebookVersionRepository, Depends(get_version_repository)],
    csi_division: str | None = Query(None),
    application: str | None = Query(None),
    limit: int = Query(100, ge=1, le=10000),
) -> dict:
    """List items in a codebook version with optional filters."""
    # Verify version exists
    version = version_repo.get_version(version_id)
    if not version:
        raise ResourceNotFoundError("codebook_version", str(version_id))

    items = item_repo.list_items(
        version_id=version_id,
        limit=limit,
        csi_division=csi_division,
        application=application,
    )

    return {
        "data": {
            "version_id": str(version_id),
            "version_number": version.version_number,
            "item_count": len(items),
            "items": [item.model_dump() for item in items],
        }
    }


@router.get("/codebook-versions/{version_id}/export")
def export_version_csv(
    version_id: UUID,
    auth: AuthDep,
    item_repo: Annotated[CodebookItemRepository, Depends(get_item_repository)],
    version_repo: Annotated[CodebookVersionRepository, Depends(get_version_repository)],
) -> StreamingResponse:
    """Export all items in a codebook version as a CSV file."""
    # Verify version exists
    version = version_repo.get_version(version_id)
    if not version:
        raise ResourceNotFoundError("codebook_version", str(version_id))

    # Fetch all items (high limit for export)
    items = item_repo.list_items(version_id=version_id, limit=10000)

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        "Code",
        "Original Label",
        "Description",
        "CSI Division",
        "CSI Section",
        "Application",
        "Metadata",
    ])

    # Data rows
    for item in items:
        metadata_str = ""
        if item.metadata:
            metadata_str = json.dumps(item.metadata)

        writer.writerow([
            item.code,
            item.original_label,
            item.description or "",
            item.csi_division or "",
            item.csi_section or "",
            item.application or "",
            metadata_str,
        ])

    output.seek(0)

    filename = f"codebook-v{version.version_number}-export.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
