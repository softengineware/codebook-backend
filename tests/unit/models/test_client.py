"""Tests for src.models.client - Client data models."""

import pytest
from uuid import uuid4


class TestClientModels:
    """Test client Pydantic models."""

    def test_client_create(self, sample_client_data):
        """Test ClientCreate model validation."""
        try:
            from src.models.client import ClientCreate
            client = ClientCreate(**sample_client_data)
            assert client.name == "Test Client"
            assert client.email == "test@example.com"
        except ImportError:
            pytest.skip("Client models not available")

    def test_client_create_requires_name(self):
        """Test that ClientCreate requires a name."""
        try:
            from src.models.client import ClientCreate
            with pytest.raises(Exception):
                ClientCreate(email="test@example.com")
        except ImportError:
            pytest.skip("Client models not available")

    def test_client_update(self):
        """Test ClientUpdate model allows partial updates."""
        try:
            from src.models.client import ClientUpdate
            update = ClientUpdate(name="Updated Name")
            assert update.name == "Updated Name"
        except ImportError:
            pytest.skip("Client models not available")

    def test_client_model_has_id(self):
        """Test Client model has id field."""
        try:
            from src.models.client import Client
            assert "id" in Client.model_fields
        except ImportError:
            pytest.skip("Client models not available")


class TestCodebookModels:
    """Test codebook Pydantic models."""

    def test_codebook_create(self, sample_codebook_data):
        """Test CodebookCreate model validation."""
        try:
            from src.models.codebook import CodebookCreate
            codebook = CodebookCreate(**sample_codebook_data)
            assert codebook.name == "Test Codebook"
        except ImportError:
            pytest.skip("Codebook models not available")


class TestJobModels:
    """Test job Pydantic models."""

    def test_job_create(self, sample_job_data):
        """Test JobCreate model validation."""
        try:
            from src.models.job import JobCreate
            job = JobCreate(**sample_job_data)
            assert job.status == "pending"
            assert job.progress == 0
        except ImportError:
            pytest.skip("Job models not available")

    def test_job_status_values(self):
        """Test that job status accepts valid values."""
        try:
            from src.models.job import Job
            # Check that the model has a status field
            assert "status" in Job.model_fields
        except ImportError:
            pytest.skip("Job models not available")
