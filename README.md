# NIQ Innovation Enablement – Object Counter Challenge

[![CI](https://github.com/ripytraw/object-counter/actions/workflows/ci.yml/badge.svg)](https://github.com/ripytraw/object-counter/actions/workflows/ci.yml)

The goal of this repository is to demonstrate how to apply **Hexagonal Architecture (Ports & Adapters)** in an ML-based system.

This application consists of a Flask API that receives an image and a threshold and returns:

- The number of detected objects grouped by class  
- A list of predictions above the given threshold  
- A cumulative count of detected objects persisted in a database  

---

# Architecture

The application is composed of three layers:

## Entrypoints
Exposes the API and receives requests. Responsible for validation and formatting responses.

## Adapters
Communicates with external services (TensorFlow Serving, databases).  
Translates domain objects to external representations and vice versa.

## Domain
Contains business logic and use cases. Orchestrates external calls and applies business rules.  
The domain layer is fully infrastructure-independent.

---

# Configuration Model

Infrastructure selection for the Object & Count Adapters is controlled following environment variables.

| Variable | Description |
|----------|------------|
| `MODEL_TYPE` | `fake` or `tensorflow` |
| `COUNT_BACKEND_TYPE` | `inmemory`, `mongo`, `postgres` |

# Environment Setup

```bash
cp .env.example .env
```

Update the variables in `.env` as needed.

---

# Running the Application

## Local Development

Unix:

```bash
./scripts/run.sh dev
```

PowerShell:

```powershell
.\scripts\run.ps1 dev
```

---

## Production-Like Mode (Docker)

Unix:

```bash
./scripts/run.sh prod-up
```

PowerShell:

```powershell
.\scripts\run.ps1 prod-up
```

Stop services:

```bash
./scripts/run.sh prod-down
```

---

# Calling the Service

```bash
curl -F "threshold=0.9" \
     -F "file=@resources/images/cat.jpg" \
     http://localhost:5000/object-count
```

```bash
curl -F "threshold=0.9" \
     -F "file=@resources/images/cat.jpg" \
     http://localhost:5000/list-predictions
```

---

# Running Tests

```bash
pytest
```

CI runs:

- flake8 lint checks  
- Validation & Unit Test cases for new endpoint
- PostgreSQL-backed integration tests  
- Fake object detector for deterministic execution  

---

## Improvements Implemented

- Added `/list-predictions` endpoint with threshold-based filtering and input validation.
- Implemented PostgreSQL adapter with atomic upsert (`ON CONFLICT DO UPDATE`) and concurrency-safe counting.
- Introduced capability-driven configuration (`MODEL_TYPE`, `COUNT_BACKEND_TYPE`, `DATABASE_URL`) for scalable backend selection.
- Refactored `create_app()` to support optional dependency injection for improved test isolation and modular wiring.
- Containerized the full stack using Docker and Docker Compose.
- Added cross-platform run scripts (`run.sh`, `run.ps1`) for standardized local setup.
- Integrated CI pipeline with:
  - Static analysis (flake8)
  - Automated unit and integration tests
  - Infrastructure-backed Postgres validation via service containers.

---

## Proposed / Future Improvements

- Introduce schema-based API input validation and standardized response envelopes.
- Enforce request size limits and early MIME-type validation for uploaded images.
- Implement streaming-based file handling to prevent in-memory loading of large uploads.
- Standardize structured error handling and centralized JSON logging (including request tracing fields such as `request_id`, `endpoint`, `model_name`, `threshold`, `status_code`, `response_time_ms`).
- Introduce rate limiting and authentication mechanisms for API protection.
- Add request tracing and correlation IDs to support distributed observability.
- Transition to asynchronous I/O handling for database and inference operations.
- Enhance monitoring and observability by:
  - Persisting inference-level metadata (image ID, threshold, model version, object counts, request ID).
  - Externalizing debug artifacts to centralized storage (e.g., S3 or MLflow).
- Extend TensorFlow Serving setup to support multi-model and versioned deployments via a centralized model registry.