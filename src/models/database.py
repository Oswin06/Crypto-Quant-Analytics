"""
Database models and connection management for tick data storage.
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TickDatabase:
    """SQLite database for storing tick data."""
    
    def __init__(self, db_path: str = "data/ticks.db"):
        """Initialize database connection."""
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables."""
        cursor = self.conn.cursor()
        
        # Ticks table - raw tick data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                price REAL NOT NULL,
                size REAL NOT NULL,
                event_time TEXT,
                trade_id INTEGER
            )
        """)
        
        # OHLC table - aggregated data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ohlc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume REAL,
                timeframe TEXT,
                trade_count INTEGER,
                UNIQUE(symbol, timestamp, timeframe)
            )
        """)
        
        # Indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticks_symbol_timestamp 
            ON ticks(symbol, timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ohlc_symbol_timestamp 
            ON ohlc(symbol, timestamp, timeframe)
        """)
        
        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def insert_tick(self, tick_data: Dict[str, Any]) -> None:
        """Insert a tick into the database."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ticks (symbol, timestamp, price, size, event_time, trade_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tick_data['symbol'],
                tick_data['timestamp'],
                tick_data['price'],
                tick_data['size'],
                tick_data.get('event_time'),
                tick_data.get('trade_id')
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error inserting tick: {e}")
            self.conn.rollback()
    
    def insert_ticks_batch(self, ticks: List[Dict[str, Any]]) -> None:
        """Insert multiple ticks in batch for efficiency."""
        cursor = self.conn.cursor()
        try:
            cursor.executemany("""
                INSERT INTO ticks (symbol, timestamp, price, size, event_time, trade_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (
                    tick['symbol'],
                    tick['timestamp'],
                    tick['price'],
                    tick['size'],
                    tick.get('event_time'),
                    tick.get('trade_id')
                )
                for tick in ticks
            ])
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error inserting ticks batch: {e}")
            self.conn.rollback()
    
    def insert_ohlc(self, ohlc_data: Dict[str, Any]) -> None:
        """Insert OHLC data."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO ohlc 
                (symbol, timestamp, open_price, high_price, low_price, close_price, 
                 volume, timeframe, trade_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ohlc_data['symbol'],
                ohlc_data['timestamp'],
                ohlc_data['open'],
                ohlc_data['high'],
                ohlc_data['low'],
                ohlc_data['close'],
                ohlc_data['volume'],
                ohlc_data['timeframe'],
                ohlc_data.get('trade_count', 0)
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error inserting OHLC: {e}")
            self.conn.rollback()
    
    def get_ticks(
        self, 
        symbol: str, 
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get ticks for a symbol within a time range."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM ticks WHERE symbol = ?"
        params = [symbol]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_ohlc(
        self,
        symbol: str,
        timeframe: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get OHLC data for a symbol and timeframe."""
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM ohlc 
            WHERE symbol = ? AND timeframe = ?
        """
        params = [symbol, timeframe]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to dict with correct column names
        result = []
        for row in rows:
            result.append({
                'symbol': row['symbol'],
                'timestamp': row['timestamp'],
                'open': row['open_price'],
                'high': row['high_price'],
                'low': row['low_price'],
                'close': row['close_price'],
                'volume': row['volume'],
                'timeframe': row['timeframe'],
                'trade_count': row.get('trade_count', 0)
            })
        return result
    
    def get_symbols(self) -> List[str]:
        """Get all unique symbols."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT symbol FROM ticks")
        return [row[0] for row in cursor.fetchall()]
    
    def get_tick_count(self, symbol: str) -> int:
        """Get total tick count for a symbol."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ticks WHERE symbol = ?", (symbol,))
        return cursor.fetchone()[0]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

