"""
Streamlit frontend for Quant Analytics dashboard.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time
import json

# Page configuration
st.set_page_config(
    page_title="Quant Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# API base URL
API_URL = "http://localhost:8000"

# Initialize session state
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = {}

def fetch_symbols():
    """Fetch available symbols from API."""
    try:
        response = requests.get(f"{API_URL}/symbols")
        if response.status_code == 200:
            data = response.json()
            return data.get('symbols', [])
    except Exception as e:
        st.error(f"Error fetching symbols: {e}")
    return []

def fetch_ticks(symbol, limit=1000):
    """Fetch ticks for a symbol."""
    try:
        response = requests.get(f"{API_URL}/ticks/{symbol}?limit={limit}")
        if response.status_code == 200:
            data = response.json()
            return data.get('ticks', [])
    except Exception as e:
        st.error(f"Error fetching ticks: {e}")
    return []

def fetch_ohlc(symbol, timeframe='1min'):
    """Fetch OHLC data for a symbol."""
    try:
        # Convert symbol to lowercase for API consistency
        symbol = symbol.lower()
        response = requests.get(f"{API_URL}/ohlc/{symbol}?timeframe={timeframe}")
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
    except Exception as e:
        st.error(f"Error fetching OHLC data: {e}")
    return []

def fetch_analytics(symbol, timeframe='1min', window=60):
    """Fetch analytics for a symbol."""
    try:
        # Convert symbol to lowercase for API consistency
        symbol = symbol.lower()
        response = requests.get(f"{API_URL}/analytics/{symbol}?timeframe={timeframe}&window={window}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching analytics: {e}")
    return {}

def plot_price_chart(df, symbol):
    """Plot price chart with candlesticks."""
    # Handle both column naming conventions
    open_col = 'open' if 'open' in df.columns else 'open_price'
    high_col = 'high' if 'high' in df.columns else 'high_price'
    low_col = 'low' if 'low' in df.columns else 'low_price'
    close_col = 'close' if 'close' in df.columns else 'close_price'
    
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df[open_col],
        high=df[high_col],
        low=df[low_col],
        close=df[close_col],
        name=symbol
    )])
    
    fig.update_layout(
        title=f'{symbol} Price Chart',
        xaxis_title='Time',
        yaxis_title='Price',
        height=500,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def plot_spread_and_zscore(prices_df, zscores):
    """Plot spread and z-score."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Price', 'Z-Score')
    )
    
    # Price chart
    fig.add_trace(
        go.Scatter(
            x=prices_df.index,
            y=prices_df['close'],
            mode='lines',
            name='Price',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    # Z-score chart
    if zscores and len(zscores) > 0:
        zscore_df = pd.DataFrame(zscores)
        zscore_df['timestamp'] = pd.to_datetime(zscore_df['timestamp'])
        
        fig.add_trace(
            go.Scatter(
                x=zscore_df['timestamp'],
                y=zscore_df['zscore'],
                mode='lines',
                name='Z-Score',
                line=dict(color='purple')
            ),
            row=2, col=1
        )
        
        # Add horizontal lines for ±2
        fig.add_hline(y=2, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=-2, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    
    fig.update_layout(height=700, title_text="Price and Z-Score Analysis")
    
    return fig

def plot_statistics(stats_dict):
    """Plot statistics as bar chart."""
    if not stats_dict:
        return None
    
    # Filter out non-numeric values
    numeric_stats = {k: v for k, v in stats_dict.items() if isinstance(v, (int, float))}
    
    if not numeric_stats:
        return None
    
    fig = go.Figure(data=[go.Bar(
        x=list(numeric_stats.keys()),
        y=list(numeric_stats.values())
    )])
    
    fig.update_layout(
        title="Price Statistics",
        xaxis_title="Metric",
        yaxis_title="Value",
        height=400
    )
    
    return fig

# Main app
def main():
    st.title("📈 Quant Analytics Dashboard")
    st.markdown("**Real-time trading analytics and visualization**")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Symbols selection
        symbols = fetch_symbols()
        if symbols:
            selected_symbol = st.selectbox(
                "Select Symbol",
                options=symbols,
                index=0 if symbols else None
            )
        else:
            selected_symbol = st.text_input("Enter symbol", "btcusdt")
            symbols = []
        
        # Timeframe selection
        timeframe = st.selectbox(
            "Timeframe",
            options=['1s', '1min', '5min'],
            index=1
        )
        
        # Window size
        window = st.slider("Rolling Window", min_value=10, max_value=200, value=60)
        
        # Auto-refresh
        auto_refresh = st.checkbox("Auto Refresh", value=False)
        refresh_interval = st.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=5)
        
        st.divider()
        
        # Collector controls
        st.header("📡 Data Collector")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start"):
                symbols_list = [selected_symbol] if selected_symbol else ['btcusdt']
                response = requests.post(f"{API_URL}/start_collector", json=symbols_list)
                if response.status_code == 200:
                    st.success("Collector started")
                else:
                    st.error("Failed to start collector")
        
        with col2:
            if st.button("Stop"):
                response = requests.post(f"{API_URL}/stop_collector")
                if response.status_code == 200:
                    st.success("Collector stopped")
                else:
                    st.error("Failed to stop collector")
        
        # System status
        st.divider()
        st.header("📊 System Status")
        try:
            response = requests.get(f"{API_URL}/stats")
            if response.status_code == 200:
                stats = response.json()
                st.metric("Collector Status", "Running" if stats.get('collector_running') else "Stopped")
                st.metric("Buffer Size", stats.get('message_buffer_size', 0))
                st.metric("Symbols", len(stats.get('symbols', [])))
        except:
            st.error("Cannot connect to API")
    
    # Main content
    if not selected_symbol:
        st.info("Please select a symbol from the sidebar")
        return
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Price Chart", "📈 Analytics", "📉 Statistics", "⚙️ Settings"])
    
    with tab1:
        st.header(f"Price Analysis: {selected_symbol}")
        
        # Fetch OHLC data
        ohlc_data = fetch_ohlc(selected_symbol, timeframe)
        
        if ohlc_data and len(ohlc_data) > 0:
            # Convert to DataFrame
            df = pd.DataFrame(ohlc_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Plot price chart
            fig = plot_price_chart(df, selected_symbol)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display last 20 values
            st.subheader("Recent OHLC Data")
            st.dataframe(df.tail(20), use_container_width=True)
        else:
            st.info(f"No data available for {selected_symbol}. Start the collector to begin receiving data.")
    
    with tab2:
        st.header(f"Analytics: {selected_symbol}")
        
        # Fetch analytics
        analytics = fetch_analytics(selected_symbol, timeframe, window)
        
        if analytics and not analytics.get('message'):
            # Display key metrics
            price_stats = analytics.get('price_stats', {})
            if price_stats:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean Price", f"${price_stats.get('mean', 0):.2f}")
                with col2:
                    st.metric("Std Dev", f"${price_stats.get('std', 0):.2f}")
                with col3:
                    st.metric("Min Price", f"${price_stats.get('min', 0):.2f}")
                with col4:
                    st.metric("Max Price", f"${price_stats.get('max', 0):.2f}")
            
            # ADF Test
            adf_result = analytics.get('adf_test', {})
            if adf_result:
                st.subheader("ADF Test (Stationarity)")
                st.write(f"ADF Statistic: {adf_result.get('adf_statistic', 0):.4f}")
                st.write(f"P-value: {adf_result.get('pvalue', 0):.4f}")
                st.write(f"Is Stationary: {'✅ Yes' if adf_result.get('is_stationary') else '❌ No'}")
            
            # Plot price and z-score
            ohlc_data = fetch_ohlc(selected_symbol, timeframe)
            if ohlc_data:
                df = pd.DataFrame(ohlc_data)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
                
                zscores = analytics.get('zscore', [])
                fig = plot_spread_and_zscore(df, zscores)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for analytics. Collect more data first.")
    
    with tab3:
        st.header(f"Statistics: {selected_symbol}")
        
        # Fetch analytics
        analytics = fetch_analytics(selected_symbol, timeframe, window)
        
        if analytics and not analytics.get('message'):
            # Plot statistics
            price_stats = analytics.get('price_stats', {})
            if price_stats:
                fig = plot_statistics(price_stats)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # Display detailed stats
            st.subheader("Detailed Statistics")
            st.json(analytics.get('price_stats', {}))
        else:
            st.info("Collect data to see statistics.")
    
    with tab4:
        st.header("Settings & Configuration")
        
        # Alert configuration
        st.subheader("Alert Configuration")
        condition = st.text_input("Alert Condition", placeholder="e.g., zscore > 2")
        if st.button("Add Alert"):
            if condition:
                response = requests.post(f"{API_URL}/add_alert", params={"condition": condition})
                if response.status_code == 200:
                    st.success("Alert added successfully")
                else:
                    st.error("Failed to add alert")
        
        # Export data
        st.subheader("Export Data")
        if st.button("Export to CSV"):
            ohlc_data = fetch_ohlc(selected_symbol, timeframe)
            if ohlc_data:
                df = pd.DataFrame(ohlc_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{selected_symbol}_{timeframe}_export.csv",
                    mime="text/csv"
                )
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()

