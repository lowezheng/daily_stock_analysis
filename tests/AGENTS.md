# AGENTS.md - Test Module (tests/)

This module contains unit and integration tests for the Daily Stock Analysis system.

## Module Overview

The `tests/` directory provides comprehensive test coverage:
- Unit tests for core functionality
- Integration tests for services and repositories
- Network-dependent tests (marked separately)

### Test Files

| File | Description |
|------|-------------|
| `test_storage.py` | Database storage tests |
| `test_backtest_service.py` | Backtest service integration tests |
| `test_backtest_engine.py` | Backtest engine unit tests |
| `test_backtest_summary.py` | Backtest summary tests |
| `test_stock_analyzer_bias.py` | Bias threshold calculation tests |
| `test_news_intel.py` | News intelligence tests |
| `test_search_news_freshness.py` | News freshness validation tests |
| `test_get_latest_data.py` | Data fetching tests |
| `test_system_config_service.py` | Config service tests |
| `test_system_config_api.py` | Config API tests |
| `test_analysis_history.py` | Analysis history tests |

## Build/Lint/Test Commands

```bash
# Run all offline tests (no network)
python -m pytest -m "not network" -v

# Run all tests including network tests
python -m pytest -v

# Run single test file
python -m pytest tests/test_storage.py -v

# Run single test class
python -m pytest tests/test_backtest_service.py::BacktestServiceTestCase -v

# Run single test method
python -m pytest tests/test_backtest_service.py::BacktestServiceTestCase::test_run_backtest -v

# Run with coverage
python -m pytest --cov=src --cov=api --cov=data_provider tests/

# Run specific marker
python -m pytest -m unit -v          # Fast offline unit tests
python -m pytest -m integration -v   # Integration tests
python -m pytest -m network -v       # Network-dependent tests

# Lint
flake8 tests/ --max-line-length=120
```

## Test Markers

Tests are categorized using pytest markers:

```python
import pytest

@pytest.mark.unit
def test_pure_logic():
    """Fast offline unit test."""
    pass

@pytest.mark.integration
def test_service_integration():
    """Service-level integration test."""
    pass

@pytest.mark.network
def test_external_api():
    """Test requiring external network/API."""
    pass
```

## Code Style Guidelines

### Test Structure

```python
import unittest
import tempfile
import os

class MyTestCase(unittest.TestCase):
    """Test case description."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        # Initialize test dependencies
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_feature(self):
        """Test specific feature."""
        # Arrange
        input_data = "test"
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        self.assertEqual(result, expected)
    
    def test_edge_case(self):
        """Test edge case handling."""
        with self.assertRaises(ValueError):
            function_under_test(None)
```

### Naming Conventions

- Test files: `test_<module>.py` (e.g., `test_storage.py`)
- Test classes: `<Module>TestCase` or `Test<Feature>`
- Test methods: `test_<scenario>` (e.g., `test_parse_sniper_value`)

### Test Database

Use temporary SQLite databases for isolation:

```python
def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()
    self.db_path = os.path.join(self.temp_dir.name, "test.db")
    os.environ["DATABASE_PATH"] = self.db_path
    # Reset singletons
    Config._instance = None
    DatabaseManager.reset_instance()
    self.db = DatabaseManager.get_instance()

def tearDown(self):
    DatabaseManager.reset_instance()
    self.temp_dir.cleanup()
```

### Assertions

```python
# Equality
self.assertEqual(actual, expected)
self.assertNotEqual(a, b)

# Boolean
self.assertTrue(condition)
self.assertFalse(condition)

# None checks
self.assertIsNone(value)
self.assertIsNotNone(value)

# Exceptions
with self.assertRaises(ValueError):
    raise ValueError()

# Approximate equality (floats)
self.assertAlmostEqual(1.0, 1.0001, places=3)

# Container checks
self.assertIn(item, container)
self.assertNotIn(item, container)
```

## CI Integration

Tests are run in CI pipeline:
1. `backend-gate`: Syntax check + flake8 + offline tests
2. `network-smoke`: Network-dependent tests (non-blocking)

See `scripts/ci_gate.sh` and `.github/workflows/` for details.

## Test Helpers

### Mocking

```python
from unittest.mock import patch, MagicMock

@patch('src.config.get_config')
def test_with_mock(mock_get_config):
    mock_config = MagicMock()
    mock_config.stock_list = ['600519']
    mock_get_config.return_value = mock_config
```

### Fixtures (pytest)

```python
import pytest

@pytest.fixture
def temp_db():
    """Provide temporary database."""
    temp_dir = tempfile.TemporaryDirectory()
    db_path = os.path.join(temp_dir.name, "test.db")
    yield db_path
    temp_dir.cleanup()

def test_with_fixture(temp_db):
    assert os.path.exists(temp_db)
```

## Dependencies

- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `unittest` - Standard library (for TestCase)
- `unittest.mock` - Mocking utilities
