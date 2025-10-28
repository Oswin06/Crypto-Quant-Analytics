"""
Simplified launcher - starts components in separate processes.
"""
import subprocess
import sys
import webbrowser
from pathlib import Path
import time

def main():
    print("=" * 60)
    print("Quant Analytics Dashboard - Starting")
    print("=" * 60)
    print()
    
    print("[1/2] Starting Backend API...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.backend.api:app", 
         "--host", "127.0.0.1", "--port", "8000"],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    # Wait a bit for backend to start
    for i in range(5):
        time.sleep(1)
        print(f"  Waiting for API... ({i+1}/5)")
    
    print("\n[2/2] Starting Streamlit Frontend...")
    print("\nDashboard will open at: http://localhost:8501")
    print("API is available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\n" + "=" * 60)
    print("\nPress Ctrl+C to stop all services\n")
    
    # Start Streamlit in foreground
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "src/frontend/app.py", "--server.port", "8501"
    ])
    
    # Cleanup
    try:
        backend.terminate()
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)


