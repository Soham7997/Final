# Unified startup script for Drone Tech AI Portal - PowerShell version
# This script activates the conda environment and runs both servers

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "   Starting Drone Tech AI Portal - UNIFIED SERVER" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Flask Server (Main Portal):     http://localhost:5000" -ForegroundColor Green
Write-Host "   FastAPI Server (Body Tracking): http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "   Click 'Body Tracking' button to switch from port 5000 to 8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if conda is available
try {
    $condaPath = (Get-Command conda).Source
    Write-Host "✓ Conda found at: $condaPath" -ForegroundColor Green
} catch {
    Write-Host "✗ Conda not found. Please install Anaconda or Miniconda." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate conda environment
Write-Host "Activating conda environment: body_tracking" -ForegroundColor Yellow
& conda activate body_tracking

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Error: Failed to activate body_tracking environment" -ForegroundColor Red
    Write-Host "Make sure you have the environment created" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Environment activated" -ForegroundColor Green
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Flask server in background
Write-Host "[1/2] Starting Flask server on port 5000..." -ForegroundColor Cyan
$flaskProcess = Start-Process -FilePath "python" -ArgumentList "server.py" `
    -WorkingDirectory $scriptDir `
    -NoNewWindow -PassThru `
    -RedirectStandardOutput "$scriptDir\flask_output.log" `
    -RedirectStandardError "$scriptDir\flask_error.log"

Start-Sleep -Seconds 3

# Start FastAPI server in background
Write-Host "[2/2] Starting FastAPI server on port 8000..." -ForegroundColor Cyan
$fastAPIProcess = Start-Process -FilePath "python" -ArgumentList "run_dev.py" `
    -WorkingDirectory $scriptDir `
    -NoNewWindow -PassThru `
    -RedirectStandardOutput "$scriptDir\fastapi_output.log" `
    -RedirectStandardError "$scriptDir\fastapi_error.log"

Write-Host ""
Write-Host "✓ Both servers are starting..." -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 6

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "✓ Servers are ready!" -ForegroundColor Green
Write-Host ""
Write-Host "   → Open your browser: http://localhost:5000" -ForegroundColor Green
Write-Host "   → Login and click 'Body Tracking'" -ForegroundColor Green
Write-Host "   → You'll be redirected to: http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Monitoring servers... Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Monitor both processes
try {
    while ($true) {
        # Check if Flask process is still running
        if ($flaskProcess.HasExited) {
            Write-Host "✗ Flask server has stopped!" -ForegroundColor Red
            break
        }
        
        # Check if FastAPI process is still running
        if ($fastAPIProcess.HasExited) {
            Write-Host "✗ FastAPI server has stopped!" -ForegroundColor Red
            break
        }
        
        Start-Sleep -Seconds 2
    }
} catch {
    Write-Host "Monitoring interrupted" -ForegroundColor Yellow
} finally {
    Write-Host ""
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "Shutting down servers..." -ForegroundColor Yellow
    
    # Terminate processes
    if (!$flaskProcess.HasExited) {
        $flaskProcess.Kill()
        Write-Host "✓ Flask server stopped" -ForegroundColor Green
    }
    
    if (!$fastAPIProcess.HasExited) {
        $fastAPIProcess.Kill()
        Write-Host "✓ FastAPI server stopped" -ForegroundColor Green
    }
    
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "All servers stopped" -ForegroundColor Green
}
