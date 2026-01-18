@echo off
REM Unified startup script for Drone Tech AI Portal on Windows
REM This script activates the conda environment and runs both servers

echo.
echo ========================================================================
echo   Starting Drone Tech AI Portal - UNIFIED SERVER
echo ========================================================================
echo.
echo   Flask Server (Main Portal):     http://localhost:5000
echo   FastAPI Server (Body Tracking): http://localhost:8000
echo.
echo   Click "Body Tracking" button to switch from port 5000 to 8000
echo.
echo   Press Ctrl+C to stop all servers
echo ========================================================================
echo.

REM Activate conda environment
call conda activate body_tracking

if errorlevel 1 (
    echo Error: Failed to activate body_tracking environment
    echo Make sure you have conda installed and the environment exists
    pause
    exit /b 1
)

REM Start both servers using Python
REM We use start command to run them in parallel
echo Starting Flask server on port 5000...
start "Flask Server (Port 5000)" cmd /k python server.py

timeout /t 3 /nobreak

echo Starting FastAPI server on port 8000...
start "FastAPI Server (Port 8000)" cmd /k python run_dev.py

timeout /t 5 /nobreak

echo.
echo ✓ Both servers are starting in separate windows
echo ✓ Main portal will open on port 5000
echo ✓ Body tracking will open on port 8000 when you click the button
echo.
pause
