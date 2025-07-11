#!/usr/bin/env python3
"""
Rick Steves Audio Guide Analysis Dashboard - Streamlit Cloud Deployment

This is the main entry point for Streamlit Cloud deployment.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the dashboard
from load.dashboard import main

if __name__ == "__main__":
    main() 