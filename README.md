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

# Improvements Implemented

- Added `/list-predictions` endpoint  
- Implemented PostgreSQL adapter with atomic upsert  
- Containerized full stack via Docker Compose  
- Added cross-platform run scripts  
- Added CI with lint and Postgres integration tests  
- Introduced capability-driven configuration model  
- Added dependency injection support for improved testability  

---

# Future Improvements

- Asynchronous API Execution
- Debugging & Error Handling
- Observability enhancement - inference level metadata storage
