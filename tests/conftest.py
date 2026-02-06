"""Shared test fixtures for codebook-backend."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    client = MagicMock()
    # Mock table operations
    table = MagicMock()
    table.select = MagicMock(return_value=table)
    table.insert = MagicMock(return_value=table)
    table.update = MagicMock(return_value=table)
    table.delete = MagicMock(return_value=table)
    table.eq = MagicMock(return_value=table)
    table.is_ = MagicMock(return_value=table)
    table.execute = MagicMock(
        return_value=MagicMock(data=[{"id": str(uuid4()), "name": "test"}])
    )
    client.table = MagicMock(return_value=table)
    return client


@pytest.fixture
def sample_client_id():
    """Sample client UUID."""
    return str(uuid4())


@pytest.fixture
def sample_admin_auth_context():
    """Sample admin authentication context."""
    return {
        "api_key_id": str(uuid4()),
        "client_id": str(uuid4()),
        "role": "admin",
        "user_id": str(uuid4()),
    }


@pytest.fixture
def sample_user_auth_context(sample_client_id):
    """Sample user authentication context."""
    return {
        "api_key_id": str(uuid4()),
        "client_id": sample_client_id,
        "role": "user",
        "user_id": str(uuid4()),
    }


@pytest.fixture
def sample_client_data():
    """Sample client creation data."""
    return {
        "name": "Test Client",
        "email": "test@example.com",
        "organization": "Test Org",
    }


@pytest.fixture
def sample_codebook_data(sample_client_id):
    """Sample codebook creation data."""
    return {
        "name": "Test Codebook",
        "description": "A test codebook for unit testing",
        "client_id": sample_client_id,
    }


@pytest.fixture
def sample_job_data(sample_client_id):
    """Sample job creation data."""
    return {
        "client_id": sample_client_id,
        "job_type": "analysis",
        "status": "pending",
        "progress": 0,
    }


@pytest.fixture
def sample_codebook_item_data():
    """Sample codebook item data."""
    return {
        "code": "01 00 00",
        "description": "General Requirements",
        "division": "01",
        "section": "00",
        "subsection": "00",
    }
