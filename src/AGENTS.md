# AGENTS.md - Core Business Logic Module (src/)

This module contains the core business logic for the Daily Stock Analysis system.

## Module Overview

The `src/` directory implements the main business logic including:
- AI-powered stock analysis (`analyzer.py`, `stock_analyzer.py`, `market_analyzer.py`)
- Configuration management (`config.py`)
- Notification services (`notification.py`)
- Data storage and persistence (`storage.py`)
- Search and news services (`search_service.py`)
- Task scheduling (`scheduler.py`)
- Output formatting (`formatters.py`)
- Logging configuration (`logging_config.py`)

### Subdirectories

- `core/` - Core pipeline, backtest engine, and config management
- `services/` - Business services (stock, analysis, backtest, history, task queue)
- `repositories/` - Data access layer (stock, analysis, backtest repos)

## Build/Lint/Test Commands

```bash
# Syntax check
python -m py_compile src/config.py src/analyzer.py src/notification.py
python -m py_compile src/storage.py src/scheduler.py src/search_service.py
python -m py_compile src/market_analyzer.py src/stock_analyzer.py

# Run offline tests
python -m pytest -m "not network" tests/

# Run single test file
python -m pytest tests/test_stock_analyzer_bias.py -v

# Run specific test function
python -m pytest tests/test_backtest_service.py::TestBacktestService::test_run_backtest -v

# Lint (critical errors only)
flake8 src/ --select=E9,F63,F7,F82 --max-line-length=120

# Full lint
flake8 src/ --max-line-length=120
```

## Code Style Guidelines

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Use absolute imports: `from src.config import get_config`
- Group imports with blank lines

### Formatting
- Line width: 120 characters max
- Use `black` for formatting
- Use `isort` with profile=black for import sorting
- 4 spaces indentation

### Naming Conventions
- Functions: `snake_case` (e.g., `get_stock_data`, `run_analysis`)
- Classes: `PascalCase` (e.g., `StockAnalyzer`, `NotificationService`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- Private methods: `_leading_underscore` (e.g., `_fetch_data`)

### Type Hints
- Use type hints for function parameters and return values
- Use `Optional[T]` for nullable types
- Use `List[T]`, `Dict[K, V]` for collections
- Example:
  ```python
  def analyze_stock(code: str, days: int = 30) -> Optional[AnalysisResult]:
  ```

### Error Handling
- Use custom exceptions from the codebase: `DataFetchError`, `RateLimitError`
- Use `tenacity` for retry with exponential backoff
- Log errors with context using the `logging` module
- Never catch and silently ignore exceptions

### Logging
- Use Python's `logging` module
- Get logger via `logger = logging.getLogger(__name__)`
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include relevant context in log messages

## Key Patterns

### Configuration Access
```python
from src.config import get_config, Config

config: Config = get_config()
stock_list = config.stock_list
```

### Service Layer Pattern
- Services in `src/services/` encapsulate business logic
- Repositories in `src/repositories/` handle data access
- Services should not directly access the database

### Pipeline Pattern
- `src/core/pipeline.py` orchestrates the analysis workflow
- Uses dependency injection for services

## Dependencies

Key dependencies used in this module:
- `google-generativeai` - Gemini AI API
- `anthropic` - Claude API
- `openai` - OpenAI-compatible API
- `tenacity` - Retry mechanism
- `sqlalchemy` - ORM for database
- `schedule` - Task scheduling
- `pandas`, `numpy` - Data processing

## Module Relationships

```
main.py
    └── src/core/pipeline.py
            ├── src/analyzer.py (AI analysis)
            ├── src/stock_analyzer.py (stock-specific analysis)
            ├── src/notification.py (push notifications)
            ├── src/search_service.py (news search)
            └── data_provider/ (market data)
```

## Important Notes

- All configuration is loaded from `.env` via `src/config.py`
- The system uses a singleton pattern for config
- AI analysis priority: Gemini > Anthropic > OpenAI
- Data source priority: efinance > akshare > tushare > pytdx > baostock > yfinance
