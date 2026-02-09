"""CSV and Excel file parsing service."""
from __future__ import annotations

import io
import logging
from typing import Any

import pandas as pd
from fastapi import UploadFile

from src.core.config import settings
from src.core.errors import FileTooLargeError

logger = logging.getLogger(__name__)

# Heuristic column name mappings
LABEL_COLUMNS = [
    "item", "name", "label", "description", "material", "title",
    "item_name", "item_description", "material_name", "product",
    "item name", "item description", "material name",
]
DESCRIPTION_COLUMNS = [
    "description", "desc", "details", "notes", "specification",
    "item_description", "item description", "spec",
]
DIAMETER_COLUMNS = [
    "diameter", "size", "dia", "nominal_size", "nominal size", "pipe_size", "pipe size",
]
APPLICATION_COLUMNS = [
    "application", "app", "use", "category", "system", "type",
    "application_type", "application type",
]

# Valid application values mapping
APPLICATION_MAP = {
    "sanitary": "sanitary_sewer",
    "sanitary_sewer": "sanitary_sewer",
    "sanitary sewer": "sanitary_sewer",
    "storm": "storm_sewer",
    "storm_sewer": "storm_sewer",
    "storm sewer": "storm_sewer",
    "water": "water",
    "potable": "water",
    "other": "other",
}


async def parse_upload_file(file: UploadFile) -> list[dict[str, Any]]:
    """Parse an uploaded CSV or Excel file into a list of raw row dicts."""
    content = await file.read()
    file_size = len(content)
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if file_size > max_size:
        raise FileTooLargeError(file_size=file_size, max_size=max_size)

    filename = (file.filename or "").lower()

    if filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
    else:
        # Default to CSV
        df = pd.read_csv(io.BytesIO(content))

    if len(df) > settings.MAX_ROWS_PER_UPLOAD:
        from src.core.errors import APIError
        raise APIError(
            code="TOO_MANY_ROWS",
            message=f"File contains {len(df)} rows, maximum allowed is {settings.MAX_ROWS_PER_UPLOAD}",
            status_code=400,
        )

    if len(df) == 0:
        from src.core.errors import APIError
        raise APIError(
            code="EMPTY_FILE",
            message="Uploaded file contains no data rows",
            status_code=400,
        )

    # Clean column names
    df.columns = [str(c).strip().lower() for c in df.columns]

    column_mapping = detect_columns(df)
    items = normalize_items(df, column_mapping)

    logger.info(f"Parsed {len(items)} items from upload", extra={
        "filename": file.filename,
        "columns_detected": column_mapping,
    })

    return items


def detect_columns(df: pd.DataFrame) -> dict[str, str | None]:
    """Detect which DataFrame columns map to our schema fields."""
    columns = list(df.columns)
    mapping: dict[str, str | None] = {
        "label": None,
        "description": None,
        "diameter": None,
        "application": None,
    }

    for col in columns:
        col_lower = col.lower().strip()
        if mapping["label"] is None and col_lower in LABEL_COLUMNS:
            mapping["label"] = col
        elif mapping["description"] is None and col_lower in DESCRIPTION_COLUMNS:
            mapping["description"] = col
        elif mapping["diameter"] is None and col_lower in DIAMETER_COLUMNS:
            mapping["diameter"] = col
        elif mapping["application"] is None and col_lower in APPLICATION_COLUMNS:
            mapping["application"] = col

    # Fallback: use first text column as label
    if mapping["label"] is None and len(columns) > 0:
        mapping["label"] = columns[0]

    # If label and description are the same, clear description
    if mapping["label"] == mapping["description"]:
        mapping["description"] = None

    return mapping


def normalize_items(
    df: pd.DataFrame, column_mapping: dict[str, str | None]
) -> list[dict[str, Any]]:
    """Transform DataFrame rows into normalized item dicts."""
    items = []
    label_col = column_mapping.get("label")
    desc_col = column_mapping.get("description")
    diameter_col = column_mapping.get("diameter")
    app_col = column_mapping.get("application")

    for _, row in df.iterrows():
        # Build original label
        original_label = ""
        if label_col and pd.notna(row.get(label_col)):
            original_label = str(row[label_col]).strip()

        if not original_label:
            continue  # Skip empty rows

        # Build description
        description = None
        if desc_col and pd.notna(row.get(desc_col)):
            description = str(row[desc_col]).strip()

        # Build metadata from all columns
        metadata: dict[str, Any] = {}
        for col in df.columns:
            if col in (label_col, desc_col) or pd.isna(row.get(col)):
                continue
            val = row[col]
            if isinstance(val, float) and val == int(val):
                val = int(val)
            metadata[col] = val

        # Extract application if detected
        application = None
        if app_col and pd.notna(row.get(app_col)):
            raw_app = str(row[app_col]).strip().lower()
            application = APPLICATION_MAP.get(raw_app)

        # Extract diameter if detected
        if diameter_col and pd.notna(row.get(diameter_col)):
            metadata["diameter"] = row[diameter_col]

        items.append({
            "original_label": original_label,
            "description": description,
            "metadata": metadata if metadata else None,
            "application": application,
        })

    return items
