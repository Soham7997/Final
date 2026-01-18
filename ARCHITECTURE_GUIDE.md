# 🏗️ ARCHITECTURE DIAGRAM

## Before Implementation (2 Commands)

```
User (Terminal 1)              User (Terminal 2)
       |                              |
       ↓                              ↓
   python server.py          python run_dev.py
       |                              |
       ↓                              ↓
Port 5000 (Flask)            Port 8000 (FastAPI)
Main Portal                  Body Tracking Model
│
├─ Dashboard
├─ Object Detection (object.html)
├─ Gender Detection (gender.html)
└─ Body Tracking (body.html) ───X─── Can't reach port 8000 directly
                                      (has to navigate manually)
```

---

## After Implementation (1 Command)

```
User runs: start_all.bat (or .ps1 or .py)
                |
                ↓
        ┌───────────────────┐
        │   Both Servers    │
        │   Start Together  │
        └────────┬──────────┘
                 |
        ┌────────┴──────────┐
        |                   |
        ↓                   ↓
Port 5000 (Flask)    Port 8000 (FastAPI)
Main Portal          Body Tracking Model

┌─────────────────────┐
│ Port 5000 (Flask)   │
├─────────────────────┤
│ • Dashboard         │
│ • Object Detection  │
│ • Gender Detection  │
│ • Body Tracking  ───┼──────────────┐
│   (BUTTON CLICK)    │              │
└─────────────────────┘              │
                                     │
                                     │ Auto-redirect
                                     ↓
                            ┌──────────────────┐
                            │ Port 8000 (Fast) │
                            ├──────────────────┤
                            │ Body Tracking UI │
                            │ (Video feed)     │
                            │ (Pose Detection) │
                            │ (Metrics)        │
                            └──────────────────┘
```

---

## Data Flow

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ Visit: http://localhost:5000
       ↓
┌────────────────────────┐
│   Flask Server         │
│   (Port 5000)          │
│                        │
│ Serves:                │
│ • index.html           │
│ • dashboard.html       │
│ • object.html          │
│ • gender.html          │
│                        │
│ Modified script.js:    │
│ Body button →          │
│ http://localhost:8000  │
└────────────┬───────────┘
             │
             │ User clicks "Body Tracking"
             │
             ↓
┌────────────────────────┐
│ Browser navigates to   │
│ http://localhost:8000  │
└────────────┬───────────┘
             │
             ↓
┌────────────────────────────┐
│   FastAPI Server           │
│   (Port 8000)              │
│                            │
│ Serves:                    │
│ • body.html (via static)   │
│ • body tracking API        │
│ • WebSocket connections    │
│ • Video feed processing    │
│ • Pose detection model     │
└────────────────────────────┘
```

---

## File Dependencies

```
┌─ server.py
│  ├─ Loads: best.pt (YOLO model)
│  ├─ Serves: index.html, dashboard.html, object.html, gender.html
│  ├─ Assets: style.css, script.js (MODIFIED)
│  └─ Port: 5000

┌─ run_dev.py
│  ├─ FastAPI application
│  ├─ Serves: body.html (via /static/)
│  ├─ Assets: styles.css, script.js (from /static/)
│  └─ Port: 8000

┌─ script.js (MODIFIED)
│  ├─ Location: root directory
│  ├─ Change: Line 59
│  ├─ From: body: 'body.html'
│  └─ To: body: 'http://localhost:8000'

┌─ start_all.bat (NEW)
│  ├─ Activates: body_tracking environment
│  ├─ Starts: server.py
│  ├─ Starts: run_dev.py
│  └─ Method: Two separate terminal windows

┌─ start_all.ps1 (NEW)
│  ├─ PowerShell version
│  └─ Same functionality as .bat

┌─ start_all.py (NEW)
│  ├─ Python version
│  └─ Cross-platform compatible
```

---

## Startup Process Timeline

```
Time  Event                           Status
────────────────────────────────────────────────
0s    User executes: start_all.bat   ⏳ Starting
1s    Conda environment activated    ✅ Ready
2s    Flask server (port 5000)       🟢 Launching
3s    Pause for stability            ⏳ Waiting
4s    FastAPI server (port 8000)     🟢 Launching
5s    Both servers ready             ✅ READY
      Browser can access both ports

User clicks "Body Tracking"
      Browser reads: script.js mapping
      Redirects to: http://localhost:8000
      FastAPI serves: body.html
      Model runs: pose detection
```

---

## Port Configuration

```
┌─────────────────────────────────────────┐
│          Network Connections             │
├─────────────────────────────────────────┤
│                                         │
│  localhost:5000 (Flask)                 │
│  ├─ Main Portal UI                      │
│  ├─ Authentication                      │
│  ├─ Dashboard                           │
│  └─ Module Selection                    │
│                                         │
│  localhost:8000 (FastAPI)               │
│  ├─ Body Tracking Interface             │
│  ├─ Video Processing                    │
│  ├─ Pose Detection API                  │
│  └─ WebSocket Connections               │
│                                         │
└─────────────────────────────────────────┘
```

---

## Navigation States

```
STATE 1: Login Page (Port 5000)
┌──────────────────────────┐
│  Drone Tech AI Portal    │
│  └─ Sign In Button       │
│  └─ Log In Button        │
└──────────────────────────┘

STATE 2: Dashboard (Port 5000)
┌──────────────────────────┐
│  Welcome, User!          │
│  ├─ Object Detection ✓   │
│  ├─ Gender Detection ✓   │
│  └─ Body Tracking ✓      │
│     └─ [Open] [Sub]      │
└──────────────────────────┘
         │ CLICK OPEN
         ↓
STATE 3: Body Tracking (Port 8000)
┌──────────────────────────┐
│  Body Tracking AI        │
│  ├─ Video Feed          │
│  ├─ [Start] [Stop]      │
│  └─ Metrics Panel       │
└──────────────────────────┘
         │ Browser Back
         ↓
STATE 2: Dashboard (Port 5000)
```

---

## Process Management

```
start_all.bat (or .ps1 or .py)
        │
        └─→ Check Python & Conda
        │
        └─→ Activate body_tracking environment
        │
        ├─→ Spawn: python server.py
        │   └─→ PID: XXXX (Port 5000)
        │
        ├─→ Wait 2 seconds
        │
        ├─→ Spawn: python run_dev.py
        │   └─→ PID: YYYY (Port 8000)
        │
        └─→ Monitor both processes
            └─→ If either dies: Report & cleanup
            └─→ If user presses Ctrl+C: Graceful shutdown
```

---

## Graceful Shutdown Flow

```
User presses: Ctrl+C

start_all script receives: SIGINT (Interrupt Signal)
        │
        ├─→ Print: "Shutting down servers..."
        │
        ├─→ Send SIGTERM to Flask process
        │   └─→ server.py receives: KeyboardInterrupt
        │   └─→ Closes connections
        │   └─→ Exits cleanly
        │
        ├─→ Send SIGTERM to FastAPI process
        │   └─→ run_dev.py receives: KeyboardInterrupt
        │   └─→ Closes connections
        │   └─→ Exits cleanly
        │
        └─→ Print: "All servers stopped"
            └─→ Exit with code: 0 (success)
```

---

## Minimal Code Change Impact

```
BEFORE (script.js line 59):
─────────────────────────────
const mapping = {
  object: 'object.html',
  gender: 'gender.html',
  body: 'body.html'  ← Points to same server (port 5000)
};

AFTER (script.js line 59):
────────────────────────────
const mapping = {
  object: 'object.html',
  gender: 'gender.html',
  body: 'http://localhost:8000'  ← Points to port 8000 ✅
};

IMPACT:
• Single line changed
• No logic altered
• No new dependencies
• No new files required
• No breaking changes
• All other functionality intact ✅
```

---

**This architecture enables seamless multi-server deployment with minimal code changes!** 🎯
