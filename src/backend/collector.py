"""
WebSocket data collector for Binance futures tick data.
"""
import json
import websocket
import threading
import logging
from datetime import datetime
from typing import List, Optional, Callable
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinanceCollector:
    """WebSocket collector for Binance futures tick data."""
    
    def __init__(self, symbols: List[str], on_message_callback: Optional[Callable] = None):
        """
        Initialize collector.
        
        Args:
            symbols: List of symbols to collect (e.g., ['btcusdt', 'ethusdt'])
            on_message_callback: Callback function to handle incoming messages
        """
        self.symbols = [symbol.lower() for symbol in symbols]
        self.on_message_callback = on_message_callback
        self.running = False
        self.ws_connections = []
        self.message_buffer = []
        self.buffer_lock = threading.Lock()
    
    def _normalize_tick(self, data: dict) -> dict:
        """
        Normalize tick data from Binance WebSocket.
        
        Raw Binance format:
        {
            "e": "trade",
            "E": 123456789,
            "s": "BTCUSDT",
            "t": 12345,
            "p": "40000.00",
            "q": "0.1",
            "b": 123,
            "a": 123,
            "T": 123456789,
            "m": true
        }
        """
        try:
            # Use 'T' (trade time) or 'E' (event time) as timestamp
            timestamp = datetime.fromtimestamp(
                data.get('T', data.get('E', time.time() * 1000)) / 1000
            ).isoformat()
            
            return {
                'symbol': data.get('s', '').lower(),  # Convert to lowercase
                'timestamp': timestamp,
                'price': float(data.get('p', 0)),
                'size': float(data.get('q', 0)),
                'event_time': data.get('T'),
                'trade_id': data.get('t'),
                'is_buyer_maker': data.get('m', False)
            }
        except Exception as e:
            logger.error(f"Error normalizing tick: {e}")
            return None
    
    def _on_message(self, ws, message, symbol: str):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            
            # Filter for trade events
            if data.get('e') == 'trade':
                normalized = self._normalize_tick(data)
                if normalized:
                    with self.buffer_lock:
                        self.message_buffer.append(normalized)
                    
                    # Call callback if provided
                    if self.on_message_callback:
                        self.on_message_callback(normalized)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _on_open(self, ws):
        """Handle WebSocket open."""
        logger.info("WebSocket connection opened")
    
    def _on_error(self, ws, error):
        """Handle WebSocket error."""
        logger.error(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close."""
        logger.info("WebSocket connection closed")
    
    def _create_connection(self, symbol: str) -> websocket.WebSocketApp:
        """Create WebSocket connection for a symbol."""
        url = f"wss://fstream.binance.com/ws/{symbol}@trade"
        
        def on_message_wrapper(ws, msg):
            self._on_message(ws, msg, symbol)
        
        ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=on_message_wrapper,
            on_error=self._on_error,
            on_close=self._on_close
        )
        return ws
    
    def start(self):
        """Start collecting data for all symbols."""
        if self.running:
            logger.warning("Collector already running")
            return
        
        self.running = True
        self.ws_connections = []
        
        # Create WebSocket connection for each symbol
        for symbol in self.symbols:
            logger.info(f"Starting WebSocket for {symbol}")
            ws = self._create_connection(symbol)
            self.ws_connections.append(ws)
            
            # Start WebSocket in a separate thread
            thread = threading.Thread(target=ws.run_forever, daemon=True)
            thread.start()
        
        logger.info(f"Started collectors for {len(self.symbols)} symbols")
    
    def stop(self):
        """Stop collecting data."""
        self.running = False
        for ws in self.ws_connections:
            try:
                ws.close()
            except:
                pass
        self.ws_connections = []
        logger.info("Stopped all collectors")
    
    def get_buffered_messages(self, clear: bool = True) -> List[dict]:
        """Get buffered messages and optionally clear the buffer."""
        with self.buffer_lock:
            messages = self.message_buffer.copy()
            if clear:
                self.message_buffer = []
            return messages
    
    def get_message_count(self) -> int:
        """Get current message count in buffer."""
        with self.buffer_lock:
            return len(self.message_buffer)

