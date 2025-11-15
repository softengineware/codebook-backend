# Construction Codebook AI Backend - Replit Setup

## Overview
This is an AI-powered construction codebook management system backend built with FastAPI. The system helps civil construction consultants generate, analyze, and maintain material, activity, and bid item codebooks for multiple clients.

## Project Status
**Status:** Initial setup complete  
**Last Updated:** November 15, 2025

The project has been imported from GitHub and configured to run in the Replit environment. All placeholder routes are functional, and the server is running on port 5000.

## Quick Start

### Running the Application
The FastAPI backend runs automatically via the configured workflow. It's accessible at:
- **Main API:** http://localhost:5000/
- **Health Check:** http://localhost:5000/health
- **API Documentation:** http://localhost:5000/docs
- **API v1 Endpoints:** http://localhost:5000/v1/*

### Current Implementation Status

#### ✅ Completed
- FastAPI application structure
- Route placeholders for all major endpoints (clients, codebooks, versions, jobs, auth, health)
- Development configuration with sensible defaults
- Uvicorn server configured on port 5000
- Auto-reload enabled for development
- Swagger/OpenAPI documentation available

#### 🚧 To Be Implemented
The following features are scaffolded but need full implementation:

1. **Database Integration**
   - Supabase connection (requires API credentials)
   - PostgreSQL schema creation
   - Repository layer implementations

2. **Vector Search**
   - Pinecone integration (requires API credentials)
   - Embedding generation
   - Semantic search capabilities

3. **LLM Integration**
   - OpenAI/Anthropic integration (requires API credentials)
   - Prompt template management
   - Analysis and recommendation generation

4. **Authentication & Authorization**
   - API key validation
   - JWT token management
   - Role-based access control

5. **Business Logic**
   - Codebook upload and parsing
   - Version management
   - Job queue processing
   - Audit logging

## Project Structure

```
.
├── src/
│   ├── api/
│   │   ├── dependencies/   # Auth and other dependencies
│   │   └── routes/        # API endpoint handlers
│   │       ├── auth.py
│   │       ├── clients.py
│   │       ├── codebooks.py
│   │       ├── health.py
│   │       ├── jobs.py
│   │       └── versions.py
│   ├── core/              # Configuration and utilities
│   │   ├── config.py
│   │   ├── errors.py
│   │   └── logging_config.py
│   ├── models/            # Pydantic models
│   ├── repositories/      # Database access layer
│   └── services/          # Business logic
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── pyproject.toml       # Project metadata
```

## Configuration

### Environment Variables
The application uses environment variables for configuration. Default values are set in `src/core/config.py` for development. For production, set these environment variables:

**Required for Full Functionality:**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service key
- `PINECONE_API_KEY` - Pinecone API key
- `PINECONE_INDEX_NAME` - Pinecone index name
- `LLM_API_KEY` - OpenAI or Anthropic API key

**Application Settings:**
- `PORT` - Server port (default: 5000)
- `APP_ENV` - Environment (development/production)
- `LOG_LEVEL` - Logging level (default: INFO)

### Development Defaults
The application starts with placeholder values for development:
- Port: 5000
- Environment: development
- CORS: Allows localhost:3000 and localhost:5000
- All external service keys use placeholder values

## Available Endpoints

### Health
- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check

### Root
- `GET /` - API information

### Authentication (v1)
- `POST /v1/auth/login` - User login (placeholder)
- `POST /v1/auth/logout` - User logout (placeholder)
- `POST /v1/auth/refresh` - Token refresh (placeholder)

### Clients (v1)
- `GET /v1/clients` - List clients (placeholder)
- `POST /v1/clients` - Create client (placeholder)
- `GET /v1/clients/{client_id}` - Get client details (placeholder)

### Codebooks (v1)
- `GET /v1/clients/{client_id}/codebooks` - List codebooks (placeholder)
- `POST /v1/clients/{client_id}/codebooks` - Create codebook (placeholder)
- `GET /v1/clients/{client_id}/codebooks/{codebook_id}` - Get codebook (placeholder)
- `POST /v1/clients/{client_id}/codebooks/upload` - Upload codebook (placeholder)

### Versions (v1)
- `GET /v1/codebooks/{codebook_id}/versions` - List versions (placeholder)
- `GET /v1/codebooks/{codebook_id}/versions/{version_id}` - Get version (placeholder)
- `POST /v1/codebooks/{codebook_id}/versions/{version_id}/activate` - Activate version (placeholder)

### Jobs (v1)
- `GET /v1/jobs` - List jobs (placeholder)
- `GET /v1/jobs/{job_id}` - Get job status (placeholder)
- `DELETE /v1/jobs/{job_id}` - Cancel job (placeholder)

## Next Steps for Development

1. **Set Up External Services**
   - Create Supabase project and run schema migrations
   - Set up Pinecone index
   - Obtain LLM API credentials

2. **Implement Core Features**
   - Complete repository layer implementations
   - Implement authentication system
   - Build codebook upload and parsing logic
   - Integrate LLM for analysis

3. **Testing**
   - Add unit tests
   - Add integration tests
   - Test async job processing

4. **Documentation**
   - Review existing documentation in:
     - `SPEC.md` - Product specification
     - `DATA_MODEL.md` - Database schema
     - `ARCHITECTURE.md` - System architecture
     - `API.md` - API documentation
     - `TASKS.md` - Implementation roadmap

## Development Workflow

The FastAPI server runs with auto-reload enabled, so changes to Python files will automatically restart the server. The workflow is configured to:
- Run on port 5000 (accessible via webview)
- Enable hot-reload for development
- Use JSON logging format in production, console format in development

## Technology Stack

- **Framework:** FastAPI 0.109.0
- **Server:** Uvicorn 0.27.0
- **Database:** Supabase (PostgreSQL)
- **Vector DB:** Pinecone
- **LLM:** OpenAI/Anthropic
- **Auth:** JWT + API Keys
- **Testing:** pytest
- **Code Quality:** ruff, black, mypy

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Supabase Documentation: https://supabase.com/docs
- Pinecone Documentation: https://docs.pinecone.io/
- OpenAI API: https://platform.openai.com/docs

## Recent Changes

### November 15, 2025 - Initial Replit Setup
- Imported project from GitHub
- Installed Python 3.11 and all dependencies
- Created placeholder route files for all endpoints
- Configured FastAPI to run on port 5000
- Fixed dependency conflicts (httpx version)
- Set up development-friendly defaults in config
- Removed global database client initialization to prevent startup errors
- Simplified route implementations to work without database dependencies
- Verified all endpoints are accessible and return appropriate responses
- API documentation (Swagger UI) is available at /docs
