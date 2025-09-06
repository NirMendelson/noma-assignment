#!/usr/bin/env python3
"""
Noma Security Agent Risk Simulator - Main Server

This is the main entry point for the Agent Risk Simulator.
It orchestrates the simulation of blue and red agents to identify
risky behaviors and generate security findings for tradeoff policy discussions.
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from api import app
from config import HOST, PORT, DEBUG, DATA_PATH

def check_data_files():
    """Check if required data files exist"""
    required_files = [
        "agents.csv",
        "actions.csv", 
        "runs.csv",
        "monitoring.csv"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = Path(DATA_PATH) / file
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print("❌ Missing required data files:")
        for file in missing_files:
            print(f"   - {file}")
        print(f"\nPlease ensure all data files are present in the {DATA_PATH} directory.")
        return False
    
    print("✅ All required data files found")
    return True

def print_startup_info():
    """Print startup information"""
    print("\n" + "="*60)
    print("🔒 Noma Security Agent Risk Simulator")
    print("="*60)
    print(f"📊 Data Path: {DATA_PATH}")
    print(f"🌐 Server: http://{HOST}:{PORT}")
    print(f"📚 API Docs: http://{HOST}:{PORT}/docs")
    print(f"🔍 Health Check: http://{HOST}:{PORT}/health")
    print("="*60)
    print("\n🚀 Starting server...")

def main():
    """Main entry point"""
    print_startup_info()
    
    # Check data files
    if not check_data_files():
        sys.exit(1)
    
    # Start the server
    try:
        uvicorn.run(
            "api:app",
            host=HOST,
            port=PORT,
            reload=DEBUG,
            log_level="info" if not DEBUG else "debug"
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
