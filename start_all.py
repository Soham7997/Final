#!/usr/bin/env python3
"""
Unified startup script for Drone Tech AI Portal
Runs both server.py (port 5000) and run_dev.py (port 8000) simultaneously
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_servers():
    """Start both servers in parallel"""
    print("=" * 70)
    print("Starting Drone Tech AI Portal - UNIFIED SERVER")
    print("=" * 70)
    print()
    print("📡 Flask Server (Main Portal):  http://localhost:5000")
    print("🎯 FastAPI Server (Body Tracking): http://localhost:8000")
    print()
    print("Press Ctrl+C to stop both servers")
    print("=" * 70)
    print()
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Create processes for both servers
    processes = []
    
    try:
        # Start server.py on port 5000
        print("[1/2] Starting Flask server on port 5000...")
        flask_process = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append(("Flask (Port 5000)", flask_process))
        
        # Wait longer for Flask to initialize
        time.sleep(3)
        
        # Start run_dev.py on port 8000
        print("[2/2] Starting FastAPI server on port 8000...")
        fastapi_process = subprocess.Popen(
            [sys.executable, "run_dev.py"],
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append(("FastAPI (Port 8000)", fastapi_process))
        
        print()
        print("✅ Both servers are starting...")
        print()
        time.sleep(6)  # Wait longer for FastAPI to load ML models
        
        # Monitor both processes
        print("📊 Server Output:")
        print("-" * 70)
        
        while True:
            for name, process in processes:
                if process.poll() is not None:
                    # Process has terminated
                    print(f"\n❌ {name} has stopped!")
                    print("Terminating all servers...")
                    for _, proc in processes:
                        if proc.poll() is None:
                            proc.terminate()
                    return
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("⏹️  Shutting down servers...")
        print("=" * 70)
        
        # Terminate all processes
        for name, process in processes:
            if process.poll() is None:
                print(f"Stopping {name}...")
                process.terminate()
        
        # Wait for processes to terminate
        for name, process in processes:
            try:
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
                process.wait()
        
        print("=" * 70)
        print("All servers stopped")
        print("=" * 70)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        for _, process in processes:
            if process.poll() is None:
                process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    run_servers()
