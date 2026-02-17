# AGENTS.md - FastAPI Web Interface Module (api/)

This module provides the RESTful API interface for the Daily Stock Analysis system.

## Module Overview

The `api/` directory implements the FastAPI-based web interface:
- Application factory and configuration (`app.py`)
- Dependency injection (`deps.py`)
- API versioning and routing (`v1/`)
- Middleware for error handling (`middlewares/`)

### API Endpoints (v1)

| Endpoint | Description |
|----------|-------------|
| `/api/v1/analysis` | Trigger stock analysis, get analysis results |
| `/api/v1/stocks` | Stock data, image extraction for stock codes |
| `/api/v1/history` | Historical analysis records |
| `/api/v1/backtest` | Backtest management and results |
| `/api/v1/system` | System configuration management |
| `/api/health` | Health check endpoint |

### Subdirectories

- `v1/` - API version 1 implementation
  - `endpoints/` - Route handlers
  - `schemas/` - Pydantic request/response models
- `middlewares/` - Error handlers, logging, etc.

## Build/Lint/Test Commands

```bash
# Syntax check
python -m py_compile api/app.py api/deps.py
python -m py_compile api/v1/*.py api/v1/endpoints/*.py api/v1/schemas/*.py

# Lint
flake8 api/ --max-line-length=120

# Run API server locally
python main.py --serve-only --port 8000

# Run with auto-reload (development)
uvicorn api.app:app --reload --port 8000

# API documentation (when server running)
# Open http://localhost:8000/docs for Swagger UI
# Open http://localhost:8000/redoc for ReDoc
```

## Code Style Guidelines

### FastAPI Patterns

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class StockRequest(BaseModel):
    code: str
    days: int = 30

class StockResponse(BaseModel):
    code: str
    name: str
    data: list

@router.post("/analyze", response_model=StockResponse)
async def analyze_stock(request: StockRequest):
    """Analyze a single stock."""
    # Implementation
    pass
```

### Dependency Injection

```python
from api.deps import get_config

@router.get("/config")
async def get_system_config(config = Depends(get_config)):
    return {"stock_list": config.stock_list}
```

### Error Handling

```python
from fastapi import HTTPException

@router.get("/stock/{code}")
async def get_stock(code: str):
    if not code:
        raise HTTPException(status_code=400, detail="Stock code required")
    # ...
```

### Naming Conventions

- Route files: `snake_case.py` (e.g., `stock_analysis.py`)
- Router objects: `router` (lowercase)
- Schema classes: `PascalCase` with suffix (e.g., `StockRequest`, `StockResponse`)
- Endpoint functions: `snake_case` (e.g., `get_stock`, `trigger_analysis`)

## API Design Guidelines

### Request/Response Models

- All endpoints should use Pydantic models for request body and response
- Place models in `api/v1/schemas/` directory
- Use descriptive names with `Request`/`Response` suffix

### HTTP Methods

- `GET` - Retrieve data (idempotent)
- `POST` - Create or trigger actions
- `PUT` - Update resources
- `DELETE` - Remove resources

### Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad request (client error)
- `404` - Not found
- `500` - Internal server error

### CORS Configuration

Configured in `app.py`:
- Default origins: `localhost:5173`, `localhost:3000`
- Set `CORS_ALLOW_ALL=true` for development
- Set `CORS_ORIGINS` for additional origins

## Static Files

The API serves the frontend SPA from the `static/` directory:
- Built frontend files from `apps/dsa-web/`
- SPA fallback to `index.html` for client-side routing

## Testing

```bash
# Run API-specific tests
python -m pytest tests/test_system_config_api.py -v

# Test with pytest-asyncio
python -m pytest tests/ -v -k "api"
```

## Module Relationships

```
main.py
    └── api/app.py (FastAPI factory)
            ├── api/v1/router.py (route aggregation)
            │       ├── api/v1/endpoints/analysis.py
            │       ├── api/v1/endpoints/stocks.py
            │       ├── api/v1/endpoints/history.py
            │       ├── api/v1/endpoints/backtest.py
            │       └── api/v1/endpoints/system_config.py
            ├── api/middlewares/error_handler.py
            └── static/ (frontend SPA)
```

## Dependencies

- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `python-multipart` - Form/file upload support
