# How to Run the Project - Simple Guide

## 🚀 Easiest Method (Recommended)

**Just double-click or run:**
```bash
start.bat
```

This starts both the backend and frontend automatically.

## 📋 What Happens

When you run `start.bat`:
1. Opens **Terminal 1** - Backend API (runs in background)
2. Opens **Terminal 2** - Streamlit Dashboard (main window)
3. Both are now running!

## 🌐 Access the Application

Open your browser to:
- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎯 Using the Dashboard

1. **Open** http://localhost:8501
2. **Click "Start"** in the sidebar
3. **Enter a symbol** like `btcusdt` or `ethusdt`
4. **Select timeframe** (1s, 1min, 5m)
5. **View analytics** in the tabs:
   - Price Chart - See candlestick charts
   - Analytics - Z-score and statistics
   - Statistics - Detailed metrics
   - Settings - Configure alerts, export data

## ⚠️ Troubleshooting

### Problem: "Port already in use"
**Solution:**
```powershell
# Stop process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Stop process on port 8501
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

### Problem: "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### Problem: "Can't connect to API"
**Solution:**
1. Make sure backend is running (http://localhost:8000 should work)
2. Wait 5 seconds after starting backend
3. Check that firewall allows local connections

### Problem: "No data showing"
**Solution:**
1. Make sure you clicked "Start" button in sidebar
2. Wait 10-30 seconds for data to accumulate
3. Check internet connection (needed for Binance WebSocket)

## 🛑 Stopping the Application

Press **Ctrl+C** in both terminal windows, or close the windows.

## 🔄 Alternative Methods

**Method 2 - Python Launcher:**
```bash
python start_simple.py
```

**Method 3 - Manual Start (Two Terminals):**

**Terminal 1 - Backend:**
```bash
cd GemsCap_Project
uvicorn src.backend.api:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd GemsCap_Project
streamlit run src/frontend/app.py --server.port 8501
```

## ✅ Verification

Test if everything is working:

1. Open http://localhost:8000/docs - should show API documentation
2. Open http://localhost:8501 - should show the dashboard
3. Click "Start" in sidebar
4. Wait for data to appear

## 📊 Expected Output

After clicking "Start" and waiting:
- You should see price charts
- Analytics will populate
- Buffer size metric will increase
- System status shows "Running"

## 🎓 Key Files

- `start.bat` - Easiest way to start (Windows)
- `start_simple.py` - Python launcher
- `src/backend/api.py` - Backend API
- `src/frontend/app.py` - Frontend dashboard
- `src/models/database.py` - Database
- `src/analytics/engine.py` - Analytics engine

## 💡 Quick Tips

1. **Keep both terminals open** - Don't close the backend terminal
2. **Wait for data** - First results appear in 10-30 seconds
3. **Auto-refresh** - Enable in sidebar for live updates
4. **Multiple symbols** - Start collector with different symbols
5. **Export data** - Use Settings tab to download CSV

## 📚 More Information

- See `README.md` for full documentation
- See `ARCHITECTURE.md` for system design
- See `QUICK_START.md` for quick reference
- See `setup_guide.md` for detailed setup

