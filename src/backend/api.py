"""
FastAPI backend for serving data and analytics endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from src.models.database import TickDatabase
from src.backend.collector import BinanceCollector
from src.backend.resampler import DataResampler
from src.analytics.engine import AnalyticsEngine
from src.utils.alert_manager import AlertManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
app = FastAPI(title="Quant Analytics API", version="1.0.0")
db = TickDatabase()
collector = None
alert_manager = AlertManager()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class TickData(BaseModel):
    symbol: str
    timestamp: str
    price: float
    size: float

class OHLCData(BaseModel):
    symbol: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str

class AnalyticsResponse(BaseModel):
    price_stats: Dict[str, float]
    spread: List[Dict[str, float]]
    zscore: List[Dict[str, float]]
    hedge_ratio: Dict[str, float]
    adf_test: Dict[str, Any]
    correlation: List[Dict[str, float]]

# Store messages in memory for real-time access
message_buffer = []

def on_tick_received(tick: Dict[str, Any]):
    """Callback for when a tick is received."""
    global message_buffer
    message_buffer.append(tick)
    db.insert_tick(tick)

@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    logger.info("API started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    if collector:
        collector.stop()
    db.close()
    logger.info("API shutdown")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Quant Analytics API", "status": "running"}

@app.post("/start_collector")
async def start_collector(symbols: List[str]):
    """Start the data collector."""
    global collector
    
    if collector and collector.running:
        return {"status": "already_running", "symbols": symbols}
    
    collector = BinanceCollector(symbols, on_tick_received)
    collector.start()
    
    return {"status": "started", "symbols": symbols}

@app.post("/stop_collector")
async def stop_collector():
    """Stop the data collector."""
    global collector
    
    if collector and collector.running:
        collector.stop()
        return {"status": "stopped"}
    
    return {"status": "not_running"}

@app.get("/ticks/{symbol}")
async def get_ticks(
    symbol: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 1000
):
    """Get ticks for a symbol."""
    ticks = db.get_ticks(symbol, start_time, end_time, limit)
    return {"symbol": symbol, "count": len(ticks), "ticks": ticks}

@app.get("/ohlc/{symbol}")
async def get_ohlc(
    symbol: str,
    timeframe: str = "1min",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """Get OHLC data for a symbol."""
    # Get raw ticks
    ticks = db.get_ticks(symbol, start_time, end_time, limit=10000)
    
    if not ticks:
        return {"symbol": symbol, "timeframe": timeframe, "count": 0, "data": []}
    
    # Resample ticks to OHLC
    ohlc_list = DataResampler.resample_to_ohlc(ticks, timeframe)
    
    # Store OHLC data in database
    for ohlc_data in ohlc_list:
        db.insert_ohlc(ohlc_data)
    
    return {"symbol": symbol, "timeframe": timeframe, "count": len(ohlc_list), "data": ohlc_list}

@app.get("/symbols")
async def get_symbols():
    """Get all symbols in database."""
    symbols = db.get_symbols()
    return {"symbols": symbols}

@app.get("/analytics/{symbol}")
async def get_analytics(
    symbol: str,
    timeframe: str = "1min",
    window: int = 60
):
    """Get analytics for a symbol."""
    # Get OHLC data
    ohlc_data = db.get_ohlc(symbol, timeframe)
    
    if len(ohlc_data) < 2:
        return {"symbol": symbol, "message": "Insufficient data"}
    
    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(ohlc_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    
    prices = df['close']
    
    # Compute analytics
    price_stats = AnalyticsEngine.compute_price_statistics(prices)
    
    # Z-score
    zscores = AnalyticsEngine.compute_zscore(prices, window=window)
    zscore_data = [
        {"timestamp": ts.isoformat(), "zscore": float(z)}
        for ts, z in zscores.items()
    ]
    
    # ADF test
    adf_result = AnalyticsEngine.compute_adf_test(prices)
    
    # Returns
    returns = AnalyticsEngine.compute_returns(prices)
    volatility = AnalyticsEngine.compute_volatility(returns, window=window)
    
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "price_stats": price_stats,
        "zscore": zscore_data[-100:],  # Last 100 points
        "adf_test": adf_result,
        "volatility": [
            {"timestamp": ts.isoformat(), "volatility": float(v)}
            for ts, v in volatility.items()
        ][-100:]
    }

@app.post("/add_alert")
async def add_alert(condition: str):
    """Add a new alert."""
    alert = alert_manager.add_alert(condition)
    return {"status": "added", "condition": condition}

@app.get("/alerts")
async def get_alerts():
    """Get all alerts."""
    return {"alerts": alert_manager.get_alerts()}

@app.get("/stats")
async def get_stats():
    """Get overall statistics."""
    global collector
    stats = {
        "collector_running": collector.running if collector else False,
        "symbols": db.get_symbols(),
        "message_buffer_size": len(message_buffer)
    }
    
    if collector:
        stats["collector_symbols"] = collector.symbols
        stats["buffer_messages"] = collector.get_message_count()
    
    return stats

