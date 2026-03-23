from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from app.core.config import get_data_path


@lru_cache(maxsize=1)
def load_seed_data() -> dict[str, Any]:
    with get_data_path().open("r", encoding="utf-8") as handle:
        return json.load(handle)
