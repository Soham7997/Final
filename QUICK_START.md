# 🚀 QUICK START - Run Everything with ONE Command!

## Windows Users - Easiest Way

### Step 1: Double-click this file
```
start_all.bat
```

✅ That's it! Two terminal windows will open automatically.

---

## PowerShell Users

```powershell
.\start_all.ps1
```

---

## Command Line Users

### Using Python
```bash
python start_all.py
```

### Manual Method (if needed)
Open TWO terminals:
```bash
# Terminal 1
python server.py

# Terminal 2
python run_dev.py
```

---

## 📍 Navigation Flow

```
1. Open browser → http://localhost:5000
                    ↓
2. Login with credentials
                    ↓
3. Click "Body Tracking" button
                    ↓
4. Automatically redirected to → http://localhost:8000
                    ↓
5. Body tracking model interface loads
                    ↓
6. Use browser back button to return to main portal
```

---

## 🔧 What Was Changed?

✅ **Modified Files:**
- `script.js` - Maps body tracking button to port 8000

✅ **No Changes To:**
- ❌ No existing functionality altered
- ❌ No static folders created
- ❌ No files deleted or restructured
- ❌ No requirements changed

✅ **New Files Created:**
- `start_all.bat` - Windows batch startup
- `start_all.ps1` - PowerShell startup
- `start_all.py` - Python startup
- `STARTUP_GUIDE.md` - Full documentation
- `QUICK_START.md` - This file

---

## 🐛 Troubleshooting

**"Port already in use?"**
```bash
# Kill the process using the port
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**"Module not found?"**
```bash
conda activate body_tracking
pip install -r requirements.txt
```

**"Can't find body_tracking environment?"**
```bash
conda create -n body_tracking python=3.8
conda activate body_tracking
pip install -r requirements.txt
```

---

## ✨ Features

✅ Start both servers with ONE command
✅ Automatic port management (5000 & 8000)
✅ Graceful shutdown with Ctrl+C
✅ Cross-platform (Windows, PowerShell, Python)
✅ No configuration needed
✅ Real-time server monitoring
✅ Works with existing conda environment

---

**Ready? Run `start_all.bat` now!** 🎯
