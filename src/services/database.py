"""Database connection and client management."""
import logging
from functools import lru_cache

from supabase import Client, create_client

from src.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get Supabase client instance (cached singleton).

    Returns:
        Supabase client for database operations
    """
    logger.info("Creating Supabase client connection")

    client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_KEY,
    )

    return client


# Global client instance (for use outside FastAPI dependency injection)
supabase_client = get_supabase_client()
