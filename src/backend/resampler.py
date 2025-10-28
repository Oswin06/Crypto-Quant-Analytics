"""
Data resampling and aggregation for different timeframes.
"""
import pandas as pd
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataResampler:
    """Resample tick data into different timeframes."""
    
    @staticmethod
    def ticks_to_dataframe(ticks: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert list of ticks to pandas DataFrame."""
        if not ticks:
            return pd.DataFrame()
        
        df = pd.DataFrame(ticks)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        df = df.sort_index()
        return df
    
    @staticmethod
    def resample_to_ohlc(
        ticks: List[Dict[str, Any]],
        timeframe: str = '1min'
    ) -> List[Dict[str, Any]]:
        """
        Resample ticks to OHLC format.
        
        Args:
            ticks: List of tick dictionaries
            timeframe: Resampling timeframe (e.g., '1s', '1min', '5min')
        
        Returns:
            List of OHLC dictionaries
        """
        if not ticks:
            return []
        
        df = DataResampler.ticks_to_dataframe(ticks)
        
        if df.empty:
            return []
        
        symbol = df['symbol'].iloc[0]
        
        # Resample to OHLC
        ohlc = df['price'].resample(timeframe).ohlc()
        volume = df['size'].resample(timeframe).sum()
        trade_count = df.resample(timeframe).size()
        
        # Combine results
        result = pd.concat([ohlc, volume.rename('volume'), trade_count.rename('trade_count')], axis=1)
        result = result.bfill()  # Fill missing values with last known price
        
        # Convert to list of dicts
        ohlc_list = []
        for timestamp, row in result.iterrows():
            ohlc_list.append({
                'symbol': symbol,
                'timestamp': timestamp.isoformat(),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']),
                'trade_count': int(row['trade_count']),
                'timeframe': timeframe
            })
        
        return ohlc_list
    
    @staticmethod
    def get_timeframe_seconds(timeframe: str) -> int:
        """Convert timeframe string to seconds."""
        timeframe_map = {
            '1s': 1,
            '1min': 60,
            '5min': 300,
            '15min': 900,
            '1h': 3600,
            '1d': 86400
        }
        return timeframe_map.get(timeframe, 60)
    
    @staticmethod
    def aggregate_ticks(ticks: List[Dict[str, Any]], timeframe: str = '1min') -> List[Dict[str, Any]]:
        """Aggregate ticks for a given timeframe."""
        return DataResampler.resample_to_ohlc(ticks, timeframe)

