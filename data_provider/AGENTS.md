# AGENTS.md - Data Provider Module (data_provider/)

This module provides market data fetching with multi-source fallback strategy.

## Module Overview

The `data_provider/` directory implements data fetching for A-shares, HK stocks, and US stocks:
- Abstract base class and manager (`base.py`)
- Multiple data source implementations with priority fallback
- Real-time quote types (`realtime_types.py`)

### Data Source Priority (highest to lowest)

| Priority | Fetcher | Description |
|----------|---------|-------------|
| 0 | `efinance_fetcher.py` | East Money (highest priority) |
| 1 | `akshare_fetcher.py` | AkShare - East Money crawler |
| 2 | `tushare_fetcher.py` | Tushare Pro API |
| 2 | `pytdx_fetcher.py` | TDX server |
| 3 | `baostock_fetcher.py` | Baostock |
| 4 | `yfinance_fetcher.py` | Yahoo Finance (fallback) |

### Stock Code Formats

| Market | Format | Example |
|--------|--------|---------|
| A-share (SH) | `600519` | Kweichow Moutai |
| A-share (SZ) | `000001` | Ping An Bank |
| A-share (CYB) | `300750` | CATL |
| HK | `hk00700` or `00700.HK` | Tencent |
| US | `AAPL` | Apple |

## Build/Lint/Test Commands

```bash
# Syntax check
python -m py_compile data_provider/*.py

# Test code recognition
./test.sh code

# Test YFinance conversion
./test.sh yfinance

# Lint
flake8 data_provider/ --max-line-length=120

# Test specific fetcher
python -c "from data_provider.akshare_fetcher import AkshareFetcher; f = AkshareFetcher(); print(f.get_stock_data('600519'))"
```

## Code Style Guidelines

### Strategy Pattern

The module uses the Strategy Pattern for data fetching:
- `BaseFetcher` - Abstract base class defining the interface
- `DataFetcherManager` - Manager that handles fallback logic

```python
from data_provider.base import DataFetcherManager

manager = DataFetcherManager()
data = manager.get_stock_data('600519', days=30)
```

### Base Class Interface

```python
class BaseFetcher(ABC):
    @abstractmethod
    def get_stock_data(self, stock_code: str, days: int = 30) -> pd.DataFrame:
        """Fetch historical OHLCV data."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the data source is available."""
        pass
```

### Rate Limiting and Retry

All fetchers implement:
- Rate limiting (sleep between requests)
- Exponential backoff retry using `tenacity`
- Circuit breaker pattern

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_data(self, code: str):
    # Implementation
    pass
```

### Custom Exceptions

```python
from data_provider.base import DataFetchError, RateLimitError, DataSourceUnavailableError

try:
    data = fetcher.get_stock_data('600519')
except RateLimitError:
    # Handle rate limiting
    pass
except DataSourceUnavailableError:
    # Handle source unavailable
    pass
```

### Naming Conventions

- Fetcher classes: `PascalCase` + `Fetcher` (e.g., `AkshareFetcher`)
- Private methods: `_leading_underscore`
- Module files: `snake_case_fetcher.py`

## Data Normalization

All fetchers normalize output to standard format:

| Column | Type | Description |
|--------|------|-------------|
| `date` | datetime | Trading date |
| `open` | float | Open price |
| `high` | float | High price |
| `low` | float | Low price |
| `close` | float | Close price |
| `volume` | int | Volume |
| `amount` | float | Amount |
| `pct_chg` | float | Percentage change |

## Anti-Rate-Limit Strategy

1. **Sleep between requests**: Configurable via `akshare_sleep_min`, `akshare_sleep_max`
2. **Multi-source fallback**: Automatic switch to next source on failure
3. **Circuit breaker**: Temporarily disable failing sources
4. **Caching**: Real-time quotes cached for `realtime_cache_ttl` seconds

## Dependencies

Key dependencies:
- `akshare` - A-share data (East Money crawler)
- `efinance` - East Money official API
- `tushare` - Tushare Pro (requires token)
- `pytdx` - TDX server
- `baostock` - Baostock
- `yfinance` - Yahoo Finance
- `pandas`, `numpy` - Data processing

## Module Relationships

```
src/core/pipeline.py
    └── data_provider/base.py (DataFetcherManager)
            ├── data_provider/efinance_fetcher.py
            ├── data_provider/akshare_fetcher.py
            ├── data_provider/tushare_fetcher.py
            ├── data_provider/pytdx_fetcher.py
            ├── data_provider/baostock_fetcher.py
            └── data_provider/yfinance_fetcher.py
```

## Important Notes

- A-shares: Use `efinance` or `akshare` first
- HK stocks: Support via `akshare` and `yfinance`
- US stocks: Use `yfinance` only
- Real-time data: Priority via `tencent`, `akshare_sina`, `efinance`
