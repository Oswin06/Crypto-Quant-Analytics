"""
Main application entry point for Quant Analytics.
"""
import uvicorn
import subprocess
import sys
from pathlib import Path

def check_api_running():
    """Check if API is already running."""
    try:
        import requests
        response = requests.get("http://localhost:8000/")
        return response.status_code == 200
    except:
        return False

def main():
    """Run the application."""
    print("=" * 60)
    print("Quant Analytics Dashboard")
    print("=" * 60)
    print()
    
    # Check if API is running
    if not check_api_running():
        print("Starting FastAPI backend...")
        # Start API in background
        import threading
        def run_api():
            uvicorn.run(
                "src.backend.api:app",
                host="127.0.0.1",
                port=8000,
                log_level="info"
            )
        
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        # Wait for API to start
        import time
        max_wait = 10
        for i in range(max_wait):
            time.sleep(1)
            if check_api_running():
                print("✓ API started successfully")
                break
            print(f"Waiting for API... ({i+1}/{max_wait})")
        
        if not check_api_running():
            print("✗ Failed to start API")
            sys.exit(1)
    else:
        print("✓ API already running")
    
    print()
    print("Starting Streamlit frontend...")
    print("Dashboard will be available at: http://localhost:8501")
    print()
    print("=" * 60)
    
    # Start Streamlit
    import streamlit.web.cli as stcli
    sys.argv = [
        "streamlit",
        "run",
        str(Path(__file__).parent / "src" / "frontend" / "app.py"),
        "--server.port=8501",
        "--server.headless=true"
    ]
    stcli.main()

if __name__ == "__main__":
    main()


