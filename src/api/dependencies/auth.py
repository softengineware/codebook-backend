"""Authentication and authorization dependencies."""
import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client as SupabaseClient

from src.core.errors import (
    ClientAccessDeniedError,
    ExpiredAPIKeyError,
    InsufficientPermissionsError,
    InvalidAPIKeyError,
    MissingAPIKeyError,
)
from src.services.database import get_supabase_client

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class AuthContext:
    """Authentication context containing user/client information."""

    def __init__(
        self,
        api_key_id: str,
        client_id: str,
        role: str,
        user_id: str | None = None,
        key_prefix: str | None = None,
    ):
        self.api_key_id = api_key_id
        self.client_id = client_id
        self.role = role
        self.user_id = user_id
        self.key_prefix = key_prefix

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin"

    def can_access_client(self, client_id: str) -> bool:
        """Check if user can access the specified client."""
        return self.is_admin() or self.client_id == client_id

    def require_admin(self) -> None:
        """Raise exception if user is not admin."""
        if not self.is_admin():
            raise InsufficientPermissionsError(
                required_role="admin",
                user_role=self.role,
                action="admin_action",
            )

    def require_client_access(self, client_id: str) -> None:
        """Raise exception if user cannot access the client."""
        if not self.can_access_client(client_id):
            raise ClientAccessDeniedError(
                requested_client_id=client_id,
                user_client_id=self.client_id,
            )


async def verify_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
    db: Annotated[SupabaseClient, Depends(get_supabase_client)],
) -> AuthContext:
    """
    Verify API key from Authorization header and return auth context.

    Raises:
        MissingAPIKeyError: If no API key provided
        InvalidAPIKeyError: If API key is invalid or revoked
        ExpiredAPIKeyError: If API key has expired
    """
    if not credentials or not credentials.credentials:
        raise MissingAPIKeyError()

    api_key = credentials.credentials

    # Extract key prefix (first 8 characters)
    if len(api_key) < 32:
        raise InvalidAPIKeyError()

    key_prefix = api_key[:12]  # e.g., "ck_live_1234"

    try:
        # Lookup API key in database by prefix
        result = db.table("api_keys").select(
            "id, key_hash, client_id, user_id, scopes, expires_at, "
            "revoked_at, clients(id, name)"
        ).eq(
            "key_prefix", key_prefix
        ).is_(
            "revoked_at", "null"
        ).execute()

        if not result.data or len(result.data) == 0:
            logger.warning(f"Invalid API key attempt with prefix: {key_prefix}")
            raise InvalidAPIKeyError()

        api_key_record = result.data[0]

        # TODO: Verify full key hash using bcrypt/passlib
        # For now, we'll skip hash verification (implement in production!)
        # import bcrypt
        # if not bcrypt.checkpw(api_key.encode(), api_key_record['key_hash'].encode()):
        #     raise InvalidAPIKeyError()

        # Check expiration
        if api_key_record.get("expires_at"):
            from datetime import datetime
            expires_at = datetime.fromisoformat(api_key_record["expires_at"].replace("Z", "+00:00"))
            if datetime.utcnow() > expires_at:
                raise ExpiredAPIKeyError(
                    expired_at=api_key_record["expires_at"],
                    key_prefix=key_prefix,
                )

        # Update last_used_at timestamp (async, don't wait)
        db.table("api_keys").update(
            {"last_used_at": "now()"}
        ).eq("id", api_key_record["id"]).execute()

        # Determine role from scopes (simplified for MVP)
        scopes = api_key_record.get("scopes", ["read", "write"])
        role = "admin" if "admin" in scopes else "client_user"

        logger.info(
            f"API key authenticated",
            extra={
                "key_prefix": key_prefix,
                "client_id": api_key_record["client_id"],
                "role": role,
            },
        )

        return AuthContext(
            api_key_id=api_key_record["id"],
            client_id=api_key_record["client_id"],
            role=role,
            user_id=api_key_record.get("user_id"),
            key_prefix=key_prefix,
        )

    except (InvalidAPIKeyError, ExpiredAPIKeyError):
        raise
    except Exception as e:
        logger.error(f"Error verifying API key: {str(e)}", exc_info=True)
        raise InvalidAPIKeyError()


# Dependency for admin-only endpoints
async def require_admin(
    auth: Annotated[AuthContext, Depends(verify_api_key)]
) -> AuthContext:
    """Require admin role for endpoint access."""
    auth.require_admin()
    return auth


# Type aliases for dependency injection
AuthDep = Annotated[AuthContext, Depends(verify_api_key)]
AdminDep = Annotated[AuthContext, Depends(require_admin)]
