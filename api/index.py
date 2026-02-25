"""Vercel serverless entry point.

Vercel looks for `api/index.py` and expects a callable ASGI/WSGI `app`.
We add the backend directory to sys.path so the existing FastAPI app
can be imported unchanged.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402, F401
