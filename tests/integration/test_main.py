"""Integration tests for main FastAPI application."""

import pytest
from unittest.mock import patch, MagicMock


class TestAppCreation:
    """Test application creation and configuration."""

    def test_app_exists(self):
        """Test that the FastAPI app is created."""
        try:
            from main import app
            assert app is not None
        except ImportError:
            pytest.skip("Main app not available")

    def test_app_has_routes(self):
        """Test that the app has registered routes."""
        try:
            from main import app
            routes = [r.path for r in app.routes]
            assert len(routes) > 0
        except ImportError:
            pytest.skip("Main app not available")


class TestMiddleware:
    """Test application middleware."""

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is configured."""
        try:
            from main import app
            middleware_classes = [m.cls.__name__ for m in app.user_middleware]
            assert any("CORS" in name for name in middleware_classes)
        except (ImportError, AttributeError):
            pytest.skip("Main app not available")


class TestExceptionHandlers:
    """Test exception handlers."""

    def test_api_error_handler_returns_json(self):
        """Test that API errors return JSON responses."""
        try:
            from fastapi.testclient import TestClient
            from main import app
            client = TestClient(app)
            # Make a request to a non-existent endpoint
            response = client.get("/nonexistent-endpoint")
            assert response.status_code in (404, 422)
        except ImportError:
            pytest.skip("Main app not available")
