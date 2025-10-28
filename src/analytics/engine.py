"""
Analytics engine for computing statistical measures and trading indicators.
"""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from statsmodels.regression.linear_model import OLS
from typing import Dict, List, Optional, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Analytics engine for computing trading indicators and statistics."""
    
    @staticmethod
    def compute_price_statistics(prices: pd.Series) -> Dict[str, float]:
        """
        Compute basic price statistics.
        
        Returns:
            Dictionary containing mean, std, min, max, etc.
        """
        if len(prices) == 0:
            return {}
        
        return {
            'mean': float(prices.mean()),
            'std': float(prices.std()),
            'min': float(prices.min()),
            'max': float(prices.max()),
            'median': float(prices.median()),
            'q25': float(prices.quantile(0.25)),
            'q75': float(prices.quantile(0.75)),
            'range': float(prices.max() - prices.min()),
            'cv': float(prices.std() / prices.mean()) if prices.mean() != 0 else 0.0  # Coefficient of variation
        }
    
    @staticmethod
    def compute_spread(series1: pd.Series, series2: pd.Series) -> pd.Series:
        """
        Compute spread between two series.
        
        Args:
            series1, series2: Price series
        
        Returns:
            Spread series
        """
        # Align the two series on their index
        aligned = pd.DataFrame({'series1': series1, 'series2': series2}).dropna()
        
        if len(aligned) < 2:
            return pd.Series()
        
        return aligned['series1'] - aligned['series2']
    
    @staticmethod
    def compute_zscore(series: pd.Series, window: int = 60) -> pd.Series:
        """
        Compute rolling z-score.
        
        Args:
            series: Price series
            window: Rolling window size
        
        Returns:
            Z-score series
        """
        if len(series) < window:
            return pd.Series()
        
        rolling_mean = series.rolling(window=window).mean()
        rolling_std = series.rolling(window=window).std()
        
        zscore = (series - rolling_mean) / rolling_std
        return zscore
    
    @staticmethod
    def compute_rolling_correlation(
        series1: pd.Series, 
        series2: pd.Series, 
        window: int = 60
    ) -> pd.Series:
        """
        Compute rolling correlation between two series.
        
        Args:
            series1, series2: Price series
            window: Rolling window size
        
        Returns:
            Rolling correlation series
        """
        # Align the two series
        aligned = pd.DataFrame({'series1': series1, 'series2': series2}).dropna()
        
        if len(aligned) < window:
            return pd.Series()
        
        return aligned['series1'].rolling(window=window).corr(aligned['series2'])
    
    @staticmethod
    def compute_hedge_ratio(
        series1: pd.Series, 
        series2: pd.Series, 
        method: str = 'ols'
    ) -> Dict[str, float]:
        """
        Compute hedge ratio using OLS regression.
        
        Args:
            series1: Dependent variable (target)
            series2: Independent variable (hedge)
            method: Regression method ('ols' for Ordinary Least Squares)
        
        Returns:
            Dictionary containing hedge ratio, intercept, and R-squared
        """
        # Align the two series
        aligned = pd.DataFrame({'series1': series1, 'series2': series2}).dropna()
        
        if len(aligned) < 2:
            return {'hedge_ratio': 0.0, 'intercept': 0.0, 'r_squared': 0.0, 'method': method}
        
        X = aligned['series2'].values.reshape(-1, 1)
        y = aligned['series1'].values
        
        # Add constant term for intercept
        X_with_const = np.column_stack([np.ones(len(X)), X])
        
        try:
            # OLS regression
            beta = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
            intercept = beta[0]
            hedge_ratio = beta[1]
            
            # Calculate R-squared
            y_pred = intercept + hedge_ratio * aligned['series2']
            ss_res = ((aligned['series1'] - y_pred) ** 2).sum()
            ss_tot = ((aligned['series1'] - aligned['series1'].mean()) ** 2).sum()
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
            
            return {
                'hedge_ratio': float(hedge_ratio),
                'intercept': float(intercept),
                'r_squared': float(r_squared),
                'method': method
            }
        except Exception as e:
            logger.error(f"Error computing hedge ratio: {e}")
            return {
                'hedge_ratio': 0.0,
                'intercept': 0.0,
                'r_squared': 0.0,
                'method': method
            }
    
    @staticmethod
    def compute_adf_test(series: pd.Series) -> Dict[str, float]:
        """
        Compute Augmented Dickey-Fuller (ADF) test for stationarity.
        
        Args:
            series: Price series
        
        Returns:
            Dictionary containing ADF test results
        """
        if len(series) < 10:
            return {
                'adf_statistic': 0.0,
                'pvalue': 1.0,
                'critical_values': {},
                'is_stationary': False
            }
        
        series_clean = series.dropna()
        
        if len(series_clean) < 10:
            return {
                'adf_statistic': 0.0,
                'pvalue': 1.0,
                'critical_values': {},
                'is_stationary': False
            }
        
        try:
            result = adfuller(series_clean)
            
            return {
                'adf_statistic': float(result[0]),
                'pvalue': float(result[1]),
                'critical_values': {
                    '1%': float(result[4]['1%']),
                    '5%': float(result[4]['5%']),
                    '10%': float(result[4]['10%'])
                },
                'is_stationary': result[1] < 0.05  # p-value < 0.05 suggests stationarity
            }
        except Exception as e:
            logger.error(f"Error computing ADF test: {e}")
            return {
                'adf_statistic': 0.0,
                'pvalue': 1.0,
                'critical_values': {},
                'is_stationary': False
            }
    
    @staticmethod
    def compute_volume_profile(prices: pd.Series, volumes: pd.Series, bins: int = 20) -> Dict[str, Any]:
        """
        Compute volume profile (price levels with volume).
        
        Args:
            prices: Price series
            volumes: Volume series
            bins: Number of bins for price levels
        
        Returns:
            Volume profile data
        """
        if len(prices) == 0 or len(volumes) == 0:
            return {}
        
        aligned = pd.DataFrame({'prices': prices, 'volumes': volumes}).dropna()
        
        if len(aligned) == 0:
            return {}
        
        # Create price bins
        price_min = aligned['prices'].min()
        price_max = aligned['prices'].max()
        
        bins_edges = np.linspace(price_min, price_max, bins + 1)
        bin_indices = np.digitize(aligned['prices'], bins_edges[:-1])
        
        # Aggregate volume by bin
        volume_profile = aligned.groupby(bin_indices)['volumes'].sum()
        bin_centers = (bins_edges[:-1] + bins_edges[1:]) / 2
        
        return {
            'price_levels': [float(bin_centers[idx]) for idx in volume_profile.index if 0 <= idx < len(bin_centers)],
            'volumes': [float(volume_profile.iloc[i]) for i in range(len(volume_profile))],
            'poc': float(bin_centers[volume_profile.idxmax()])  # Point of Control (POC)
        }
    
    @staticmethod
    def compute_returns(prices: pd.Series) -> pd.Series:
        """Compute returns from prices."""
        return prices.pct_change().dropna()
    
    @staticmethod
    def compute_volatility(returns: pd.Series, window: int = 60) -> pd.Series:
        """Compute rolling volatility."""
        if len(returns) < window:
            return pd.Series()
        return returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
    
    @staticmethod
    def compute_moving_average(series: pd.Series, window: int) -> pd.Series:
        """Compute simple moving average."""
        return series.rolling(window=window).mean()
    
    @staticmethod
    def compute_bollinger_bands(
        series: pd.Series, 
        window: int = 20, 
        num_std: float = 2.0
    ) -> Dict[str, pd.Series]:
        """Compute Bollinger Bands."""
        rolling_mean = series.rolling(window=window).mean()
        rolling_std = series.rolling(window=window).std()
        
        return {
            'upper': rolling_mean + (rolling_std * num_std),
            'middle': rolling_mean,
            'lower': rolling_mean - (rolling_std * num_std)
        }

