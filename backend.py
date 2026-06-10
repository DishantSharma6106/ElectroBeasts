"""Entrypoint.

Kept so the existing `python backend.py` start command (and render.yaml) keeps
working, but now it actually launches the server and respects $PORT — the
original file defined routes but never started uvicorn, so deploys never came up.
"""
import os

import uvicorn

from app.main import app  # noqa: F401  (re-exported for `uvicorn backend:app`)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
