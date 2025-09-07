import os
import sys
from typing import AsyncIterator

import pytest
from httpx import AsyncClient
from httpx import ASGITransport

# === Import app ===
TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
REPO_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))

for path in (BACKEND_DIR, REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

# Robust FastAPI app import
_app = None
try:
    from app.main import app as _app
except Exception as e1:
    try:
        from backend.app.main import app as _app
    except Exception as e2:
        raise ImportError(
            f"Failed to import FastAPI app\nError 1: {e1}\nError 2: {e2}"
        )

# === Fixtures ===

@pytest.fixture(scope="session")
def use_live_server() -> bool:
    return os.getenv("USE_LIVE_SERVER", "0") == "1"

@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "http://127.0.0.1:8000")

@pytest.fixture
async def client(use_live_server: bool, base_url: str) -> AsyncIterator[AsyncClient]:
    if use_live_server:
        async with AsyncClient(base_url=base_url, timeout=20.0) as ac:
            yield ac
    else:
        # ✅ Updated approach using ASGITransport for in-process testing
        transport = ASGITransport(app=_app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac