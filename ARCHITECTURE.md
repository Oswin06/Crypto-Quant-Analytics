# System Architecture

## Overview

The Quant Analytics system is designed as a modular, scalable platform for real-time trading data ingestion, storage, analytics computation, and interactive visualization.

## Architecture Diagram Description

```
┌─────────────────────────────────────────────────────────────────┐
│                        STREAMLIT FRONTEND                       │
│                     (Interactive Dashboard)                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │Price Charts│  │  Analytics │  │Statistics │  │ Settings│ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND (REST)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Data API    │  │  Analytics │  │   Alerts   │            │
│  │  Endpoints │  │   Endpoints │  │  Endpoints │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                      ANALYTICS ENGINE                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Stats   │  │ Z-Score  │  │   ADF    │  │ Hedge    │      │
│  │Computing│  │ Computing│  │   Test   │  │  Ratio   │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Correlation│  │  Spread  │  │  Volume  │  │ Bollinger│      │
│  │ Computing │  │ Computing│  │  Profile │  │  Bands   │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                       DATA PROCESSING                            │
│  ┌──────────────┐         ┌────────────────────────────────┐ │
│  │  Resampler   │─────────→│     SQLite Database            │ │
│  │              │  Store   │                                │ │
│  │ (1s, 1m, 5m) │─────────│  - Ticks Table              │ │
│  │              │  Retrieve│  - OHLC Table                 │ │
│  └──────────────┘         └────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    WEBSOCKET COLLECTOR                           │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │  BTCUSDT     │   │   ETHUSDT    │   │   BNBUSDT    │       │
│  │  WebSocket   │   │  WebSocket   │   │  WebSocket   │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    BINANCE FUTURES WEBSOCKET                     │
│                   wss://fstream.binance.com                     │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Ingestion Layer

**Binance WebSocket Collector**
- Connects to `wss://fstream.binance.com/ws/{symbol}@trade`
- Handles multiple symbols simultaneously
- Normalizes tick data format
- Buffers messages for batch processing

**Key Features:**
- Automatic reconnection (to be implemented)
- Message buffering
- Thread-safe operations

### 2. Storage Layer

**SQLite Database**
- Lightweight, serverless database
- Two main tables:
  - `ticks`: Raw tick data (timestamp, symbol, price, size)
  - `ohlc`: Aggregated OHLC data (open, high, low, close, volume)
- Indexed for fast queries
- Automatic data deduplication

### 3. Processing Layer

**Data Resampler**
- Aggregates tick data to multiple timeframes
- Supported: 1s, 1min, 5min
- Computes OHLC, volume, trade count
- Handles missing data gracefully

**Analytics Engine**
- Statistical computation module
- Modular design allows easy addition of new analytics
- Functions:
  - Price statistics (mean, std, min, max, quartiles)
  - Z-score (rolling standardization)
  - ADF test for stationarity
  - Hedge ratio via OLS regression
  - Rolling correlation
  - Volume profiling
  - Bollinger Bands

### 4. API Layer

**FastAPI Backend**
- RESTful API for data access
- Endpoints for:
  - Collector control (start/stop)
  - Data retrieval (ticks, OHLC)
  - Analytics computation
  - Alert management
- CORS enabled for frontend access
- Async support for scalability

### 5. Presentation Layer

**Streamlit Dashboard**
- Interactive web-based UI
- Four main views:
  1. **Price Chart**: Candlestick visualization
  2. **Analytics**: Key metrics and z-score
  3. **Statistics**: Detailed statistical breakdown
  4. **Settings**: Configuration and export
- Real-time updates via auto-refresh
- Plotly charts for interactivity

## Data Flow

### 1. Collection Flow
```
Binance → WebSocket → Collector → Buffer → Database
```

### 2. Analytics Flow
```
Database → Resampler → OHLC Data → Analytics Engine → API → Frontend
```

### 3. Real-time Flow
```
Binance → Collector → Database → API → Streamlit (auto-refresh)
```

## Design Principles

### Modularity
- Each component is independent
- Well-defined interfaces between components
- Easy to replace or extend any component

### Scalability
- Database can be replaced with PostgreSQL/Redis
- API can be load-balanced
- Multiple collector instances possible

### Extensibility
- New analytics: Add functions to `AnalyticsEngine`
- New data sources: Implement collector interface
- New visualizations: Add tabs in Streamlit

### Data Sources
Current: Binance WebSocket
Potential:
- CME futures
- REST API polling
- CSV file upload
- Kafka streams

## Performance Considerations

### Storage
- SQLite suitable for development
- Indexed queries for fast retrieval
- Automatic aggregation reduces storage needs

### Computation
- Analytics computed on-demand
- Rolling window calculations
- Vectorized operations with pandas/numpy

### Network
- WebSocket for real-time data
- REST API for control and retrieval
- Efficient JSON serialization

## Security Considerations

**Current Implementation:**
- Local-only access (127.0.0.1)
- No authentication

**Production Deployment:**
- Authentication required
- Rate limiting
- HTTPS/SSL
- Database encryption
- Access control

## Deployment Scenarios

### Development (Current)
```
Python environment → SQLite → Local network
```

### Production (Recommended)
```
Docker containers → PostgreSQL → Cloud deployment
                   ↓
              Nginx/Apache
                   ↓
          Load balancer
```

### Microservices (Advanced)
```
[Collector Service] → [Message Queue] → [Processor Service]
                                             ↓
[Analytics Service] ← [Database] ← [Storage Service]
                          ↓
                   [API Gateway] → [Frontend CDN]
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend API | FastAPI | REST API server |
| Frontend | Streamlit | Interactive dashboard |
| Database | SQLite | Data storage |
| WebSocket | websocket-client | Real-time data |
| Analytics | pandas, numpy, scipy, statsmodels | Statistical computation |
| Visualization | Plotly | Interactive charts |
| Language | Python 3.10+ | Implementation |

## Future Enhancements

1. **Infrastructure**
   - Docker containerization
   - Kubernetes orchestration
   - Redis for caching
   - PostgreSQL for production

2. **Advanced Analytics**
   - Kalman Filter
   - Robust regression
   - Machine learning models
   - Backtesting framework

3. **Features**
   - Multi-asset correlation
   - Strategy backtesting
   - Paper trading
   - Performance attribution

4. **Operations**
   - Logging (ELK stack)
   - Monitoring (Prometheus)
   - Alerting (PagerDuty)
   - CI/CD pipeline

