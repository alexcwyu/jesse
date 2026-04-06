# Jesse -- Workflows

## Strategy Development Workflow

```mermaid
flowchart TD
    A[Create Strategy] --> B[Define Entry/Exit Logic]
    B --> C[Import Historical Candles]
    C --> D[Backtest Strategy]
    D --> E{Results Acceptable?}
    E -->|No| F[Adjust Logic / Parameters]
    F --> D
    E -->|Yes| G[Optimize Hyperparameters]
    G --> H[Monte Carlo Validation]
    H --> I{Robust?}
    I -->|No| F
    I -->|Yes| J[Paper Trade]
    J --> K{Validated?}
    K -->|No| F
    K -->|Yes| L[Deploy Live]
```

## Backtesting Workflow

### Data Flow

```mermaid
sequenceDiagram
    participant Dashboard
    participant Controller as Backtest Controller
    participant BacktestMode
    participant Store as Global Store
    participant Strategy
    participant Broker
    participant Exchange as Sandbox Exchange
    participant DB as PostgreSQL

    Dashboard->>Controller: POST /backtest (routes, dates, config)
    Controller->>BacktestMode: run(client_id, routes, dates, ...)
    BacktestMode->>DB: Load 1m candles for date range
    BacktestMode->>Store: Initialize state (exchanges, positions, candles)
    BacktestMode->>Strategy: Instantiate per route

    loop For each 1-minute candle
        BacktestMode->>Store: Update candle state
        BacktestMode->>Strategy: Generate higher-TF candles
        
        alt New trading-timeframe candle
            Strategy->>Strategy: before()
            
            alt No open position
                Strategy->>Strategy: should_long() / should_short()
                alt Signal triggered
                    Strategy->>Strategy: go_long() / go_short()
                    Strategy->>Broker: Submit entry + SL/TP orders
                    Broker->>Exchange: Place orders
                end
            else Position open
                Strategy->>Strategy: update_position()
            end
            
            Strategy->>Strategy: after()
        end
        
        BacktestMode->>Exchange: Check pending orders against price
        
        alt Order filled
            Exchange->>Store: Update position state
            Strategy->>Strategy: on_open/close/increased/reduced_position()
        end
    end

    BacktestMode->>BacktestMode: Calculate metrics
    BacktestMode->>DB: Store BacktestSession + ClosedTrades
    BacktestMode->>Dashboard: Publish results via Redis
```

### Strategy Lifecycle per Candle

```mermaid
stateDiagram-v2
    [*] --> before: New candle arrives

    before --> CheckPosition: before() executed
    
    CheckPosition --> EvaluateSignals: No open position
    CheckPosition --> UpdatePosition: Position is open
    
    EvaluateSignals --> should_long: Check long signal
    should_long --> go_long: Returns True
    should_long --> should_short: Returns False
    should_short --> go_short: Returns True
    should_short --> after: Returns False
    
    go_long --> SubmitOrders: Set buy/stop_loss/take_profit
    go_short --> SubmitOrders: Set sell/stop_loss/take_profit
    SubmitOrders --> after
    
    UpdatePosition --> after: update_position() called

    after --> [*]: after() executed
```

## Optimization Workflow

```mermaid
sequenceDiagram
    participant Dashboard
    participant Controller as Optimization Controller
    participant Optimizer
    participant Optuna
    participant Ray as Ray Cluster
    participant Fitness as Fitness Function

    Dashboard->>Controller: POST /optimization (config, routes, dates)
    Controller->>Optimizer: Initialize(session_id, config, candles)
    Optimizer->>Optuna: Create Study
    Optimizer->>Ray: Initialize cluster (N CPUs)

    loop For each trial batch
        Optuna->>Optimizer: Suggest hyperparameter set
        Optimizer->>Ray: Submit ray_evaluate_trial.remote()
        
        par Parallel execution
            Ray->>Fitness: get_fitness(hp, training_candles)
            Fitness->>Fitness: Run backtest with training data
            Fitness->>Fitness: Run backtest with testing data
            Fitness-->>Ray: (score, training_metrics, testing_metrics)
        end
        
        Ray-->>Optimizer: Collect results
        Optimizer->>Optuna: Report trial results
        Optimizer->>Dashboard: Publish progress via Redis
    end

    Optimizer->>Dashboard: Publish best candidates
```

## Monte Carlo Workflow

```mermaid
sequenceDiagram
    participant Dashboard
    participant Runner as MonteCarloRunner
    participant Ray as Ray Cluster
    participant TradesSim as Trades Simulation
    participant CandlesSim as Candles Simulation
    participant DB as PostgreSQL

    Dashboard->>Runner: Start simulation (config, scenarios)
    Runner->>Ray: Initialize cluster

    alt Trades Simulation
        Runner->>TradesSim: Run N scenarios
        loop Each scenario (parallel via Ray)
            TradesSim->>TradesSim: Reshuffle trade order
            TradesSim->>TradesSim: Recalculate equity curve
            TradesSim->>TradesSim: Compute metrics
        end
        TradesSim-->>Runner: Confidence intervals (5th/50th/95th percentiles)
    end

    alt Candles Simulation
        Runner->>CandlesSim: Run N scenarios
        loop Each scenario (parallel via Ray)
            CandlesSim->>CandlesSim: Perturb candles (Gaussian / Bootstrap)
            CandlesSim->>CandlesSim: Run full backtest on perturbed data
            CandlesSim->>CandlesSim: Compute metrics
        end
        CandlesSim-->>Runner: Distribution of outcomes
    end

    Runner->>DB: Store session results
    Runner->>Dashboard: Publish summary via Redis
```

## Live Trading Workflow

Live trading (requires `jesse-live` plugin) follows the same strategy lifecycle as backtesting but with real exchange connections:

```mermaid
flowchart TD
    A[Start Live Session] --> B[Connect to Exchange WebSocket]
    B --> C[Subscribe to Market Data]
    C --> D[Receive Real-time Candles]
    D --> E[Execute Strategy Logic]
    E --> F{Order Signal?}
    F -->|Yes| G[Submit Order to Exchange]
    G --> H[Monitor Order Status]
    H --> I[Update Position State]
    I --> D
    F -->|No| D
    
    D --> J[Notification Service]
    J --> K[Telegram / Slack / Discord]
```

## Candle Import Workflow

```mermaid
flowchart LR
    A[Select Exchange] --> B[Select Symbol + Date Range]
    B --> C[Exchange Driver]
    C --> D[Fetch Candles via REST API]
    D --> E[Normalize to Standard Format]
    E --> F[Store in PostgreSQL]
    F --> G[Available for Backtesting]
```

Each exchange has a dedicated driver (e.g., `BinancePerpetualFutures`, `BybitUSDTPerpetual`) that handles API pagination, rate limiting, and data format normalization. All candles are stored as 1-minute OHLCV records.

## Multi-Route Trading

Jesse supports trading multiple symbols and timeframes simultaneously within a single session:

```python
# Trading routes
routes = [
    {'exchange': 'Binance', 'symbol': 'BTC-USDT', 'timeframe': '1h', 'strategy': 'TrendFollower'},
    {'exchange': 'Binance', 'symbol': 'ETH-USDT', 'timeframe': '4h', 'strategy': 'MeanReversion'},
]

# Data-only routes (for cross-symbol analysis)
data_routes = [
    {'exchange': 'Binance', 'symbol': 'BTC-USDT', 'timeframe': '15m'},
]
```

Strategies on different routes share the global `store`, enabling cross-symbol and cross-timeframe analysis. A strategy on ETH-USDT can read BTC-USDT candles from the store to make correlated decisions.

---
## See Also
- [README](README.md) — Project overview and quick start
- [Architecture](architecture.md) — System design and components
- [State Management](state-management.md) — State lifecycle and data models
- [Development](development.md) — Development guide and best practices
