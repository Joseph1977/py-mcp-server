#!/usr/bin/env python
import uvicorn
from app.config import settings # Import settings
import subprocess # For running main.py directly
import sys # For passing arguments

if __name__ == "__main__":
    if settings.MCP_TRANSPORT_MODE == "stdio":
        # Run app/main.py directly for stdio mode
        # Pass any command line arguments from run.py to main.py
        process = subprocess.Popen([sys.executable, "app/main.py"] + sys.argv[1:], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        process.wait()
    else:
        # Default to HTTP/SSE mode using Uvicorn
        uvicorn.run("app.main:app", host=settings.MCP_SERVER_HOST, port=settings.MCP_SERVER_PORT, reload=True)
