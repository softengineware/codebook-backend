"""Embedding metadata models."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ItemEmbeddingBase(BaseModel):
    client_id: UUID
    item_id: UUID
    pinecone_id: str
    embedding_model: str | None = None


class ItemEmbedding(ItemEmbeddingBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CSIEmbeddingBase(BaseModel):
    client_id: UUID | None = None
    csi_code: str
    csi_title: str
    csi_description: str | None = None
    pinecone_id: str
    embedding_model: str | None = None


class CSIEmbedding(CSIEmbeddingBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


