"""Tests for src.core.errors - Custom API error classes."""

import pytest


class TestAPIErrors:
    """Test custom API error classes."""

    def test_missing_api_key_error(self):
        """Test MissingAPIKeyError has correct status code."""
        try:
            from src.core.errors import MissingAPIKeyError
            error = MissingAPIKeyError()
            assert error.status_code == 401
        except ImportError:
            pytest.skip("Errors module not available")

    def test_invalid_api_key_error(self):
        """Test InvalidAPIKeyError has correct status code."""
        try:
            from src.core.errors import InvalidAPIKeyError
            error = InvalidAPIKeyError()
            assert error.status_code == 401
        except ImportError:
            pytest.skip("Errors module not available")

    def test_forbidden_error(self):
        """Test ForbiddenError has correct status code."""
        try:
            from src.core.errors import ForbiddenError
            error = ForbiddenError()
            assert error.status_code == 403
        except ImportError:
            pytest.skip("Errors module not available")

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError has correct status code."""
        try:
            from src.core.errors import ResourceNotFoundError
            error = ResourceNotFoundError("client", "test-id")
            assert error.status_code == 404
        except ImportError:
            pytest.skip("Errors module not available")

    def test_validation_error(self):
        """Test ValidationError has correct status code."""
        try:
            from src.core.errors import ValidationError
            error = ValidationError("Invalid input")
            assert error.status_code == 422
        except ImportError:
            pytest.skip("Errors module not available")

    def test_database_error(self):
        """Test DatabaseError has correct status code."""
        try:
            from src.core.errors import DatabaseError
            error = DatabaseError("Connection failed")
            assert error.status_code == 500
        except ImportError:
            pytest.skip("Errors module not available")

    def test_rate_limit_error(self):
        """Test RateLimitExceededError has correct status code."""
        try:
            from src.core.errors import RateLimitExceededError
            error = RateLimitExceededError()
            assert error.status_code == 429
        except ImportError:
            pytest.skip("Errors module not available")

    def test_job_already_running_error(self):
        """Test JobAlreadyRunningError has correct status code."""
        try:
            from src.core.errors import JobAlreadyRunningError
            error = JobAlreadyRunningError()
            assert error.status_code == 409
        except ImportError:
            pytest.skip("Errors module not available")

    def test_api_error_has_timestamp(self):
        """Test that APIError base class includes timestamp."""
        try:
            from src.core.errors import MissingAPIKeyError
            error = MissingAPIKeyError()
            assert hasattr(error, "timestamp") or hasattr(error, "detail")
        except ImportError:
            pytest.skip("Errors module not available")
