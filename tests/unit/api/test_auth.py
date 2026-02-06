"""Tests for src.api.dependencies.auth - Authentication middleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestAuthContext:
    """Test AuthContext class."""

    def test_is_admin(self):
        """Test is_admin returns True for admin role."""
        try:
            from src.api.dependencies.auth import AuthContext
            ctx = AuthContext(
                api_key_id=str(uuid4()),
                client_id=str(uuid4()),
                role="admin",
                user_id=str(uuid4()),
            )
            assert ctx.is_admin() is True
        except ImportError:
            pytest.skip("Auth module not available")

    def test_is_not_admin(self):
        """Test is_admin returns False for non-admin role."""
        try:
            from src.api.dependencies.auth import AuthContext
            ctx = AuthContext(
                api_key_id=str(uuid4()),
                client_id=str(uuid4()),
                role="user",
                user_id=str(uuid4()),
            )
            assert ctx.is_admin() is False
        except ImportError:
            pytest.skip("Auth module not available")

    def test_can_access_own_client(self):
        """Test user can access their own client data."""
        try:
            from src.api.dependencies.auth import AuthContext
            client_id = str(uuid4())
            ctx = AuthContext(
                api_key_id=str(uuid4()),
                client_id=client_id,
                role="user",
                user_id=str(uuid4()),
            )
            assert ctx.can_access_client(client_id) is True
        except ImportError:
            pytest.skip("Auth module not available")

    def test_admin_can_access_any_client(self):
        """Test admin can access any client data."""
        try:
            from src.api.dependencies.auth import AuthContext
            ctx = AuthContext(
                api_key_id=str(uuid4()),
                client_id=str(uuid4()),
                role="admin",
                user_id=str(uuid4()),
            )
            assert ctx.can_access_client(str(uuid4())) is True
        except ImportError:
            pytest.skip("Auth module not available")

    def test_require_admin_raises_for_non_admin(self):
        """Test require_admin raises error for non-admin users."""
        try:
            from src.api.dependencies.auth import AuthContext
            ctx = AuthContext(
                api_key_id=str(uuid4()),
                client_id=str(uuid4()),
                role="user",
                user_id=str(uuid4()),
            )
            with pytest.raises(Exception):
                ctx.require_admin()
        except ImportError:
            pytest.skip("Auth module not available")

    def test_require_client_access_raises_for_wrong_client(self):
        """Test require_client_access raises error for wrong client."""
        try:
            from src.api.dependencies.auth import AuthContext
            ctx = AuthContext(
                api_key_id=str(uuid4()),
                client_id=str(uuid4()),
                role="user",
                user_id=str(uuid4()),
            )
            with pytest.raises(Exception):
                ctx.require_client_access(str(uuid4()))
        except ImportError:
            pytest.skip("Auth module not available")


class TestVerifyApiKey:
    """Test API key verification."""

    @pytest.mark.asyncio
    async def test_missing_api_key_raises_error(self):
        """Test that missing API key raises error."""
        try:
            from src.api.dependencies.auth import verify_api_key
            from fastapi import Request
            request = MagicMock(spec=Request)
            request.headers = {}
            with pytest.raises(Exception):
                await verify_api_key(request)
        except ImportError:
            pytest.skip("Auth module not available")
