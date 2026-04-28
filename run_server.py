"""Launcher that explicitly sets sys.path so the preview sandbox can find packages."""
import sys
import os

# Resolve the project root (this file's directory)
ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(ROOT, ".venv", "bin", "python")
SITE_PKGS = os.path.join(ROOT, ".venv", "lib", "python3.9", "site-packages")

# Re-exec with venv Python if not already running from it
if os.path.exists(VENV_PYTHON) and os.path.abspath(sys.executable) != os.path.abspath(VENV_PYTHON):
    os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

if SITE_PKGS not in sys.path:
    sys.path.insert(0, SITE_PKGS)

# Change working directory to project root so uvicorn finds app.py
os.chdir(ROOT)

# Kill any stale process on port 8000 before binding
import signal
import subprocess
import time

try:
    result = subprocess.run(["lsof", "-ti", ":8000"], capture_output=True, text=True)
    pids = [p for p in result.stdout.strip().split("\n") if p.strip()]
    if pids:
        for pid in pids:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        time.sleep(0.5)
        print(f"[run_server] Killed stale process(es) on :8000 → {', '.join(pids)}")
except Exception:
    pass

import uvicorn
uvicorn.run("app:app", host="0.0.0.0", port=8000, loop="asyncio", http="h11")
