#!/usr/bin/env python3
"""Script to run the TUI interface"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from interface.tui.main import run_tui

if __name__ == "__main__":
    # Default API URL, can be overridden with environment variable
    import os
    api_url = os.getenv("ANSIBLE_LABS_API_URL", "http://localhost:8000")
    
    print(f"Starting Ansible Labs TUI...")
    print(f"API URL: {api_url}")
    print("Make sure the API server is running (run_web.py or interface/api/main.py)")
    print()
    
    run_tui(api_url=api_url)


