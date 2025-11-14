"""Custom error classes and error handling utilities."""
from datetime import datetime
from typing import Any


class APIError(Exception):
    """Base class for all API errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        super().__init__(self.message)


# Authentication Errors (1xxx)
class MissingAPIKeyError(APIError):
    """API key is missing from Authorization header."""

    def __init__(self):
        super().__init__(
            code="MISSING_API_KEY",
            message="API key is missing from Authorization header",
            status_code=401,
            details={"expected_format": "Authorization: Bearer <API_KEY>"},
        )


class InvalidAPIKeyError(APIError):
    """API key is invalid or has been revoked."""

    def __init__(self):
        super().__init__(
            code="INVALID_API_KEY",
            message="API key is invalid or has been revoked",
            status_code=401,
        )


class ExpiredAPIKeyError(APIError):
    """API key has expired."""

    def __init__(self, expired_at: str, key_prefix: str):
        super().__init__(
            code="EXPIRED_API_KEY",
            message="API key has expired",
            status_code=401,
            details={"expired_at": expired_at, "key_prefix": key_prefix},
        )


# Authorization Errors (2xxx)
class ForbiddenError(APIError):
    """User does not have permission to access this resource."""

    def __init__(self, message: str = "You do not have permission to access this resource"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403,
        )


class ClientAccessDeniedError(APIError):
    """User does not have access to this client."""

    def __init__(self, requested_client_id: str, user_client_id: str):
        super().__init__(
            code="CLIENT_ACCESS_DENIED",
            message="You do not have access to this client",
            status_code=403,
            details={
                "requested_client_id": requested_client_id,
                "your_client_id": user_client_id,
            },
        )


class InsufficientPermissionsError(APIError):
    """User's role does not have permission for this action."""

    def __init__(self, required_role: str, user_role: str, action: str):
        super().__init__(
            code="INSUFFICIENT_PERMISSIONS",
            message="Your role does not have permission for this action",
            status_code=403,
            details={
                "required_role": required_role,
                "your_role": user_role,
                "action": action,
            },
        )


class ResourceLockedError(APIError):
    """Resource is currently locked by another user."""

    def __init__(self, locked_by: str, locked_at: str, resource_id: str):
        super().__init__(
            code="RESOURCE_LOCKED",
            message="This resource is currently locked by another user",
            status_code=409,
            details={
                "locked_by": locked_by,
                "locked_at": locked_at,
                "resource_id": resource_id,
            },
        )


# Validation Errors (3xxx)
class ValidationError(APIError):
    """Request validation failed."""

    def __init__(self, errors: list[dict[str, Any]]):
        super().__init__(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=422,
            details={"errors": errors},
        )


class InvalidCodebookTypeError(APIError):
    """Codebook type is invalid."""

    def __init__(self, provided_type: str):
        super().__init__(
            code="INVALID_CODEBOOK_TYPE",
            message="Codebook type must be material, activity, or bid_item",
            status_code=400,
            details={
                "provided_type": provided_type,
                "allowed_types": ["material", "activity", "bid_item"],
            },
        )


class FileTooLargeError(APIError):
    """File size exceeds maximum allowed."""

    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            code="FILE_TOO_LARGE",
            message="File size exceeds maximum allowed",
            status_code=413,
            details={
                "file_size_bytes": file_size,
                "max_size_bytes": max_size,
                "max_size_mb": max_size // (1024 * 1024),
            },
        )


# Resource Errors (4xxx)
class ResourceNotFoundError(APIError):
    """The requested resource was not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message="The requested resource was not found",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ClientNotFoundError(APIError):
    """Client not found."""

    def __init__(self, client_id: str):
        super().__init__(
            code="CLIENT_NOT_FOUND",
            message="Client not found",
            status_code=404,
            details={"client_id": client_id},
        )


class CodebookNotFoundError(APIError):
    """Codebook not found."""

    def __init__(self, codebook_id: str):
        super().__init__(
            code="CODEBOOK_NOT_FOUND",
            message="Codebook not found",
            status_code=404,
            details={"codebook_id": codebook_id},
        )


class JobNotFoundError(APIError):
    """Job not found."""

    def __init__(self, job_id: str):
        super().__init__(
            code="JOB_NOT_FOUND",
            message="Job not found",
            status_code=404,
            details={"job_id": job_id},
        )


# External Service Errors (5xxx)
class DatabaseError(APIError):
    """Database operation failed."""

    def __init__(self, operation: str, table: str):
        super().__init__(
            code="DATABASE_ERROR",
            message="Database operation failed",
            status_code=500,
            details={"operation": operation, "table": table},
        )


class LLMAPIError(APIError):
    """LLM service returned an error."""

    def __init__(self, provider: str, error_code: str, error_message: str):
        super().__init__(
            code="LLM_API_ERROR",
            message="LLM service returned an error",
            status_code=502,
            details={
                "llm_provider": provider,
                "llm_error_code": error_code,
                "llm_error_message": error_message,
            },
        )


class PineconeError(APIError):
    """Vector database operation failed."""

    def __init__(self, operation: str, error_code: str | None = None):
        super().__init__(
            code="PINECONE_ERROR",
            message="Vector database operation failed",
            status_code=502,
            details={"operation": operation, "error_code": error_code},
        )


# Rate Limit Errors (6xxx)
class RateLimitExceededError(APIError):
    """Rate limit exceeded."""

    def __init__(self, limit: int, period: str, retry_after: int):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded",
            status_code=429,
            details={
                "limit": limit,
                "period": period,
                "retry_after_seconds": retry_after,
            },
        )


# Job Errors (7xxx)
class JobAlreadyRunningError(APIError):
    """A job is already running for this codebook."""

    def __init__(self, codebook_id: str, running_job_id: str, job_type: str):
        super().__init__(
            code="JOB_ALREADY_RUNNING",
            message="A job is already running for this codebook",
            status_code=409,
            details={
                "codebook_id": codebook_id,
                "running_job_id": running_job_id,
                "job_type": job_type,
            },
        )
