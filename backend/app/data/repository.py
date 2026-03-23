from __future__ import annotations

from copy import deepcopy

from app.data.seed import load_seed_data


class SeedRepository:
    def __init__(self) -> None:
        self._data = load_seed_data()

    def generated_at(self) -> str:
        return self._data["generated_at"]

    def get_signals(self) -> list[dict]:
        return deepcopy(self._data["signals"])

    def get_patterns(self) -> list[dict]:
        return deepcopy(self._data["patterns"])

    def get_portfolio_demo(self) -> dict:
        return deepcopy(self._data["portfolio_demo"])

    def get_stories(self) -> dict:
        return deepcopy(self._data["stories"])

    def get_ipos(self) -> list[dict]:
        return deepcopy(self._data["ipos"])

    def get_health(self) -> dict:
        return deepcopy(self._data["health"])


repository = SeedRepository()
