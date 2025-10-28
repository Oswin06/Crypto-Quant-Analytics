"""
Simplified application launcher.
Run with: python run.py
"""
import subprocess
import sys
import time
import signal
import requests

def check_api():
    """Check if API is running."""
    try:
        return requests.get("http://localhost:8000/").status_code == 200
    except:
        return False

def main():
    print("=" * 60)
    print("Quant Analytics Dashboard - Starting...")
    print("=" * 60)
    
    # Import and start API
    if not check_api():
        print("\n[1/3] Starting FastAPI backend on http://localhost:8000...")
        import threading
        import uvicorn
        
        def run_api():
            uvicorn.run(
                "src.backend.api:app",
                host="127.0.0.1",
                port=8000,
                log_level="info"
            )
        
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        # Wait for API
        for i in range(15):
            time.sleep(1)
            if check_api():
                print("[OK] Backend started successfully")
                break
            if i == 14:
                print("[ERROR] Backend failed to start")
                return
        
        time.sleep(1)
    
    print("\n[2/3] Backend running on http://localhost:8000")
    print("[3/3] Starting Streamlit frontend...")
    print("\n" + "=" * 60)
    print("Dashboard will open at: http://localhost:8501")
    print("=" * 60 + "\n")
    
    # Run Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "src/frontend/app.py",
        "--server.port=8501"
    ])

if __name__ == "__main__":
    main()

