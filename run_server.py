#!/usr/bin/env python3
"""
Server launcher script for the Weather Dashboard
Handles proper startup with reload capability
"""

import sys
import os
import subprocess

def main():
    """Launch the weather dashboard server."""
    print("🌤️  Starting Weather Dashboard Server...")
    print("=" * 50)
    
    # Check if uvicorn is available
    try:
        import uvicorn
        print("✅ Uvicorn found, starting with proper reload support...")
        
        # Run with import string for proper reload
        uvicorn.run(
            "backend_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError:
        print("❌ Uvicorn not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn[standard]"])
        
        # Try again
        import uvicorn
        uvicorn.run(
            "backend_server:app",
            host="0.0.0.0", 
            port=8000,
            reload=True,
            log_level="info"
        )

if __name__ == "__main__":
    main()