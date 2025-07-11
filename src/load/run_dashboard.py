#!/usr/bin/env python3
"""
Launcher script for the Rick Steves Audio Guide Analysis Dashboard.

This script runs the Streamlit dashboard application with the correct
data file paths and configuration.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit dashboard."""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Path to the dashboard script
    dashboard_script = script_dir / "dashboard.py"
    
    # Check if the dashboard script exists
    if not dashboard_script.exists():
        print(f"Error: Dashboard script not found at {dashboard_script}")
        sys.exit(1)
    
    # Check if data files exist
    metrics_file = script_dir.parent / "transform" / "audio_guide_metrics.json"
    comparison_file = script_dir.parent / "transform" / "museum_comparison.json"
    enhanced_posts_file = script_dir.parent / "transform" / "enhanced_posts.json"
    
    if not metrics_file.exists():
        print(f"Error: Metrics file not found at {metrics_file}")
        sys.exit(1)
    
    if not comparison_file.exists():
        print(f"Error: Comparison file not found at {comparison_file}")
        sys.exit(1)
    
    if not enhanced_posts_file.exists():
        print(f"Error: Enhanced posts file not found at {enhanced_posts_file}")
        sys.exit(1)
    
    print("🎧 Starting Rick Steves Audio Guide Analysis Dashboard...")
    print(f"📊 Metrics data: {metrics_file}")
    print(f"📈 Comparison data: {comparison_file}")
    print(f"📋 Enhanced posts data: {enhanced_posts_file}")
    print("🌐 Opening dashboard in your browser...")
    
    # Run the Streamlit dashboard
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(dashboard_script),
            "--server.port", "8502",
            "--server.address", "localhost"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running dashboard: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except FileNotFoundError:
        print("Error: Streamlit not found. Please install it with: pip install streamlit")
        sys.exit(1)


if __name__ == "__main__":
    main() 