#!/usr/bin/env python3
"""
Server Status Checker
Verify that both Flask and FastAPI servers are running
"""

import socket
import sys
import time

def check_port(host, port, name):
    """Check if a server is running on the given port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ {name} is RUNNING on {host}:{port}")
            return True
        else:
            print(f"❌ {name} is NOT running on {host}:{port}")
            return False
    except Exception as e:
        print(f"❌ Error checking {name}: {e}")
        return False

def main():
    print("=" * 70)
    print("Server Status Checker")
    print("=" * 70)
    print()
    
    # Check both servers
    flask_ok = check_port("127.0.0.1", 5000, "Flask Server (Port 5000)")
    time.sleep(1)
    fastapi_ok = check_port("127.0.0.1", 8000, "FastAPI Server (Port 8000)")
    
    print()
    print("=" * 70)
    
    if flask_ok and fastapi_ok:
        print("✅ Both servers are ONLINE and READY!")
        print()
        print("Open your browser to:")
        print("  → Main Portal:     http://localhost:5000")
        print("  → Body Tracking:   http://localhost:8000")
        print()
        return 0
    elif flask_ok:
        print("⚠️  Flask server is running, but FastAPI server is not ready yet")
        print("   The ML model is still loading. Please wait 10-15 seconds...")
        print()
        return 1
    elif fastapi_ok:
        print("⚠️  FastAPI server is running, but Flask server is not online")
        print()
        return 1
    else:
        print("❌ Both servers are OFFLINE!")
        print()
        print("Solutions:")
        print("  1. Make sure you ran: start_all.bat (or start_all.py)")
        print("  2. Wait at least 10 seconds for servers to fully initialize")
        print("  3. Check if ports 5000 and 8000 are not blocked")
        print("  4. Check for error messages in the terminal windows")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
