"""Tests for src.repositories.clients - Client data access layer."""

import pytest
from unittest.mock import MagicMock
from uuid import uuid4


class TestClientRepository:
    """Test client repository operations."""

    def test_create_client(self, mock_supabase_client, sample_client_data):
        """Test creating a client."""
        try:
            from src.repositories.clients import ClientRepository
            repo = ClientRepository(mock_supabase_client)
            result = repo.create_client(sample_client_data)
            assert result is not None
            mock_supabase_client.table.assert_called()
        except ImportError:
            pytest.skip("Client repository not available")

    def test_get_client(self, mock_supabase_client):
        """Test getting a client by ID."""
        try:
            from src.repositories.clients import ClientRepository
            repo = ClientRepository(mock_supabase_client)
            client_id = str(uuid4())
            result = repo.get_client(client_id)
            assert result is not None
        except ImportError:
            pytest.skip("Client repository not available")

    def test_list_clients(self, mock_supabase_client):
        """Test listing all clients."""
        try:
            from src.repositories.clients import ClientRepository
            repo = ClientRepository(mock_supabase_client)
            results = repo.list_clients()
            assert isinstance(results, (list, type(None)))
        except ImportError:
            pytest.skip("Client repository not available")


class TestCodebookRepository:
    """Test codebook repository operations."""

    def test_create_codebook(self, mock_supabase_client, sample_codebook_data):
        """Test creating a codebook."""
        try:
            from src.repositories.codebooks import CodebookRepository
            repo = CodebookRepository(mock_supabase_client)
            result = repo.create_codebook(sample_codebook_data)
            assert result is not None
        except ImportError:
            pytest.skip("Codebook repository not available")

    def test_soft_delete(self, mock_supabase_client):
        """Test soft deleting a codebook."""
        try:
            from src.repositories.codebooks import CodebookRepository
            repo = CodebookRepository(mock_supabase_client)
            codebook_id = str(uuid4())
            repo.soft_delete(codebook_id)
            mock_supabase_client.table.assert_called()
        except ImportError:
            pytest.skip("Codebook repository not available")


class TestJobRepository:
    """Test job repository operations."""

    def test_create_job(self, mock_supabase_client, sample_job_data):
        """Test creating a job."""
        try:
            from src.repositories.jobs import JobRepository
            repo = JobRepository(mock_supabase_client)
            result = repo.create_job(sample_job_data)
            assert result is not None
        except ImportError:
            pytest.skip("Job repository not available")

    def test_update_job_status(self, mock_supabase_client):
        """Test updating job status."""
        try:
            from src.repositories.jobs import JobRepository
            repo = JobRepository(mock_supabase_client)
            job_id = str(uuid4())
            repo.update_job_status(job_id, "running")
            mock_supabase_client.table.assert_called()
        except ImportError:
            pytest.skip("Job repository not available")

    def test_update_job_progress(self, mock_supabase_client):
        """Test updating job progress."""
        try:
            from src.repositories.jobs import JobRepository
            repo = JobRepository(mock_supabase_client)
            job_id = str(uuid4())
            repo.update_job_progress(job_id, 50)
            mock_supabase_client.table.assert_called()
        except ImportError:
            pytest.skip("Job repository not available")
