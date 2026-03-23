from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "config" / "marketnerve.seed.json"


def get_data_path() -> Path:
    configured = os.getenv("MARKETNERVE_DATA_PATH")
    if configured:
        return Path(configured).resolve()
    return DEFAULT_DATA_PATH


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000")


def get_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "")
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://marketnerve.vercel.app",
    ]
