#!/usr/bin/env python3
"""Script to run the web interface (API + Web UI)"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from interface.api.main import run_api

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Ansible Labs Web Interface")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    args = parser.parse_args()
    
    print(f"Starting Ansible Labs Web Interface...")
    print(f"Server: http://{args.host}:{args.port}")
    print(f"API Docs: http://{args.host}:{args.port}/docs")
    print()
    
    run_api(host=args.host, port=args.port)


