# Error Code Catalog

This document defines all error codes, their meanings, and recommended resolutions for the Construction Codebook AI Backend.

---

## Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "additional context"
    },
    "request_id": "uuid",
    "timestamp": "2025-01-15T10:30:00Z",
    "documentation_url": "https://docs.codebook.example.com/errors/ERROR_CODE"
  }
}
```

---

## Error Categories

1. **Authentication Errors (1xxx)**
2. **Authorization Errors (2xxx)**
3. **Validation Errors (3xxx)**
4. **Resource Errors (4xxx)**
5. **External Service Errors (5xxx)**
6. **Rate Limit Errors (6xxx)**
7. **Job Errors (7xxx)**
8. **System Errors (9xxx)**

---

## 1. Authentication Errors (1xxx)

### 1001 - MISSING_API_KEY
**HTTP Status:** 401 Unauthorized
**Message:** "API key is missing from Authorization header"
**Details:**
```json
{
  "expected_format": "Authorization: Bearer <API_KEY>"
}
```
**Resolution:** Include `Authorization: Bearer <API_KEY>` header in request.

---

### 1002 - INVALID_API_KEY
**HTTP Status:** 401 Unauthorized
**Message:** "API key is invalid or has been revoked"
**Resolution:** Verify API key is correct. Generate a new key if needed.

---

### 1003 - EXPIRED_API_KEY
**HTTP Status:** 401 Unauthorized
**Message:** "API key has expired"
**Details:**
```json
{
  "expired_at": "2025-01-01T00:00:00Z",
  "key_prefix": "ck_live_1234"
}
```
**Resolution:** Generate a new API key via the dashboard or API.

---

### 1004 - INVALID_JWT_TOKEN
**HTTP Status:** 401 Unauthorized
**Message:** "JWT token is invalid or malformed"
**Resolution:** Ensure JWT token is properly signed and not expired. Re-authenticate if needed.

---

### 1005 - EXPIRED_JWT_TOKEN
**HTTP Status:** 401 Unauthorized
**Message:** "JWT token has expired"
**Details:**
```json
{
  "expired_at": "2025-01-15T10:15:00Z"
}
```
**Resolution:** Refresh the JWT token using the refresh token endpoint.

---

## 2. Authorization Errors (2xxx)

### 2001 - FORBIDDEN
**HTTP Status:** 403 Forbidden
**Message:** "You do not have permission to access this resource"
**Resolution:** Verify your account has the required role or permissions.

---

### 2002 - CLIENT_ACCESS_DENIED
**HTTP Status:** 403 Forbidden
**Message:** "You do not have access to this client"
**Details:**
```json
{
  "requested_client_id": "uuid",
  "your_client_id": "uuid"
}
```
**Resolution:** Ensure you're accessing resources for your own client. Contact admin if you need access to another client.

---

### 2003 - INSUFFICIENT_PERMISSIONS
**HTTP Status:** 403 Forbidden
**Message:** "Your role does not have permission for this action"
**Details:**
```json
{
  "required_role": "client_user",
  "your_role": "readonly",
  "action": "codebook:create"
}
```
**Resolution:** Contact your administrator to upgrade your permissions.

---

### 2004 - RESOURCE_LOCKED
**HTTP Status:** 409 Conflict
**Message:** "This resource is currently locked by another user"
**Details:**
```json
{
  "locked_by": "user@example.com",
  "locked_at": "2025-01-15T10:00:00Z",
  "codebook_id": "uuid"
}
```
**Resolution:** Wait for the other user to complete their operation or contact them to release the lock.

---

## 3. Validation Errors (3xxx)

### 3001 - VALIDATION_ERROR
**HTTP Status:** 422 Unprocessable Entity
**Message:** "Request validation failed"
**Details:**
```json
{
  "errors": [
    {
      "field": "name",
      "message": "Name must be between 1 and 255 characters",
      "value": ""
    },
    {
      "field": "type",
      "message": "Type must be one of: material, activity, bid_item",
      "value": "invalid_type"
    }
  ]
}
```
**Resolution:** Fix the validation errors listed in the `errors` array.

---

### 3002 - INVALID_UUID
**HTTP Status:** 400 Bad Request
**Message:** "Invalid UUID format"
**Details:**
```json
{
  "field": "codebook_id",
  "value": "not-a-uuid"
}
```
**Resolution:** Ensure all IDs are valid UUIDs.

---

### 3003 - INVALID_CODEBOOK_TYPE
**HTTP Status:** 400 Bad Request
**Message:** "Codebook type must be material, activity, or bid_item"
**Details:**
```json
{
  "provided_type": "invalid",
  "allowed_types": ["material", "activity", "bid_item"]
}
```
**Resolution:** Use one of the allowed codebook types.

---

### 3004 - INVALID_FILE_TYPE
**HTTP Status:** 400 Bad Request
**Message:** "File type not supported"
**Details:**
```json
{
  "provided_mime_type": "application/pdf",
  "allowed_types": ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
}
```
**Resolution:** Upload a CSV or Excel file.

---

### 3005 - FILE_TOO_LARGE
**HTTP Status:** 413 Payload Too Large
**Message:** "File size exceeds maximum allowed"
**Details:**
```json
{
  "file_size_bytes": 15728640,
  "max_size_bytes": 10485760,
  "max_size_mb": 10
}
```
**Resolution:** Reduce file size or split into multiple uploads.

---

### 3006 - TOO_MANY_ROWS
**HTTP Status:** 422 Unprocessable Entity
**Message:** "File contains too many rows"
**Details:**
```json
{
  "row_count": 15000,
  "max_rows": 10000
}
```
**Resolution:** Split file into multiple uploads with max 10,000 rows each.

---

### 3007 - INVALID_CSV_FORMAT
**HTTP Status:** 422 Unprocessable Entity
**Message:** "CSV file format is invalid"
**Details:**
```json
{
  "error": "Missing required column: 'label'",
  "required_columns": ["label", "description"],
  "found_columns": ["name", "description"]
}
```
**Resolution:** Ensure CSV has required columns with correct names.

---

### 3008 - INVALID_JSON
**HTTP Status:** 400 Bad Request
**Message:** "Request body contains invalid JSON"
**Details:**
```json
{
  "parse_error": "Unexpected token } in JSON at position 42"
}
```
**Resolution:** Validate JSON syntax before sending request.

---

### 3009 - DUPLICATE_CODE
**HTTP Status:** 409 Conflict
**Message:** "Code already exists in this version"
**Details:**
```json
{
  "code": "2-DIP-08-B",
  "existing_item_id": "uuid",
  "version_id": "uuid"
}
```
**Resolution:** Use a unique code or update the existing item.

---

### 3010 - DUPLICATE_CLIENT_NAME
**HTTP Status:** 409 Conflict
**Message:** "A client with this name already exists"
**Details:**
```json
{
  "name": "ACME Construction",
  "existing_client_id": "uuid"
}
```
**Resolution:** Choose a different client name.

---

## 4. Resource Errors (4xxx)

### 4001 - RESOURCE_NOT_FOUND
**HTTP Status:** 404 Not Found
**Message:** "The requested resource was not found"
**Details:**
```json
{
  "resource_type": "codebook",
  "resource_id": "uuid"
}
```
**Resolution:** Verify the resource ID is correct and the resource exists.

---

### 4002 - CLIENT_NOT_FOUND
**HTTP Status:** 404 Not Found
**Message:** "Client not found"
**Details:**
```json
{
  "client_id": "uuid"
}
```
**Resolution:** Verify the client ID is correct.

---

### 4003 - CODEBOOK_NOT_FOUND
**HTTP Status:** 404 Not Found
**Message:** "Codebook not found"
**Details:**
```json
{
  "codebook_id": "uuid"
}
```
**Resolution:** Verify the codebook ID is correct.

---

### 4004 - VERSION_NOT_FOUND
**HTTP Status:** 404 Not Found
**Message:** "Codebook version not found"
**Details:**
```json
{
  "version_id": "uuid",
  "codebook_id": "uuid"
}
```
**Resolution:** Verify the version ID is correct.

---

### 4005 - ITEM_NOT_FOUND
**HTTP Status:** 404 Not Found
**Message:** "Codebook item not found"
**Details:**
```json
{
  "item_id": "uuid"
}
```
**Resolution:** Verify the item ID is correct.

---

### 4006 - JOB_NOT_FOUND
**HTTP Status:** 404 Not Found
**Message:** "Job not found"
**Details:**
```json
{
  "job_id": "uuid"
}
```
**Resolution:** Verify the job ID is correct. Jobs may be deleted after 30 days.

---

### 4007 - RECOMMENDATION_NOT_FOUND
**HTTP Status:** 404 Not Found
**Message:** "Recommendation not found"
**Details:**
```json
{
  "recommendation_id": "uuid"
}
```
**Resolution:** Verify the recommendation ID is correct.

---

### 4008 - NO_ACTIVE_VERSION
**HTTP Status:** 404 Not Found
**Message:** "Codebook has no active version"
**Details:**
```json
{
  "codebook_id": "uuid"
}
```
**Resolution:** Create an initial version by uploading items.

---

### 4009 - RESOURCE_DELETED
**HTTP Status:** 410 Gone
**Message:** "This resource has been deleted"
**Details:**
```json
{
  "resource_type": "codebook",
  "resource_id": "uuid",
  "deleted_at": "2025-01-10T12:00:00Z"
}
```
**Resolution:** Resource cannot be accessed. Contact admin if this was a mistake.

---

## 5. External Service Errors (5xxx)

### 5001 - DATABASE_ERROR
**HTTP Status:** 500 Internal Server Error
**Message:** "Database operation failed"
**Details:**
```json
{
  "operation": "INSERT",
  "table": "codebooks"
}
```
**Resolution:** This is a server error. Retry the request. Contact support if persists.

---

### 5002 - DATABASE_CONNECTION_ERROR
**HTTP Status:** 503 Service Unavailable
**Message:** "Cannot connect to database"
**Resolution:** Database is temporarily unavailable. Retry in a few moments.

---

### 5003 - PINECONE_ERROR
**HTTP Status:** 502 Bad Gateway
**Message:** "Vector database operation failed"
**Details:**
```json
{
  "operation": "upsert",
  "error_code": "QUOTA_EXCEEDED"
}
```
**Resolution:** This is a server error. Retry the request. Contact support if persists.

---

### 5004 - PINECONE_UNAVAILABLE
**HTTP Status:** 503 Service Unavailable
**Message:** "Vector database is temporarily unavailable"
**Resolution:** Retry in a few moments. If urgent, contact support.

---

### 5005 - LLM_API_ERROR
**HTTP Status:** 502 Bad Gateway
**Message:** "LLM service returned an error"
**Details:**
```json
{
  "llm_provider": "openai",
  "llm_error_code": "context_length_exceeded",
  "llm_error_message": "This model's maximum context length is 128000 tokens"
}
```
**Resolution:** Reduce the size of the input or split into smaller requests.

---

### 5006 - LLM_UNAVAILABLE
**HTTP Status:** 503 Service Unavailable
**Message:** "LLM service is temporarily unavailable"
**Details:**
```json
{
  "llm_provider": "openai",
  "retry_after_seconds": 60
}
```
**Resolution:** LLM provider is experiencing issues. Job will be retried automatically.

---

### 5007 - LLM_TIMEOUT
**HTTP Status:** 504 Gateway Timeout
**Message:** "LLM service request timed out"
**Details:**
```json
{
  "timeout_seconds": 60
}
```
**Resolution:** LLM took too long to respond. Job will be retried automatically.

---

### 5008 - EMBEDDING_GENERATION_FAILED
**HTTP Status:** 502 Bad Gateway
**Message:** "Failed to generate embeddings"
**Details:**
```json
{
  "model": "text-embedding-3-large",
  "error": "Invalid input"
}
```
**Resolution:** This is a server error. Retry the request. Contact support if persists.

---

## 6. Rate Limit Errors (6xxx)

### 6001 - RATE_LIMIT_EXCEEDED
**HTTP Status:** 429 Too Many Requests
**Message:** "Rate limit exceeded"
**Details:**
```json
{
  "limit": 100,
  "period": "minute",
  "retry_after_seconds": 30
}
```
**Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1610000000
Retry-After: 30
```
**Resolution:** Wait before making more requests. Consider implementing exponential backoff.

---

### 6002 - LLM_RATE_LIMIT_EXCEEDED
**HTTP Status:** 429 Too Many Requests
**Message:** "LLM operation rate limit exceeded"
**Details:**
```json
{
  "limit": 10,
  "period": "hour",
  "retry_after_seconds": 1800
}
```
**Resolution:** LLM operations are rate-limited. Wait before retrying or contact support to increase limit.

---

### 6003 - TOKEN_QUOTA_EXCEEDED
**HTTP Status:** 402 Payment Required
**Message:** "Monthly LLM token quota exceeded"
**Details:**
```json
{
  "quota_tokens": 1000000,
  "used_tokens": 1000000,
  "reset_date": "2025-02-01T00:00:00Z"
}
```
**Resolution:** Upgrade your plan or wait until quota resets on the first of next month.

---

### 6004 - CONCURRENT_REQUEST_LIMIT
**HTTP Status:** 429 Too Many Requests
**Message:** "Too many concurrent requests"
**Details:**
```json
{
  "max_concurrent": 10,
  "current_concurrent": 10
}
```
**Resolution:** Reduce the number of parallel requests.

---

## 7. Job Errors (7xxx)

### 7001 - JOB_FAILED
**HTTP Status:** 500 Internal Server Error
**Message:** "Job execution failed"
**Details:**
```json
{
  "job_id": "uuid",
  "job_type": "refactor",
  "error": "LLM API timeout after 3 retries",
  "failed_at": "2025-01-15T10:30:00Z"
}
```
**Resolution:** Review job error details. Retry the job or contact support.

---

### 7002 - JOB_TIMEOUT
**HTTP Status:** 504 Gateway Timeout
**Message:** "Job execution timed out"
**Details:**
```json
{
  "job_id": "uuid",
  "timeout_seconds": 300,
  "progress": 67
}
```
**Resolution:** Job took too long. It may complete eventually. Check job status.

---

### 7003 - JOB_ALREADY_RUNNING
**HTTP Status:** 409 Conflict
**Message:** "A job is already running for this codebook"
**Details:**
```json
{
  "codebook_id": "uuid",
  "running_job_id": "uuid",
  "job_type": "refactor"
}
```
**Resolution:** Wait for the current job to complete before starting a new one.

---

### 7004 - JOB_CANCELLED
**HTTP Status:** 409 Conflict
**Message:** "Job was cancelled"
**Details:**
```json
{
  "job_id": "uuid",
  "cancelled_by": "user@example.com",
  "cancelled_at": "2025-01-15T10:25:00Z"
}
```
**Resolution:** Job was manually cancelled. Start a new job if needed.

---

### 7005 - INVALID_JOB_STATE
**HTTP Status:** 409 Conflict
**Message:** "Job is not in a valid state for this operation"
**Details:**
```json
{
  "job_id": "uuid",
  "current_status": "completed",
  "required_status": "running",
  "operation": "cancel"
}
```
**Resolution:** Cannot perform operation on job in this state.

---

## 8. Business Logic Errors (8xxx)

### 8001 - CANNOT_DELETE_ACTIVE_VERSION
**HTTP Status:** 409 Conflict
**Message:** "Cannot delete the active version"
**Details:**
```json
{
  "version_id": "uuid",
  "codebook_id": "uuid"
}
```
**Resolution:** Create or activate a different version before deleting this one.

---

### 8002 - CANNOT_REVERT_TO_SAME_VERSION
**HTTP Status:** 400 Bad Request
**Message:** "Cannot revert to the currently active version"
**Details:**
```json
{
  "current_version": 3,
  "requested_version": 3
}
```
**Resolution:** Choose a different version to revert to.

---

### 8003 - VERSION_NUMBER_CONFLICT
**HTTP Status:** 409 Conflict
**Message:** "Version number already exists for this codebook"
**Details:**
```json
{
  "codebook_id": "uuid",
  "version_number": 2
}
```
**Resolution:** This is a server error. Retry the request.

---

### 8004 - RECOMMENDATION_ALREADY_ACTED
**HTTP Status:** 409 Conflict
**Message:** "Recommendation has already been accepted or rejected"
**Details:**
```json
{
  "recommendation_id": "uuid",
  "current_status": "accepted",
  "acted_at": "2025-01-15T10:00:00Z",
  "acted_by": "user@example.com"
}
```
**Resolution:** Cannot change recommendation status once acted upon.

---

### 8005 - EMPTY_CODEBOOK
**HTTP Status:** 400 Bad Request
**Message:** "Cannot perform operation on empty codebook"
**Details:**
```json
{
  "codebook_id": "uuid",
  "operation": "refactor"
}
```
**Resolution:** Upload items before performing this operation.

---

### 8006 - INVALID_RULES_JSON
**HTTP Status:** 422 Unprocessable Entity
**Message:** "Rules JSON schema is invalid"
**Details:**
```json
{
  "validation_errors": [
    "Missing required field: ordering_strategy",
    "Invalid value for naming_template"
  ]
}
```
**Resolution:** Fix the rules JSON structure according to schema.

---

## 9. System Errors (9xxx)

### 9001 - INTERNAL_SERVER_ERROR
**HTTP Status:** 500 Internal Server Error
**Message:** "An unexpected error occurred"
**Details:**
```json
{
  "error_id": "uuid",
  "timestamp": "2025-01-15T10:30:00Z"
}
```
**Resolution:** This is a server error. Our team has been notified. Retry or contact support.

---

### 9002 - SERVICE_UNAVAILABLE
**HTTP Status:** 503 Service Unavailable
**Message:** "Service is temporarily unavailable"
**Details:**
```json
{
  "retry_after_seconds": 60
}
```
**Resolution:** Service is under maintenance or experiencing issues. Retry after specified time.

---

### 9003 - MAINTENANCE_MODE
**HTTP Status:** 503 Service Unavailable
**Message:** "Service is in maintenance mode"
**Details:**
```json
{
  "estimated_completion": "2025-01-15T12:00:00Z",
  "message": "Scheduled maintenance for database upgrades"
}
```
**Resolution:** Wait for maintenance to complete.

---

### 9004 - CONFIGURATION_ERROR
**HTTP Status:** 500 Internal Server Error
**Message:** "Server configuration error"
**Resolution:** This is a server error. Contact support immediately.

---

### 9005 - DEPENDENCY_ERROR
**HTTP Status:** 500 Internal Server Error
**Message:** "Required dependency is not available"
**Details:**
```json
{
  "dependency": "redis",
  "error": "Connection refused"
}
```
**Resolution:** This is a server error. Our team has been notified.

---

## Error Handling Best Practices

### For API Consumers

**1. Always check HTTP status codes**
```typescript
if (response.status !== 200) {
  const error = await response.json();
  console.error(`Error ${error.error.code}: ${error.error.message}`);
}
```

**2. Implement exponential backoff for retries**
```typescript
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status >= 500 || error.status === 429) {
        const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error; // Don't retry client errors
      }
    }
  }
}
```

**3. Handle rate limits gracefully**
```typescript
if (error.code === 'RATE_LIMIT_EXCEEDED') {
  const retryAfter = error.details.retry_after_seconds;
  await sleep(retryAfter * 1000);
  // Retry request
}
```

**4. Display user-friendly messages**
```typescript
const USER_FRIENDLY_MESSAGES = {
  'INVALID_CODEBOOK_TYPE': 'Please select a valid codebook type',
  'FILE_TOO_LARGE': 'Your file is too large. Please upload a file smaller than 10MB',
  'LLM_UNAVAILABLE': 'AI service is temporarily unavailable. Your request will be processed shortly.'
};

const friendlyMessage = USER_FRIENDLY_MESSAGES[error.code] || error.message;
showToast(friendlyMessage);
```

---

### For API Implementers

**1. Always include request_id for tracing**
```typescript
app.use((req, res, next) => {
  req.id = generateUUID();
  res.setHeader('X-Request-ID', req.id);
  next();
});
```

**2. Log errors with full context**
```typescript
logger.error('Database query failed', {
  error_code: 'DATABASE_ERROR',
  request_id: req.id,
  client_id: req.auth.client_id,
  query: 'SELECT * FROM codebooks WHERE...',
  error_message: error.message
});
```

**3. Sanitize error details before returning**
```typescript
// Don't expose internal details in production
const errorDetails = process.env.NODE_ENV === 'production'
  ? { error_id: req.id }
  : { error_id: req.id, stack: error.stack, query: sqlQuery };
```

**4. Use consistent error factory**
```typescript
class APIError extends Error {
  constructor(code, message, details = {}, statusCode = 500) {
    super(message);
    this.code = code;
    this.details = details;
    this.statusCode = statusCode;
  }

  toJSON(requestId) {
    return {
      error: {
        code: this.code,
        message: this.message,
        details: this.details,
        request_id: requestId,
        timestamp: new Date().toISOString()
      }
    };
  }
}
```

---

## Error Code Index

Quick reference for all error codes:

| Code | HTTP | Error Name                     |
|------|------|--------------------------------|
| 1001 | 401  | MISSING_API_KEY                |
| 1002 | 401  | INVALID_API_KEY                |
| 1003 | 401  | EXPIRED_API_KEY                |
| 1004 | 401  | INVALID_JWT_TOKEN              |
| 1005 | 401  | EXPIRED_JWT_TOKEN              |
| 2001 | 403  | FORBIDDEN                      |
| 2002 | 403  | CLIENT_ACCESS_DENIED           |
| 2003 | 403  | INSUFFICIENT_PERMISSIONS       |
| 2004 | 409  | RESOURCE_LOCKED                |
| 3001 | 422  | VALIDATION_ERROR               |
| 3002 | 400  | INVALID_UUID                   |
| 3003 | 400  | INVALID_CODEBOOK_TYPE          |
| 3004 | 400  | INVALID_FILE_TYPE              |
| 3005 | 413  | FILE_TOO_LARGE                 |
| 3006 | 422  | TOO_MANY_ROWS                  |
| 3007 | 422  | INVALID_CSV_FORMAT             |
| 3008 | 400  | INVALID_JSON                   |
| 3009 | 409  | DUPLICATE_CODE                 |
| 3010 | 409  | DUPLICATE_CLIENT_NAME          |
| 4001 | 404  | RESOURCE_NOT_FOUND             |
| 4002 | 404  | CLIENT_NOT_FOUND               |
| 4003 | 404  | CODEBOOK_NOT_FOUND             |
| 4004 | 404  | VERSION_NOT_FOUND              |
| 4005 | 404  | ITEM_NOT_FOUND                 |
| 4006 | 404  | JOB_NOT_FOUND                  |
| 4007 | 404  | RECOMMENDATION_NOT_FOUND       |
| 4008 | 404  | NO_ACTIVE_VERSION              |
| 4009 | 410  | RESOURCE_DELETED               |
| 5001 | 500  | DATABASE_ERROR                 |
| 5002 | 503  | DATABASE_CONNECTION_ERROR      |
| 5003 | 502  | PINECONE_ERROR                 |
| 5004 | 503  | PINECONE_UNAVAILABLE           |
| 5005 | 502  | LLM_API_ERROR                  |
| 5006 | 503  | LLM_UNAVAILABLE                |
| 5007 | 504  | LLM_TIMEOUT                    |
| 5008 | 502  | EMBEDDING_GENERATION_FAILED    |
| 6001 | 429  | RATE_LIMIT_EXCEEDED            |
| 6002 | 429  | LLM_RATE_LIMIT_EXCEEDED        |
| 6003 | 402  | TOKEN_QUOTA_EXCEEDED           |
| 6004 | 429  | CONCURRENT_REQUEST_LIMIT       |
| 7001 | 500  | JOB_FAILED                     |
| 7002 | 504  | JOB_TIMEOUT                    |
| 7003 | 409  | JOB_ALREADY_RUNNING            |
| 7004 | 409  | JOB_CANCELLED                  |
| 7005 | 409  | INVALID_JOB_STATE              |
| 8001 | 409  | CANNOT_DELETE_ACTIVE_VERSION   |
| 8002 | 400  | CANNOT_REVERT_TO_SAME_VERSION  |
| 8003 | 409  | VERSION_NUMBER_CONFLICT        |
| 8004 | 409  | RECOMMENDATION_ALREADY_ACTED   |
| 8005 | 400  | EMPTY_CODEBOOK                 |
| 8006 | 422  | INVALID_RULES_JSON             |
| 9001 | 500  | INTERNAL_SERVER_ERROR          |
| 9002 | 503  | SERVICE_UNAVAILABLE            |
| 9003 | 503  | MAINTENANCE_MODE               |
| 9004 | 500  | CONFIGURATION_ERROR            |
| 9005 | 500  | DEPENDENCY_ERROR               |
