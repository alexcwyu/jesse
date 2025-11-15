# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Jesse is an advanced crypto trading framework for researching, backtesting, optimizing, and live trading cryptocurrency strategies. The framework emphasizes simplicity with powerful features including 100+ technical indicators, multi-symbol/timeframe trading, hyperparameter optimization, and a built-in web dashboard.

**Version**: 1.11.0
**Language**: Python 3.10+
**Dependencies**: NumPy, Pandas, FastAPI, PostgreSQL (via Peewee ORM), Redis, Ray (for optimization)

## Installation & Setup

```bash
# Install in development mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt

# Run the web application (starts FastAPI server on port 9000)
python -m jesse run

# Install live trading plugin (optional)
jesse install-live
```

**Prerequisites**:
- Python 3.10+ (setup.py specifies `python_requires='>=3.10'`)
- PostgreSQL database (for storing candles, trades, sessions)
- Redis (for inter-process communication and pub/sub)

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_backtest.py

# Run specific test by name
pytest -k test_order_submission

# Run with coverage
pytest --cov=jesse

# Run specific test modules
pytest tests/test_strategy.py
pytest tests/test_indicators.py
```

**Test Structure**:
- 30+ test files in `/tests/` directory
- 137+ test strategy implementations in `jesse/strategies/` (Test01, Test02, etc.)
- Testing utilities in `jesse/testing_utils.py`
- Test factories in `jesse/factories.py`

## Key Commands

### CLI Commands

Jesse uses Click for CLI. The main entry point is `jesse` command (defined in `jesse/__init__.py:cli`):

```bash
# Start the web application
jesse run

# Install live trading plugin
jesse install-live [--strict/--no-strict]

# Check version
jesse --version
```

**Note**: Most operations (backtesting, optimization, strategy creation) are performed through the web dashboard at `http://localhost:9000` rather than CLI commands.

### Web Dashboard

The web dashboard (FastAPI-based) provides:
- Strategy creation and editing (built-in code editor)
- Backtesting interface with charts
- Hyperparameter optimization
- Candle data import/management
- Live trading control (requires jesse-live plugin)
- Real-time monitoring via WebSocket

Access at: `http://localhost:9000` (default)

## Architecture Overview

### High-Level Architecture

Jesse follows a **strategy-centric, event-driven architecture** with centralized state management:

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Dashboard (FastAPI)                   │
│         Routes: /backtest, /optimize, /strategies, etc.      │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                   Controllers Layer                          │
│  backtest, optimization, strategy, exchange, candles, etc.   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    Modes & Services                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Backtest    │  │  Optimize    │  │ Import       │      │
│  │  Mode        │  │  Mode (Ray)  │  │ Candles      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  Services: broker, candle, metrics, notifier, logger, api   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│               Strategy Layer (User Code)                     │
│  Base Strategy class with lifecycle hooks:                   │
│  • should_long/should_short - Entry signals                  │
│  • go_long/go_short - Position entry                         │
│  • on_open/close/increased/reduced_position - Events         │
│  • update_position - Continuous management                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              State Management (store)                        │
│  CandlesState, OrdersState, PositionsState, ExchangesState   │
│  ClosedTrades, TickersState, TradesState, OrderbookState     │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│           Database & Storage (PostgreSQL)                    │
│  Models: Candle, Order, Position, BacktestSession,           │
│          OptimizationSession, ClosedTrade                    │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

**1. Strategy Layer** (`jesse/strategies/Strategy.py` - 1485 lines)
- Base class for all trading strategies
- **Lifecycle hooks**:
  - `should_long()` / `should_short()` - Entry signal evaluation
  - `go_long()` / `go_short()` - Position entry execution
  - `on_open_position()`, `on_close_position()` - Position lifecycle
  - `on_increased_position()`, `on_reduced_position()` - Position size changes
  - `before()` / `after()` - Pre/post candle hooks
  - `update_position()` - Called on every candle when position is open
- **Built-in properties**: `price`, `candles`, `position`, `balance`, `leverage`, `broker`
- **Order management**: `buy`, `sell`, `stop_loss`, `take_profit`
- **Indicators**: Access to 100+ indicators via `ta` module
- **Caching**: LRU cache decorators for performance (`@cached`)
- **Chart support**: Line charts and horizontal lines for visualization

**2. Backtesting Engine** (`jesse/modes/backtest_mode.py` - 46k lines)
- Event-driven candle simulation
- Generates candles from 1-minute data (supports 1m, 3m, 5m, 15m, 30m, 45m, 1h, 2h, 3h, 4h, 6h, 8h, 12h, 1D, 3D, 1W)
- Order execution simulation (market, limit, stop orders)
- Realistic order matching with slippage
- Multi-route support (multiple symbols/timeframes simultaneously)
- Performance metrics calculation (Sharpe, Calmar, Sortino, max drawdown, etc.)
- Debug mode with detailed logging
- Chart generation in TradingView format
- Persists results to database (`BacktestSession`, `ClosedTrade`)

**3. Optimization Engine** (`jesse/modes/optimize_mode/Optimize.py`)
- **Distributed optimization** using Ray (parallel execution across CPU cores)
- **Optuna-based** hyperparameter optimization
- **Fitness functions**: Sharpe, Calmar, Sortino, Omega, Serenity ratios
- **Cross-validation**: Training/testing data splits
- **Session tracking**: Stores trials in PostgreSQL (`OptimizationSession`)
- Define hyperparameters in strategy:
  ```python
  def hyperparameters(self):
      return [
          {'name': 'ema_period', 'type': int, 'min': 10, 'max': 200, 'default': 50},
          {'name': 'stop_loss_pct', 'type': float, 'min': 0.01, 'max': 0.1, 'default': 0.05}
      ]
  ```

**4. State Management** (`jesse/store/__init__.py`)
- **Global store object** accessible throughout the application
- **State managers**:
  - `CandlesState` - OHLCV data (NumPy arrays)
  - `OrdersState` - Active orders tracking
  - `PositionsState` - Open positions per route
  - `ClosedTrades` - Completed trades history
  - `ExchangesState` - Exchange instances (futures/spot)
  - `TickersState`, `TradesState`, `OrderbookState` - Market data
- **Reset utilities** for testing and new sessions

**5. Broker Service** (`jesse/services/broker.py`)
- Abstracts order placement and management
- **Smart order routing**: Automatically selects market/limit/stop based on price relationships
- **Order methods**:
  - `buy_at(qty, price)`, `sell_at(qty, price)`
  - `buy_at_market(qty)`, `sell_at_market(qty)`
  - `start_profit_at(side, qty, price)` - Take profit orders
  - `reduce_position_at(qty, price)` - Partial exits
- Handles order submission, cancellation, and execution
- Used internally by Strategy class

**6. Database Models** (`jesse/models/`)
- **Peewee ORM** with PostgreSQL backend
- **Key models**:
  - `Candle` - Historical OHLCV data
  - `Order` - Order history
  - `Position` - Position management
  - `ClosedTrade` - Completed trade records
  - `BacktestSession` - Backtest metadata and results
  - `OptimizationSession` - Optimization trials
  - `FuturesExchange`, `SpotExchange` - Exchange configurations
- **Migrations**: Managed in `jesse/services/migrator.py`

**7. Services** (`jesse/services/`)
- `candle.py` - Candle generation and timeframe aggregation
- `metrics.py` - Performance metrics (Sharpe, Sortino, drawdown, win rate, etc.)
- `api.py` - Exchange driver management
- `broker.py` - Order placement abstraction
- `notifier.py` - Notifications (Telegram, Slack, Discord)
- `logger.py` - Structured logging
- `charts.py` - Chart data generation for web dashboard
- `cache.py` - Caching utilities
- `db.py` - Database connection management
- `multiprocessing.py` - Process manager for background tasks

**8. Indicators** (`jesse/indicators/`)
- 100+ technical indicators (EMA, SMA, RSI, MACD, Bollinger Bands, etc.)
- NumPy-optimized for performance
- Numba JIT compilation where applicable
- Access via `ta` module in strategies:
  ```python
  ema = ta.ema(self.candles, period=20)
  rsi = ta.rsi(self.candles, period=14)
  bb = ta.bollinger_bands(self.candles, period=20, devup=2, devdn=2)
  ```

**9. Exchange Support** (`jesse/exchanges/`)
- Sandbox exchange for testing/backtesting
- Live trading via optional `jesse-live` plugin
- Supports 20+ exchanges: Binance, Bybit, Bitget, Gate.io, Hyperliquid, etc.
- Exchange types: futures, spot, perpetual
- Unified driver interface (`jesse/services/api.py`)

### Route-Based Configuration

Trading is configured through **routes** that specify:
- Exchange (e.g., 'Binance', 'Bybit', 'Sandbox')
- Symbol (e.g., 'BTC-USDT', 'ETH-USDT')
- Timeframe (e.g., '1h', '4h', '1D')
- Strategy class name

**Example route configuration**:
```python
routes = [
    {'exchange': 'Binance', 'symbol': 'BTC-USDT', 'timeframe': '1h', 'strategy': 'MyStrategy'}
]

# Multiple routes for multi-symbol/timeframe trading
routes = [
    {'exchange': 'Binance', 'symbol': 'BTC-USDT', 'timeframe': '1h', 'strategy': 'TrendStrategy'},
    {'exchange': 'Binance', 'symbol': 'ETH-USDT', 'timeframe': '4h', 'strategy': 'MeanReversionStrategy'}
]

# Data routes for additional data sources (non-trading)
data_routes = [
    {'exchange': 'Binance', 'symbol': 'BTC-USDT', 'timeframe': '15m'}  # For lower timeframe indicators
]
```

Routes are configured via `jesse/routes/__init__.py` or through the web dashboard.

## Strategy Development

### Creating a Strategy

1. **Generate strategy** via web dashboard or create directory manually:
   ```
   strategies/
   └── MyStrategy/
       └── __init__.py
   ```

2. **Implement strategy class**:
   ```python
   from jesse.strategies import Strategy
   import jesse.indicators as ta
   from jesse import utils

   class MyStrategy(Strategy):
       def should_long(self) -> bool:
           # Entry signal for long position
           ema_short = ta.ema(self.candles, 20)
           ema_long = ta.ema(self.candles, 50)
           return ema_short > ema_long

       def should_short(self) -> bool:
           # Entry signal for short position
           ema_short = ta.ema(self.candles, 20)
           ema_long = ta.ema(self.candles, 50)
           return ema_short < ema_long

       def go_long(self):
           # Execute long entry
           qty = utils.size_to_qty(self.balance * 0.05, self.price)  # Risk 5% of capital
           self.buy = qty, self.price
           self.take_profit = qty, self.price * 1.2  # 20% profit target
           self.stop_loss = qty, self.price * 0.95   # 5% stop loss

       def go_short(self):
           # Execute short entry
           qty = utils.size_to_qty(self.balance * 0.05, self.price)
           self.sell = qty, self.price
           self.take_profit = qty, self.price * 0.8
           self.stop_loss = qty, self.price * 1.05

       def update_position(self):
           # Called on every candle when position is open
           # Use for trailing stops, position management, etc.
           pass
   ```

### Strategy Lifecycle

The framework calls strategy methods in this order:

1. **Initialization**: Strategy instance created for each route
2. **On each candle**:
   - `before()` - Pre-candle hook
   - `should_long()` / `should_short()` - Evaluated if no position
   - `go_long()` / `go_short()` - Called if should_long/short returns True
   - `on_open_position()` - Triggered when position opens
   - `update_position()` - Called every candle when position is open
   - `on_increased_position()` / `on_reduced_position()` - Size changes
   - `on_close_position()` - Triggered when position closes
   - `after()` - Post-candle hook

### Key Conventions

- **Candle data format**: NumPy arrays with shape `(n, 6)` containing `[timestamp, open, close, high, low, volume]`
- **Price references**: All prices in quote currency (e.g., USDT for BTC-USDT)
- **Quantity references**: All quantities in base currency (e.g., BTC for BTC-USDT)
- **Order format**: `self.buy = qty, price` or `self.buy = [(qty1, price1), (qty2, price2)]` for multiple orders
- **Position access**: `self.position.qty`, `self.position.entry_price`, `self.position.pnl`, `self.position.is_open`
- **Indicator usage**: Always pass `self.candles` to indicator functions
- **Caching**: Use `@property` with `@cached` decorator for expensive computations
- **Hyperparameters**: Access via `self.hp['param_name']` after defining in `hyperparameters()` method
- **Filters**: Return `True` to allow trade, `False` to block (optional `filters()` method)

### Advanced Features

**Multi-Route Broadcasting**:
```python
# Share data between routes (symbols/timeframes)
from jesse import store

def should_long(self):
    # Access data from another route
    btc_candles = store.candles.get_candles('Binance', 'BTC-USDT', '1h')
    eth_candles = store.candles.get_candles('Binance', 'ETH-USDT', '1h')
    # Compare BTC and ETH trends
    return some_correlation_logic(btc_candles, eth_candles)
```

**Partial Fills** (scaling in/out):
```python
def go_long(self):
    qty = utils.size_to_qty(self.balance * 0.05, self.price)
    # Enter with multiple orders
    self.buy = [
        (qty * 0.5, self.price - 10),      # 50% at lower price
        (qty * 0.5, self.price)             # 50% at current price
    ]

def update_position(self):
    # Scale out at profit targets
    if self.position.pnl_percentage > 10:
        self.liquidate(0.5)  # Close 50% of position
```

**Custom Indicators**:
```python
@property
@cached
def custom_indicator(self):
    # Define custom indicator using NumPy
    highs = self.candles[:, 3]
    lows = self.candles[:, 4]
    return (highs + lows) / 2
```

**Chart Visualization**:
```python
def before(self):
    # Add indicators to chart
    if self.index > 200:
        self.chart.plot('EMA20', ta.ema(self.candles, 20)[-1])
        self.chart.plot_shape('Entry', self.price, 'triangle-up', 'green')
```

## File Structure

```
jesse/
├── __init__.py              # FastAPI app, CLI commands, route registration
├── config.py                # Framework configuration (exchanges, optimization, logging)
├── constants.py             # Constants (timeframes, order types, etc.)
├── helpers.py               # Utility functions (color output, date parsing, price formatting)
├── utils.py                 # Trading utilities (size_to_qty, risk_to_qty, etc.)
├── info.py                  # Exchange information and metadata
├── version.py               # Version string
├── testing_utils.py         # Test helper functions
├── math_utils.py            # Mathematical utilities
├── controllers/             # FastAPI route controllers
│   ├── backtest_controller.py
│   ├── optimization_controller.py
│   ├── strategy_controller.py
│   ├── exchange_controller.py
│   ├── candles_controller.py
│   └── ...
├── enums/                   # Enumerations
│   └── __init__.py          # Timeframes, order types, exchanges, trade types, etc.
├── exceptions/              # Custom exceptions
├── exchanges/               # Exchange implementations
│   ├── Sandbox/             # Sandbox exchange for testing
│   └── ...
├── factories/               # Test data factories
├── indicators/              # 100+ technical indicators (EMA, SMA, RSI, MACD, etc.)
├── libs/                    # Third-party libraries and wrappers
├── models/                  # Peewee ORM models
│   ├── Candle.py
│   ├── Order.py
│   ├── Position.py
│   ├── ClosedTrade.py
│   ├── BacktestSession.py
│   ├── OptimizationSession.py
│   ├── FuturesExchange.py
│   ├── SpotExchange.py
│   └── ...
├── modes/                   # Trading modes
│   ├── backtest_mode.py     # Backtesting engine (46k lines)
│   ├── optimize_mode/       # Optimization engine (Ray + Optuna)
│   ├── import_candles_mode/ # Candle import from exchanges
│   └── data_provider.py     # Configuration data provider
├── research/                # Research utilities (backtesting, Monte Carlo)
├── routes/                  # Route configuration
│   └── __init__.py          # Define routes and data routes
├── services/                # Core services
│   ├── api.py               # Exchange driver management
│   ├── broker.py            # Order placement abstraction
│   ├── candle.py            # Candle generation and aggregation
│   ├── metrics.py           # Performance metrics
│   ├── notifier.py          # Notifications (Telegram, Slack, Discord)
│   ├── logger.py            # Structured logging
│   ├── charts.py            # Chart data generation
│   ├── cache.py             # Caching utilities
│   ├── db.py                # Database connection
│   ├── migrator.py          # Database migrations
│   ├── multiprocessing.py   # Process manager
│   ├── redis.py             # Redis client and pub/sub
│   ├── web.py               # Web utilities and request models
│   ├── ws_manager.py        # WebSocket connection manager
│   ├── auth.py              # Authentication
│   └── ...
├── static/                  # Frontend assets (web dashboard)
├── store/                   # State management
│   └── __init__.py          # Global store with state managers
└── strategies/              # User strategies + test strategies
    ├── Strategy.py          # Base strategy class (1485 lines)
    ├── Test01/              # Test strategies (137+)
    ├── Test02/
    └── ...

tests/                       # Test suite
├── test_backtest.py
├── test_strategy.py
├── test_broker.py
├── test_indicators.py
├── test_position.py
├── test_order.py
├── test_helpers.py
├── test_metrics.py
└── ...

setup.py                     # Package setup
requirements.txt             # Dependencies
README.md                    # Documentation
```

## Important Development Notes

### Candle Data Structure

All candle data in Jesse uses NumPy arrays with shape `(n, 6)`:
```python
# Column indices (use helpers for readability)
candles[:, 0]  # timestamp (milliseconds)
candles[:, 1]  # open
candles[:, 2]  # close
candles[:, 3]  # high
candles[:, 4]  # low
candles[:, 5]  # volume

# Access in strategies
current_close = self.candles[-1, 2]    # Latest close price
previous_open = self.candles[-2, 1]    # Previous candle open
highs = self.candles[:, 3]             # All highs as array
```

### State Access

Access global state via `store`:
```python
from jesse import store

# Get candles for any route
candles = store.candles.get_candles(exchange, symbol, timeframe)

# Get current position
position = store.positions.get_position(exchange, symbol)

# Get exchange instance
exchange = store.exchanges.get_exchange(exchange_name)

# Access orders
orders = store.orders.get_orders(exchange, symbol)
```

### Configuration

Framework configuration is in `jesse/config.py`:
- `config['env']['exchanges']` - Exchange settings (fee, leverage, balance)
- `config['env']['logging']` - Logging toggles
- `config['env']['optimization']` - Optimization settings
- `config['env']['caching']` - Cache driver selection

Configuration is modified at runtime based on mode (backtest, live, optimize) and user settings via web dashboard.

### Performance Considerations

1. **Use NumPy operations** instead of loops for candle data manipulation
2. **Cache expensive computations** with `@cached` or `@lru_cache`
3. **Minimize indicator recalculation** by using `@property` decorators
4. **Use Numba JIT** for custom numerical functions (see `jesse/indicators/` for examples)
5. **Avoid lookback bias** - only use `self.candles[:-1]` or earlier in calculations
6. **Leverage Ray** for parallel optimization trials

### Common Pitfalls

- **Lookback bias**: Don't use current candle close in `should_long/should_short` (use `self.candles[:-1]` to exclude current)
- **Order format**: Always use `(qty, price)` tuples, not separate assignments
- **Position size**: Use `utils.size_to_qty()` or `utils.risk_to_qty()` to calculate quantities correctly
- **Indicator warmup**: Indicators need warmup period (e.g., 200 candles for 200-period EMA)
- **State persistence**: Don't store mutable state as instance variables (use `self.vars` dict if needed)
- **Multiple routes**: Be careful with shared state when trading multiple symbols simultaneously

### Database

Jesse requires PostgreSQL for storing:
- Historical candle data (`Candle` model)
- Backtest sessions and results (`BacktestSession`, `ClosedTrade`)
- Optimization trials (`OptimizationSession`)
- Exchange configurations (`FuturesExchange`, `SpotExchange`)

Database migrations are run automatically on `jesse run` via `jesse/services/migrator.py`.

## Resources

- **Documentation**: https://docs.jesse.trade
- **Website**: https://jesse.trade
- **YouTube**: https://jesse.trade/youtube (screencast tutorials)
- **Discord**: https://jesse.trade/discord
- **Help Center**: https://jesse.trade/help
- **JesseGPT**: https://jesse.trade/gpt (AI assistant for strategy development)
- **GitHub**: https://github.com/jesse-ai/jesse

## Live Trading

Live trading requires the optional `jesse-live` plugin:
```bash
jesse install-live
```

This adds:
- Real exchange connectivity (Binance, Bybit, Bitget, etc.)
- Paper trading mode
- WebSocket market data streaming
- Order execution on live exchanges
- Real-time notifications
- Additional controllers and endpoints (`jesse/controllers/live_controller.py`)

The plugin integrates seamlessly with the web dashboard and uses the same strategy code as backtesting.

## Development Workflow

1. **Create strategy** via web dashboard or manually in `strategies/YourStrategy/`
2. **Define entry/exit logic** in `should_long/short()` and `go_long/short()`
3. **Import candles** via web dashboard for backtesting
4. **Backtest** strategy using web interface
5. **Analyze results** (metrics, charts, trade log)
6. **Optimize** hyperparameters if needed (define in `hyperparameters()` method)
7. **Iterate** on strategy logic based on results
8. **Paper trade** to validate in near-real-time conditions (requires jesse-live)
9. **Deploy live** when confident (requires jesse-live and exchange API keys)

## Code Style

- Follow PEP 8 style guide
- Use type hints where applicable (gradually typed codebase)
- Document complex logic with comments
- Use descriptive variable names
- Keep strategy methods focused and single-purpose
- Prefer NumPy operations over Python loops
- Use `jesse.helpers` for common utilities (color output, date parsing, etc.)
