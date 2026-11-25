
# S4Bridge

### Enterprise SAP Integration and Order Management Platform

S4Bridge is a backend-focused enterprise integration platform built with Python and FastAPI. It demonstrates business data management, inventory control, sales order processing, and reliable integration workflows through a simulated SAP S/4HANA-compatible adapter.

## Key Features

- **Customer Management:** Create, retrieve, update, and manage customer records.
- **Product Management:** Maintain product information, SKUs, pricing, and active status.
- **Inventory Management:** Track warehouse-level stock, reserved quantities, and reorder levels.
- **Sales Order Management:** Create orders with automatic pricing calculations and inventory reservation.
- **SAP Integration:** Simulated SAP synchronization workflow with event tracking.
- **Idempotency:** Prevent duplicate integration events using idempotency keys.
- **Retry Handling:** Retry failed integration events.
- **Persistent Storage:** PostgreSQL for business data and integration metadata; MongoDB for integration payloads.
- **Database Migrations:** Schema versioning and management using Alembic.
- **Automated Testing:** API and integration tests using Pytest and HTTPX2.

## Technology Stack

| Category | Technologies |
|---|---|
| Language | Python |
| Backend | FastAPI, REST APIs |
| ORM | SQLAlchemy |
| Databases | PostgreSQL, MongoDB |
| Migrations | Alembic |
| Validation | Pydantic |
| Testing | Pytest, HTTPX2 |
| Code Quality | Ruff |
| Infrastructure | Docker, Docker Compose |
| API Documentation | OpenAPI, Swagger UI |

## Architecture

```text
                 Client Applications
                         |
                         v
                  FastAPI REST API
                         |
                         v
                  Business Services
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
         Customers   Products   Sales Orders
                                     |
                                     v
                                  Inventory
                         |
                         v
                 Integration Services
                         |
                         v
              Simulated SAP Adapter
                         |
              +----------+----------+
              |                     |
              v                     v
          PostgreSQL             MongoDB
       Business Data &        Integration Payloads
       Event Metadata
```

## Project Structure

S4Bridge/
|-- app/
|   |-- api/
|   |   `-- v1/endpoints/
|   |-- core/
|   |-- db/
|   |-- integrations/
|   |   |-- sap/
|   |   `-- sync/
|   |-- models/
|   |-- schemas/
|   |-- services/
|   `-- main.py
|-- migrations/
|-- scripts/
|-- tests/
|   |-- api/
|   |-- integration/
|   `-- unit/
|-- docs/
|-- .github/
|   `-- workflows/
|-- .env.example
|-- docker-compose.yml
|-- alembic.ini
|-- requirements.txt
`-- README.md


## Prerequisites

- Python 3.12 or later
- Docker Desktop with Docker Compose
- Git

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/nikitam2612/S4Bridge.git
cd S4Bridge
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local database credentials if required.

### 5. Start PostgreSQL and MongoDB

```powershell
docker compose up -d
```

### 6. Apply database migrations

```powershell
alembic upgrade head
```

### 7. Start the application

```powershell
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health Check: http://127.0.0.1:8000/health

## Running Tests

Run the complete test suite:

```powershell
python -m pytest -v
```

Run code quality checks:

```powershell
ruff check .
ruff format --check .
```

## Database Management

S4Bridge uses Alembic for database schema versioning.

```powershell
alembic current
alembic history
alembic upgrade head
```

## SAP Integration Note

The current SAP adapter is a **simulated integration** designed to demonstrate enterprise synchronization concepts, event persistence, idempotency, and retry handling.

It does not establish a live connection to an SAP S/4HANA system.

## Current Test Status

- 12 automated tests passing.
- API endpoint tests.
- Sales order and inventory reservation tests.
- Integration idempotency tests.
- SAP synchronization failure-handling tests.

## Future Enhancements

- JWT-based authentication and role-based access control.
- Production SAP S/4HANA connectivity using actual SAP APIs.
- Transactional outbox and background event processing.
- Expanded integration and concurrency testing.
- CI/CD automation and cloud deployment.
- Structured logging and application monitoring.

## Author

**Nikita Manjul**

GitHub: https://github.com/nikitam2612
