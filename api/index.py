"""Vercel serverless entrypoint - exposes the FastAPI app."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.main import app  # noqa: E402  (Vercel looks for `app` here)
