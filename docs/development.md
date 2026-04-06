# Jesse -- Development Guide

## Setting Up the Development Environment

### Prerequisites

- Python 3.10+
- PostgreSQL (for candle storage and session tracking)
- Redis (for inter-process communication)

### Installation

```bash
# Clone and install in development mode
git clone <repo-url>
cd jesse
pip install -e .

# Or with uv
uv sync --active --all-groups --all-extras
```

### Configuration

Jesse reads environment variables from a `.env` file in the project root:

```env
APP_PORT=9000
APP_HOST=0.0.0.0
APP_PASSWORD=your-password

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jesse
POSTGRES_USER=jesse
POSTGRES_PASSWORD=jesse

REDIS_HOST=localhost
REDIS_PORT=6379
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_backtest.py

# Run by name pattern
pytest -k test_order_submission

# With coverage
pytest --cov=jesse

# Verbose output
pytest -v tests/test_strategy.py
```

### Test Structure

Tests are organized in `/tests/` and use test strategies from `src/jesse/strategies/Test*/`:

| Test File | Coverage Area |
|-----------|--------------|
| `test_backtest.py` | Backtesting engine |
| `test_strategy.py` | Strategy lifecycle |
| `test_broker.py` | Order placement |
| `test_indicators.py` | Technical indicators |
| `test_position.py` | Position management |
| `test_order.py` | Order model |
| `test_helpers.py` | Utility functions |
| `test_metrics.py` | Performance calculations |

There are 137+ test strategy implementations (`Test01` through `Test48` and named test strategies) that exercise specific framework behaviors.

### Testing Utilities

```python
from jesse.testing_utils import get_btc_candles, set_up, single_route_backtest

# Set up test environment
set_up()

# Run a single-route backtest for testing
result = single_route_backtest('TestStrategyName', candles)
```

## Creating a Strategy

### Via Web Dashboard

1. Navigate to `http://localhost:9000`
2. Use the Strategy panel to create a new strategy
3. The built-in code editor provides autocompletion

### Manual Creation

Create a directory under your project's `strategies/` folder:

```
strategies/
  MyStrategy/
    __init__.py
```

### Strategy Template

```python
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

class MyStrategy(Strategy):
    # --- Required Methods ---

    def should_long(self) -> bool:
        """Return True when conditions favor a long entry."""
        return False

    def should_short(self) -> bool:
        """Return True when conditions favor a short entry."""
        return False

    def go_long(self):
        """Define long entry orders. Called when should_long() returns True."""
        qty = utils.size_to_qty(self.balance * 0.05, self.price)
        self.buy = qty, self.price
        self.stop_loss = qty, self.price * 0.95
        self.take_profit = qty, self.price * 1.10

    def go_short(self):
        """Define short entry orders. Called when should_short() returns True."""
        pass

    # --- Optional Lifecycle Hooks ---

    def before(self):
        """Called before each candle is processed."""
        pass

    def after(self):
        """Called after each candle is processed."""
        pass

    def update_position(self):
        """Called on every candle when a position is open.
        Use for trailing stops, dynamic TP/SL, position scaling."""
        pass

    def on_open_position(self, order):
        """Triggered when a position is opened."""
        pass

    def on_close_position(self, order):
        """Triggered when a position is closed."""
        pass

    def on_increased_position(self, order):
        """Triggered when position size increases."""
        pass

    def on_reduced_position(self, order):
        """Triggered when position size decreases."""
        pass

    def on_cancel(self, order):
        """Triggered when an order is cancelled."""
        pass

    def before_terminate(self):
        """Called before the strategy terminates (end of backtest)."""
        pass

    def terminate(self):
        """Called when the strategy terminates."""
        pass

    def filters(self) -> list:
        """Return a list of filter functions. Each must return True for a trade to proceed."""
        return []

    # --- Optimization ---

    def hyperparameters(self):
        """Define searchable hyperparameters for optimization."""
        return [
            {'name': 'ema_fast', 'type': int, 'min': 5, 'max': 50, 'default': 20},
            {'name': 'ema_slow', 'type': int, 'min': 30, 'max': 200, 'default': 50},
            {'name': 'risk_pct', 'type': float, 'min': 0.01, 'max': 0.10, 'default': 0.05},
        ]
```

## Order Placement Patterns

### Single Orders

```python
# Entry orders
self.buy = qty, price       # Limit buy
self.sell = qty, price       # Limit sell

# Exit orders
self.stop_loss = qty, price
self.take_profit = qty, price
```

### Multiple Orders (Scaling In/Out)

```python
def go_long(self):
    qty = utils.size_to_qty(self.balance * 0.05, self.price)
    # Scale into position at multiple prices
    self.buy = [
        (qty * 0.5, self.price),
        (qty * 0.5, self.price * 0.98),
    ]
    self.stop_loss = qty, self.price * 0.95
    self.take_profit = [
        (qty * 0.5, self.price * 1.05),
        (qty * 0.5, self.price * 1.10),
    ]
```

### Dynamic Position Management

```python
def update_position(self):
    # Trailing stop
    if self.position.pnl_percentage > 5:
        new_sl = self.position.entry_price * 1.02
        self.stop_loss = self.position.qty, new_sl

    # Scale out at profit targets
    if self.position.pnl_percentage > 10:
        self.liquidate(0.5)  # Close 50%
```

## Using Indicators

```python
import jesse.indicators as ta

class MyStrategy(Strategy):
    @property
    @cached
    def ema_fast(self):
        return ta.ema(self.candles, period=self.hp.get('ema_fast', 20))

    @property
    @cached
    def rsi(self):
        return ta.rsi(self.candles, period=14)

    def should_long(self):
        return (
            self.ema_fast > ta.ema(self.candles, 50) and
            self.rsi < 70
        )
```

Available indicator categories:
- **Trend**: EMA, SMA, DEMA, TEMA, WMA, HMA, ALMA, SuperTrend
- **Momentum**: RSI, MACD, Stochastic, CCI, ADX, MFI
- **Volatility**: Bollinger Bands, ATR, Standard Deviation
- **Volume**: OBV, NVI, PVI, VWMA
- **Oscillators**: Aroon, Williams %R, Ultimate Oscillator

## Accessing Cross-Route Data

```python
from jesse.store import store

class MyStrategy(Strategy):
    def should_long(self):
        # Read candles from another symbol
        btc_candles = store.candles.get_candles('Binance', 'BTC-USDT', '1h')
        btc_trend = ta.ema(btc_candles, 50)

        # Only go long if BTC is also trending up
        return self.ema_fast > self.ema_slow and btc_trend[-1] > btc_trend[-2]
```

## Performance Metrics

The framework computes these metrics automatically after backtests:

| Metric | Description |
|--------|-------------|
| Net Profit % | Total return as percentage |
| Sharpe Ratio | Risk-adjusted return (annualized) |
| Calmar Ratio | Return / Max Drawdown |
| Sortino Ratio | Downside risk-adjusted return |
| Omega Ratio | Probability-weighted gains vs losses |
| Max Drawdown | Largest peak-to-trough decline |
| Win Rate | Percentage of winning trades |
| Profit Factor | Gross profit / Gross loss |
| Total Trades | Number of completed trades |
| Annual Return | Annualized rate of return |

## Adding a New Exchange Driver

To add candle import support for a new exchange:

1. Create a directory under `src/jesse/modes/import_candles_mode/drivers/NewExchange/`
2. Implement the driver interface:

```python
from jesse.modes.import_candles_mode.drivers.interface import CandleExchangeInterface

class NewExchangeSpot(CandleExchangeInterface):
    def get_starting_time(self, symbol: str) -> int:
        """Return the earliest available timestamp for this symbol."""
        pass

    def fetch(self, symbol: str, start_timestamp: int, timeframe: str = '1m') -> list:
        """Fetch candles and return as list of [timestamp, open, close, high, low, volume]."""
        pass
```

3. Register the driver in the exchange configuration.

## Common Pitfalls

1. **Lookback bias**: Do not use the current candle's close in `should_long()`/`should_short()`. Use `self.candles[:-1]` to exclude the forming candle.

2. **Order format**: Always use tuple notation `self.buy = qty, price`. Separate assignments will not work.

3. **Position sizing**: Use `utils.size_to_qty()` or `utils.risk_to_qty()` instead of manual calculations to handle precision correctly.

4. **Indicator warmup**: Ensure enough warmup candles are configured (default 240). A 200-period EMA needs at least 200 candles before producing valid output.

5. **Mutable state**: Do not store mutable state as instance variables that persist across trades. Use `self.vars` dict, which is shared across the store, or reset variables in `on_open_position()`.

6. **Multiple routes**: Be aware that all routes share the global store. Name your `store.vars` keys carefully to avoid collisions.

## Code Style

- Follow PEP 8
- Use type hints where applicable
- Prefer NumPy vectorized operations over Python loops
- Cache expensive computations with `@cached` decorator
- Keep strategy methods focused and single-purpose
- Use conventional commit messages

## Configuration Reference

Jesse's configuration is defined in `src/jesse/config.py` and environment variables from `.env`. The runtime configuration is a nested dictionary modified based on the active mode (backtest, live, optimize).

### Environment Variables (`.env`)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `APP_PORT` | int | `9000` | Port for the FastAPI web dashboard |
| `APP_HOST` | str | `0.0.0.0` | Host address for the web server |
| `APP_PASSWORD` | str | _(required)_ | Password for web dashboard authentication |
| `POSTGRES_HOST` | str | `localhost` | PostgreSQL server hostname |
| `POSTGRES_PORT` | int | `5432` | PostgreSQL server port |
| `POSTGRES_DB` | str | `jesse` | PostgreSQL database name |
| `POSTGRES_USER` | str | `jesse` | PostgreSQL username |
| `POSTGRES_PASSWORD` | str | `jesse` | PostgreSQL password |
| `REDIS_HOST` | str | `localhost` | Redis server hostname |
| `REDIS_PORT` | int | `6379` | Redis server port |

### Exchange Configuration (`config['env']['exchanges']`)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fee` | float | `0` (Sandbox) | Trading fee as a decimal (e.g., `0.001` for 0.1%) |
| `type` | str | `"futures"` | Exchange type: `"futures"` or `"spot"` |
| `futures_leverage_mode` | str | `"cross"` | Leverage mode: `"cross"` or `"isolated"` |
| `futures_leverage` | int | `1` | Leverage multiplier (1, 2, 10, 50, etc.) |
| `balance` | float | `10000` | Starting balance in quote currency |

### Optimization Configuration (`config['env']['optimization']`)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `objective_function` | str | `"sharpe"` | Fitness metric: `sharpe`, `calmar`, `sortino`, `omega`, `serenity`, `smart sharpe`, `smart sortino` |
| `trials` | int | `200` | Number of Optuna trials per hyperparameter |
| `best_candidates_count` | int | `20` | Number of top results to display |

### Data Configuration (`config['env']['data']`)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `warmup_candles_num` | int | `240` | Number of warmup candles loaded before session start |
| `generate_candles_from_1m` | bool | `False` | Generate higher timeframe candles from 1-minute data |
| `persistency` | bool | `True` | Persist state to database during live trading |

### Logging Configuration (`config['env']['logging']`)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strategy_execution` | bool | `True` | Log strategy execution events |
| `order_submission` | bool | `True` | Log order submission events |
| `order_cancellation` | bool | `True` | Log order cancellation events |
| `order_execution` | bool | `True` | Log order execution events |
| `position_opened` | bool | `True` | Log position open events |
| `position_increased` | bool | `True` | Log position increase events |
| `position_reduced` | bool | `True` | Log position reduction events |
| `position_closed` | bool | `True` | Log position close events |
| `shorter_period_candles` | bool | `False` | Log shorter period candle generation |
| `trading_candles` | bool | `True` | Log trading candle events |
| `balance_update` | bool | `True` | Log balance update events |

### Caching Configuration (`config['env']['caching']`)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `driver` | str | `"pickle"` | Cache driver: `"pickle"` |

## Troubleshooting

### 1. `psycopg2.OperationalError: could not connect to server`
**Cause**: PostgreSQL is not running or connection parameters are wrong.
**Solution**: Verify PostgreSQL is running (`pg_isready`), check `.env` values for `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`. Create the database if needed: `createdb jesse`.

### 2. `redis.exceptions.ConnectionError: Error connecting to localhost:6379`
**Cause**: Redis server is not running.
**Solution**: Start Redis with `redis-server` or `systemctl start redis`. Verify with `redis-cli ping`.

### 3. `ValueError: Strategy class not found`
**Cause**: Strategy directory structure is wrong or `__init__.py` does not export the class.
**Solution**: Ensure your strategy is at `strategies/MyStrategy/__init__.py` and the class name matches the directory name exactly (case-sensitive).

### 4. `IndexError: index out of bounds` in indicators
**Cause**: Insufficient warmup candles for the indicator period used.
**Solution**: Increase `warmup_candles_num` in the backtest configuration. A 200-period EMA needs at least 200 warmup candles (default is 240).

### 5. `TypeError: 'NoneType' object is not iterable` in `go_long()`
**Cause**: Forgetting to use tuple notation for order assignment.
**Solution**: Use `self.buy = qty, price` (tuple), not separate `self.buy_qty = qty; self.buy_price = price`.

### 6. Backtest shows zero trades
**Cause**: `should_long()` / `should_short()` never returns `True`, or filters block all entries.
**Solution**: Check indicator logic, ensure candles have enough data, temporarily remove filters to isolate the issue. Enable debug logging.

### 7. `ray.exceptions.RayTaskError` during optimization
**Cause**: Ray workers fail due to memory or serialization issues.
**Solution**: Reduce the number of concurrent trials, ensure strategy code is serializable (no lambda functions or open file handles in strategy class).

### 8. Web dashboard returns 401 Unauthorized
**Cause**: `APP_PASSWORD` in `.env` does not match what you entered in the browser.
**Solution**: Check `.env` file, restart the server after changes.

### 9. `ModuleNotFoundError: No module named 'jesse_live'`
**Cause**: The optional live trading plugin is not installed.
**Solution**: Run `jesse install-live` to install the live trading extension. This is only required for live/paper trading, not backtesting.

### 10. Candle import hangs or times out
**Cause**: Exchange API rate limits or network issues.
**Solution**: Use smaller date ranges, check network connectivity, verify the exchange and symbol are supported (see `jesse/info.py` for the full list).

## Security Considerations

### API Key Management
- **Never hardcode API keys** in strategy files or configuration. Use environment variables or the `.env` file.
- The `.env` file should be excluded from version control (add to `.gitignore`).
- Jesse stores exchange credentials for live trading; ensure the machine running Jesse has restricted access.

### Credential Storage
- Database credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`) are stored in plaintext in `.env`. On production servers, use environment variables set by your deployment system instead.
- The `APP_PASSWORD` for the web dashboard is transmitted in HTTP; use HTTPS (reverse proxy with TLS) for remote access.
- Redis connections are unauthenticated by default. Configure Redis `requirepass` if the server is network-accessible.

### Network Security
- The web dashboard binds to `0.0.0.0` by default, exposing it on all interfaces. Restrict to `127.0.0.1` in `.env` if only local access is needed.
- Use a firewall to restrict access to ports 9000 (dashboard), 5432 (PostgreSQL), and 6379 (Redis).
- For live trading, ensure WebSocket connections to exchanges use TLS (handled by exchange libraries).

### Safe Practices
- Run backtests and live trading under a dedicated OS user with minimal privileges.
- Use read-only API keys for data import operations; only enable trading permissions for live trading keys.
- Review strategy code for unintended side effects (file system access, network calls) before deploying to production.
- Enable authentication on PostgreSQL and Redis in production environments.
- Regularly rotate API keys and database passwords.

---
## See Also
- [README](README.md) — Project overview and quick start
- [Architecture](architecture.md) — System design and components
- [Workflow](workflow.md) — Event flows and processing pipelines
- [State Management](state-management.md) — State lifecycle and data models
