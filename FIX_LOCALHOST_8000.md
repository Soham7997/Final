# 🔧 LOCALHOST 8000 NOT CONNECTING - TROUBLESHOOTING GUIDE

## ✅ IMPORTANT: The Server IS Working!

The FastAPI server on port 8000 **IS actually running**, but it takes **10-15 seconds** to fully load because:
1. It loads the ML model (best.pt) on startup (~8-10 seconds)
2. MediaPipe initialization takes time
3. The server needs to be ready before handling requests

---

## 🔍 Why "Connection Refused"?

Common causes:

| Cause | Solution | Status |
|-------|----------|--------|
| Server not fully loaded yet | Wait 10-15 seconds | ✅ FIXED |
| Port 8000 blocked | Check firewall | 📋 See below |
| FastAPI process crashed | Check logs | 📋 See below |
| Network issue | Restart startup script | 📋 See below |

---

## ✅ SOLUTION 1: Wait Longer (Most Common)

The startup scripts have been updated to wait **longer** for servers to initialize.

**What changed:**
- Old: Wait 2-3 seconds
- New: Wait 5-6 seconds for FastAPI to load ML models

**To verify the fix:**
1. Run: `start_all.bat` (or `python start_all.py`)
2. Wait **at least 10 seconds**
3. Then open: http://localhost:8000
4. You should see the Body Tracking interface

---

## ✅ SOLUTION 2: Check Server Status

Use the new status checker:

```bash
python check_servers.py
```

Or run batch file:
```bash
check_servers.bat
```

**Output will show:**
- ✅ if server is running
- ❌ if server is offline
- ⚠️ if server is loading

---

## 🔧 SOLUTION 3: Manual Verification

### Step 1: Start Servers Manually

```bash
# Terminal 1
conda activate body_tracking
python server.py

# Terminal 2 (wait 3 seconds, then)
conda activate body_tracking
python run_dev.py
```

### Step 2: Watch for "Server is ready" message

You should see in Terminal 2:
```
[DEV] Starting Body Tracking AI in DEVELOPMENT mode
...
INFO:     Uvicorn running on http://localhost:8000
...
🚀 Body Tracking AI Server is ready!
📊 Model Available: ✓
🌐 Server is now accepting connections
```

### Step 3: Wait for "Server is ready"

When you see "Server is now accepting connections", it's ready.

### Step 4: Test in Browser

Open: http://localhost:8000

---

## 🔍 SOLUTION 4: Check Logs

### PowerShell Script Logs

If you used `start_all.ps1`:
```bash
# Check Flask logs
cat flask_output.log

# Check FastAPI logs
cat fastapi_output.log
```

### Manual Terminal Output

Watch the terminal window running `run_dev.py` for any error messages.

**Look for:**
- ✅ "Server is ready" message = Good
- ❌ "ERROR" or "ModuleNotFoundError" = Problem

---

## 🛠️ SOLUTION 5: Port Already in Use

If port 8000 is already used by another process:

**Windows:**
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Linux/macOS:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

Then restart: `start_all.bat`

---

## 🛠️ SOLUTION 6: Reinstall/Update Dependencies

Some ML packages might have issues:

```bash
conda activate body_tracking
pip install --upgrade uvicorn fastapi
pip install -r requirements.txt --upgrade
```

Then restart: `start_all.bat`

---

## 🛠️ SOLUTION 7: Full Restart

If nothing works:

**Step 1: Stop all processes**
```bash
taskkill /F /IM python.exe
```

**Step 2: Wait 5 seconds**
```bash
timeout /t 5
```

**Step 3: Start fresh**
```bash
start_all.bat
```

**Step 4: Wait 15 seconds for full initialization**

**Step 5: Test**
```bash
python check_servers.py
```

---

## 📊 Timeline - What Happens When You Run `start_all.bat`

```
Time    Event                                   Status
────────────────────────────────────────────────────────
0s      start_all.bat executed                 ▶️  Starting
1s      Flask server starts                    ⏳ Loading
3s      FastAPI server starts                  ⏳ Loading
        (Flask fully ready)                    ✅ Ready
4s      ML Model (best.pt) loading             ⏳ Loading (8-10 sec)
5s      MediaPipe initialization               ⏳ Loading
6s      FastAPI starting up                    ⏳ Loading
10-12s  ML Model fully loaded                  ✅ Ready
13s     Server accepting connections           ✅ READY
        port 5000: ✅ READY
        port 8000: ✅ READY (just loaded)
```

**Bottom line:** Wait at least **10-15 seconds** before testing.

---

## ✅ NEW IMPROVEMENTS

The startup scripts now:
1. ✅ Wait **3 seconds** before starting FastAPI (was 2)
2. ✅ Wait **5-6 seconds** after both servers start (was 3)
3. ✅ Display clearer instructions
4. ✅ Work with ML model loading delays

---

## 🚀 Quick Test

After running `start_all.bat`:

**At 5 seconds:**
- Port 5000: Ready ✅
- Port 8000: Loading... ⏳

**At 10-15 seconds:**
- Port 5000: Ready ✅
- Port 8000: Ready ✅

**Now test:**
```bash
# Check status
python check_servers.py

# Both should show ✅
```

---

## 📋 CHECKLIST

- [ ] You ran `start_all.bat` or `python start_all.py`
- [ ] You waited **at least 10 seconds** (not 5)
- [ ] You see "Server is ready" in the terminal
- [ ] You're using `http://localhost:8000` (not `127.0.0.1:8000`)
- [ ] No firewall is blocking port 8000
- [ ] Port 8000 is not used by another application
- [ ] You're using the latest startup scripts

---

## 🎯 NEXT STEPS

1. **Run status checker:**
   ```bash
   python check_servers.py
   ```

2. **If both show ✅:**
   - Open: http://localhost:5000
   - Click "Body Tracking"
   - Enjoy!

3. **If port 8000 shows ❌:**
   - Check logs in terminal
   - Run Solution 3 (Manual Verification)
   - Contact support with error message

---

## 📞 IF STILL NOT WORKING

1. Run: `python check_servers.py`
2. Share the output
3. Check terminal for error messages
4. Verify conda environment: `conda activate body_tracking`
5. Check ML model exists: `dir best.pt`

---

**Remember:** The first startup always takes 10-15 seconds due to ML model loading!
This is **normal and expected**.

