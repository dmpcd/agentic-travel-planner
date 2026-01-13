#!/usr/bin/env python
"""
Run the Agentic Travel Planner API Server

Usage:
    python run_api.py              # Run in development mode (with reload)
    python run_api.py --prod       # Run in production mode
    python run_api.py --port 3000  # Run on custom port
"""
import argparse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Run the Agentic Travel Planner API"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Run in production mode (no reload)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (production only)"
    )
    
    args = parser.parse_args()
    
    # Print startup banner
    print("\n" + "=" * 60)
    print("🌍 AGENTIC TRAVEL PLANNER API")
    print("=" * 60)
    print(f"Mode: {'PRODUCTION' if args.prod else 'DEVELOPMENT'}")
    print(f"URL: http://{args.host}:{args.port}")
    print(f"Docs: http://{args.host}:{args.port}/docs")
    print("=" * 60 + "\n")
    
    # Run the server
    uvicorn.run(
        "src.api.main:app",
        host=args.host,
        port=args.port,
        reload=not args.prod,
        workers=args.workers if args.prod else 1,
        log_level="info"
    )


if __name__ == "__main__":
    main()
