"""Launcher that explicitly sets sys.path so the preview sandbox can find packages."""
import sys
import os

# Resolve the project root (this file's directory)
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_PKGS = os.path.join(ROOT, ".venv", "lib", "python3.9", "site-packages")

if SITE_PKGS not in sys.path:
    sys.path.insert(0, SITE_PKGS)

# Change working directory to project root so uvicorn finds app.py
os.chdir(ROOT)

import uvicorn
uvicorn.run("app:app", host="0.0.0.0", port=8000, loop="asyncio", http="h11")
