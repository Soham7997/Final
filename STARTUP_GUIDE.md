# Unified Server Startup Guide

## Overview
You can now run both servers with a **single command** instead of manually running two separate terminals!

### What Changed?
- **Modified**: `script.js` - Updated body tracking button to navigate to `http://localhost:8000`
- **Created**: `start_all.bat` - Windows batch file to start both servers
- **Created**: `start_all.ps1` - PowerShell script to start both servers
- **Created**: `start_all.py` - Python script to start both servers

---

## How to Run

### Option 1: Windows Batch File (Easiest)
Simply double-click or run:
```bash
start_all.bat
```

This will:
1. Activate your `body_tracking` conda environment
2. Start Flask server on port 5000 in one window
3. Start FastAPI server on port 8000 in another window
4. Display helpful information about the URLs

### Option 2: PowerShell Script
Run in PowerShell:
```powershell
.\start_all.ps1
```

Or in VS Code terminal (PowerShell):
```powershell
powershell -ExecutionPolicy Bypass -File start_all.ps1
```

### Option 3: Python Script
Run in any terminal:
```bash
python start_all.py
```

---

## Usage Workflow

1. **Start the servers** using one of the methods above
2. **Open your browser** and navigate to: `http://localhost:5000`
3. **Log in** with your credentials
4. **Click "Body Tracking"** button on the dashboard
5. **Automatically redirected** to `http://localhost:8000` where the body tracking model is running

---

## Server Details

| Server | Port | Purpose | Command |
|--------|------|---------|---------|
| Flask (server.py) | 5000 | Main Portal UI | `python server.py` |
| FastAPI (run_dev.py) | 8000 | Body Tracking Model | `python run_dev.py` |

---

## Stopping the Servers

**Press `Ctrl+C`** in the terminal/window to stop all servers gracefully.

Or close the terminal windows if using batch/PowerShell.

---

## Troubleshooting

### "conda: command not found"
- Make sure Anaconda/Miniconda is installed
- Add conda to your system PATH

### Port Already in Use
- Make sure no other services are using ports 5000 or 8000
- Kill any existing Python processes:
  ```bash
  # Windows
  netstat -ano | findstr :5000
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```

### "body_tracking environment not found"
- Create the environment:
  ```bash
  conda create -n body_tracking python=3.8
  conda activate body_tracking
  pip install -r requirements.txt
  ```

### Module Import Errors
- Make sure all requirements are installed:
  ```bash
  conda activate body_tracking
  pip install -r requirements.txt
  ```

---

## What's Happening Behind the Scenes?

When you click the "Body Tracking" button on the main portal (port 5000):
1. The button click handler reads the `data-module` attribute
2. `script.js` maps "body" module to `http://localhost:8000`
3. Your browser navigates to the FastAPI server
4. The body tracking model interface loads
5. When done, you can go back to the main portal by browser back button or manually navigating to port 5000

---

## No Changes to Existing Functionality
- ✅ All existing files remain unchanged
- ✅ No new static folders created
- ✅ Only `script.js` was modified to map the navigation
- ✅ Both servers work independently as before
- ✅ Can still run them manually separately if needed

---

**Enjoy your unified server experience!** 🚀
