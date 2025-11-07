#!/usr/bin/env python3
"""Startup script for the FastAPI server."""

from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

if __name__ == "__main__":
    import uvicorn

    print("Starting Query Automation Agent FastAPI Server...")
    print("API will be available at: http://127.0.0.1:8000")
    print("Interactive docs at: http://127.0.0.1:8000/docs")
    print("Alternative docs at: http://127.0.0.1:8000/redoc")
    print("\nEndpoints:")
    print("  GET  / - API information")
    print("  GET  /health - Health check")
    print("  POST /query - Process natural language query")
    print("  POST /query/validate - Validate query")
    print("  GET  /schema - Get database schema")
    print("\nPress Ctrl+C to stop the server")

    uvicorn.run(
        "agent_pipeline.api.fastapi_app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
