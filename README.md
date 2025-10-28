# Quant Analytics Dashboard

A real-time trading analytics and visualization system for cryptocurrency data from Binance futures market.

## 🎯 Project Overview

This application demonstrates end-to-end capabilities from real-time data ingestion to quantitative analytics and interactive visualization. The system is designed with modularity and extensibility in mind, suitable for use in quantitative trading environments.

### Key Features

- **Real-time Data Collection**: WebSocket connection to Binance futures for live tick data
- **Data Storage**: SQLite database for efficient storage and retrieval
- **Multi-timeframe Resampling**: Automatic aggregation (1s, 1m, 5m timeframes)
- **Comprehensive Analytics**:
  - Price statistics (mean, std, min, max, quartiles)
  - Hedge ratio estimation via OLS regression
  - Spread calculation
  - Rolling z-score computation
  - Augmented Dickey-Fuller (ADF) test for stationarity
  - Rolling correlation analysis
  - Volume profiling
  - Bollinger Bands
- **Interactive Visualization**: Plotly-based charts with zoom, pan, hover
- **Alerting System**: Custom condition-based alerts
- **Data Export**: CSV export functionality

## 📋 Requirements

- Python 3.10 or higher
- Windows/Linux/macOS
- Internet connection for Binance WebSocket

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database

The database will be automatically created in the `data/` directory on first run.

## ▶️ Usage

### Quick Start

**Option 1 - Batch File (Windows - Easiest):**
```bash
start.bat
```

**Option 2 - Python Launcher:**
```bash
python start_simple.py
```

**Option 3 - Manual (Two Terminals):**

Terminal 1:
```bash
uvicorn src.backend.api:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2:
```bash
streamlit run src/frontend/app.py --server.port 8501
```

**Once running:**
- Open browser to http://localhost:8501
- Click "Start" in sidebar to begin collecting data
- Select symbol and timeframe
- Navigate through tabs to view analytics

### Manual Start

Alternatively, you can start components separately:

**Backend (Terminal 1):**
```bash
uvicorn src.backend.api:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend (Terminal 2):**
```bash
streamlit run src/frontend/app.py
```

### Using the Dashboard

1. **Start the collector**: Use the sidebar controls to start data collection
2. **Select symbol**: Choose from available symbols (e.g., btcusdt, ethusdt)
3. **Choose timeframe**: Select resampling period (1s, 1m, 5m)
4. **View analytics**: Navigate through tabs to see different analytics
5. **Configure alerts**: Set up custom alert conditions
6. **Export data**: Download CSV files of processed data

## 📁 Project Structure

```
Quant_Analytics/
├── src/
│   ├── backend/
│   │   ├── api.py          # FastAPI backend server
│   │   ├── collector.py    # WebSocket data collector
│   │   └── resampler.py    # Data resampling logic
│   ├── frontend/
│   │   └── app.py          # Streamlit dashboard
│   ├── models/
│   │   └── database.py      # Database models and utilities
│   ├── analytics/
│   │   └── engine.py       # Analytics computation
│   └── utils/
│       └── alert_manager.py # Alert management
├── data/                   # SQLite database
├── logs/                   # Application logs
├── app.py                  # Main entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Symbols

Add symbols to monitor by updating the collector start command or through the API:

```python
POST http://localhost:8000/start_collector
Body: ["btcusdt", "ethusdt", "bnbusdt"]
```

### Timeframes

Available resampling timeframes:
- `1s`: 1 second
- `1min`: 1 minute
- `5min`: 5 minutes

### Rolling Window

Adjust the rolling window for z-score and correlation calculations via the sidebar slider (10-200 periods).

## 📊 API Endpoints

### Data Collection
- `POST /start_collector` - Start WebSocket collector
- `POST /stop_collector` - Stop WebSocket collector
- `GET /stats` - Get system statistics

### Data Retrieval
- `GET /symbols` - Get all available symbols
- `GET /ticks/{symbol}` - Get raw tick data
- `GET /ohlc/{symbol}` - Get OHLC aggregated data

### Analytics
- `GET /analytics/{symbol}` - Get comprehensive analytics

### Alerts
- `POST /add_alert` - Add alert condition
- `GET /alerts` - Get all active alerts

## 🧮 Analytics Explanation

### Price Statistics
- **Mean**: Average price
- **Std**: Standard deviation
- **Min/Max**: Price range
- **Quartiles**: 25th and 75th percentile
- **CV**: Coefficient of variation (std/mean)

### Hedge Ratio (OLS)
Estimates the optimal hedge ratio between two assets using linear regression:
```
y = α + βx + ε
```
Where β is the hedge ratio indicating how many units of asset X to hedge against Y.

### Z-Score
Measures how many standard deviations a price is from its rolling mean:
```
z = (price - mean(price)) / std(price)
```
Values > 2 or < -2 may indicate overbought/oversold conditions.

### ADF Test
Tests for stationarity in time series. A p-value < 0.05 suggests the series is stationary (mean-reverting).

### Rolling Correlation
Computes correlation between two assets over a rolling window, useful for pairs trading.

## 🎨 Dashboard Features

1. **Price Chart Tab**: Candlestick visualization with recent data table
2. **Analytics Tab**: Key metrics, ADF test results, price and z-score plots
3. **Statistics Tab**: Detailed statistical breakdown
4. **Settings Tab**: Alert configuration and data export

## 🔍 Architecture

### Design Philosophy

The system is built with modularity and scalability in mind:

- **Loose Coupling**: Components interact through well-defined interfaces (API endpoints)
- **Scalability**: Can easily switch data sources (Binance → CME, REST API, CSV)
- **Extensibility**: New analytics can be added without modifying existing code
- **Simplicity**: Readable code takes precedence over premature optimization

### Component Interactions

```
[Binance WebSocket] → [Collector] → [Database] → [Resampler] → [Analytics Engine]
                                                          ↓
[Streamlit UI] ← ← ← ← ← ← ← ← ← ← ← ← [FastAPI] ← ← ← ←
```

1. **Collector** receives tick data via WebSocket
2. **Database** stores raw ticks
3. **Resampler** aggregates to OHLC format
4. **Analytics Engine** computes statistics
5. **FastAPI** serves data via REST API
6. **Streamlit** displays interactive visualizations

## 🚨 Alerting

Configure custom alerts in the Settings tab:

Examples:
- `zscore > 2` - Alert when z-score exceeds 2
- `price > 50000` - Alert when price crosses threshold
- `spread > 100` - Alert on spread widening

## 📤 Data Export

Export processed data to CSV:
1. Select symbol and timeframe
2. Go to Settings tab
3. Click "Export to CSV"
4. Download appears with timestamped filename

## 🧪 Testing

### Manual Testing
1. Start collector with test symbol (e.g., btcusdt)
2. Monitor data flow in dashboard
3. Verify analytics update in real-time
4. Test alerts with various conditions

## 📝 ChatGPT Usage Transparency

This project was developed with the assistance of ChatGPT for:
- Initial project structure design
- Code boilerplate generation
- Documentation writing
- Debugging assistance

**Key prompts used:**
- "Design a modular architecture for real-time trading analytics"
- "Create a FastAPI backend with WebSocket collector for Binance data"
- "Build a Streamlit dashboard with interactive Plotly charts"
- "Implement statistical analytics (OLS, ADF test, z-score) in Python"

## 🎓 Learning Resources

- [Binance WebSocket Documentation](https://binance-docs.github.io/apidocs/futures/en/#websocket-market-data)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)

## 📄 License

This project is developed for educational and evaluation purposes.

## 👤 Author

Created for Quantitative Developer Evaluation

## 🙏 Acknowledgments

- Binance for providing public WebSocket API
- FastAPI, Streamlit, and Plotly communities
- Statsmodels for statistical functions

