# 🎯 Drone Tech AI Portal - Unified Server Solution

## ⚡ Quick Start (30 seconds)

**Windows Users:**
```bash
Double-click: RUN_SERVERS.bat
```

**Command Line:**
```bash
start_all.bat
OR
.\start_all.ps1
OR
python start_all.py
```

✅ Both servers will start automatically!

---

## 📖 What This Does

This solution allows you to run **two separate servers with ONE command**:

- **Port 5000:** Main Portal (Flask) - Dashboard, Authentication
- **Port 8000:** Body Tracking Model (FastAPI) - Pose Detection

When you click the "Body Tracking" button on the dashboard, you're automatically redirected from port 5000 to port 8000.

---

## 📁 New Files Created

| File | Purpose |
|------|---------|
| `start_all.bat` | Windows batch starter (easiest) |
| `start_all.ps1` | PowerShell starter |
| `start_all.py` | Python starter (cross-platform) |
| `RUN_SERVERS.bat` | Quick launcher (click to run) |
| `QUICK_START.md` | Quick reference guide |
| `STARTUP_GUIDE.md` | Complete setup & troubleshooting |
| `IMPLEMENTATION_SUMMARY.md` | Technical implementation details |
| `ARCHITECTURE_GUIDE.md` | System architecture & flow diagrams |

---

## 📝 Modified Files

| File | Change | Impact |
|------|--------|--------|
| `script.js` | Line 59: `body: 'body.html'` → `body: 'http://localhost:8000'` | Body tracking button now navigates to port 8000 |

**That's it! Only 1 line changed!**

---

## 🚀 Usage Workflow

```
1. Execute: start_all.bat (or .ps1 or .py)
                 ↓
2. Both servers start in 5 seconds
                 ↓
3. Open: http://localhost:5000
                 ↓
4. Login with credentials
                 ↓
5. Click: "Body Tracking" button
                 ↓
6. Redirected to: http://localhost:8000
                 ↓
7. Body tracking model interface loads
                 ↓
8. Use browser back button to return
```

---

## ✨ Key Features

✅ **Single Command Execution** - Start both servers at once
✅ **Automatic Port Management** - Configured ports 5000 & 8000
✅ **Graceful Shutdown** - Press Ctrl+C to stop all servers
✅ **Multiple Startup Methods** - Batch, PowerShell, or Python
✅ **Zero Existing Code Changes** - Only 1 line modified in script.js
✅ **No New Dependencies** - Uses existing packages
✅ **No New Folders** - No static folder created
✅ **Cross-Platform** - Works on Windows, Linux, macOS
✅ **Environment Aware** - Uses body_tracking conda environment
✅ **Well Documented** - Complete guides included

---

## 📋 System Requirements

- Python 3.8+
- Conda with `body_tracking` environment
- Dependencies from `requirements.txt` installed
- Ports 5000 and 8000 available

---

## 🔧 Troubleshooting

### "Port already in use?"
```bash
# Check what's using the port
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F
```

### "Conda environment not found?"
```bash
conda create -n body_tracking python=3.8
conda activate body_tracking
pip install -r requirements.txt
```

### "Module import error?"
```bash
conda activate body_tracking
pip install -r requirements.txt --upgrade
```

See **STARTUP_GUIDE.md** for more troubleshooting!

---

## 📊 Architecture Overview

```
User runs: start_all.bat
                ↓
        ┌───────────────┐
        │ Conda Env     │
        │ Activation   │
        └───────┬───────┘
                ↓
    ┌───────────────────────┐
    │  Flask Server         │
    │  (Port 5000)          │
    │                       │
    │ • Main Portal         │
    │ • Dashboard           │
    │ • Authentication      │
    └───────────────────────┘
                ↓ (click Body Tracking)
    ┌───────────────────────┐
    │  FastAPI Server       │
    │  (Port 8000)          │
    │                       │
    │ • Body Tracking UI    │
    │ • Pose Detection      │
    │ • Video Processing    │
    └───────────────────────┘
```

See **ARCHITECTURE_GUIDE.md** for detailed diagrams!

---

## 📚 Documentation Files

1. **QUICK_START.md** - Get started in 30 seconds
2. **STARTUP_GUIDE.md** - Complete guide with troubleshooting
3. **IMPLEMENTATION_SUMMARY.md** - What changed and why
4. **ARCHITECTURE_GUIDE.md** - System design & flow diagrams

---

## ✅ Testing the Solution

1. **Start the servers:**
   ```bash
   start_all.bat
   ```

2. **Check Flask server:**
   ```
   Open: http://localhost:5000
   Expected: Drone Tech AI Portal login page
   ```

3. **Check FastAPI server:**
   ```
   Open: http://localhost:8000
   Expected: Body Tracking interface (if served directly)
   ```

4. **Test navigation:**
   - Login with credentials
   - Click "Body Tracking" button
   - Browser should redirect to port 8000
   - Body tracking interface should load

5. **Test return:**
   - Use browser back button
   - Should return to port 5000

---

## 🛑 Stopping the Servers

### Method 1: Press Ctrl+C
```
Press: Ctrl+C (in the terminal running start_all.py)
Result: Both servers shut down gracefully
```

### Method 2: Close Terminal Windows
- If using batch/PowerShell: Close the windows
- Servers will stop automatically

### Method 3: Task Manager (Windows)
```
1. Open Task Manager (Ctrl+Shift+Esc)
2. Find: python.exe processes
3. Right-click → End Task
```

---

## 🔄 Manual Startup (If Needed)

If startup scripts don't work, run manually:

**Terminal 1:**
```bash
conda activate body_tracking
python server.py
```

**Terminal 2:**
```bash
conda activate body_tracking
python run_dev.py
```

Then navigate to `http://localhost:5000`

---

## 💡 How It Works

### Before This Solution
```
Manual: Terminal 1 → python server.py
        Terminal 2 → python run_dev.py
        Problem: Two commands, two terminals to manage
```

### After This Solution
```
Automated: One command → start_all.bat
           Both servers start together
           Button click handles navigation
           Result: Seamless user experience ✅
```

---

## 📞 Support

### Quick Fixes
1. Check **QUICK_START.md** for common issues
2. Check **STARTUP_GUIDE.md** for detailed troubleshooting
3. Verify conda environment exists
4. Ensure ports 5000 & 8000 are free

### If Still Stuck
1. Verify Python installation: `python --version`
2. Verify Conda installation: `conda --version`
3. Check environment: `conda env list`
4. Verify packages: `conda activate body_tracking && pip list`

---

## 📦 What's NOT Changed

✅ No modification to `server.py`
✅ No modification to `run_dev.py`
✅ No modification to `body.html`
✅ No modification to CSS files
✅ No new static folders created
✅ No breaking changes to existing code
✅ All original functionality preserved

---

## 🎯 Next Steps

1. **First Time Users:** Read **QUICK_START.md**
2. **Detailed Setup:** Read **STARTUP_GUIDE.md**
3. **Understanding Architecture:** Read **ARCHITECTURE_GUIDE.md**
4. **Implementation Details:** Read **IMPLEMENTATION_SUMMARY.md**

---

## 🚀 Ready to Go!

Everything is set up and ready to use!

```bash
# For Windows users:
Double-click: RUN_SERVERS.bat

# For command line:
python start_all.py

# Then open: http://localhost:5000
```

**Enjoy your unified server experience!** 🎉

---

**Created:** January 2026
**Solution Type:** Multi-Server Unified Startup
**Technology:** Flask (Port 5000) + FastAPI (Port 8000)
**Status:** ✅ Ready to Use
