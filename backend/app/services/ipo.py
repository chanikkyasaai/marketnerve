from __future__ import annotations

from app.data.repository import repository
from app.models.schemas import IpoInsight


def _demand_label(subscription_multiple: float) -> str:
    if subscription_multiple >= 10:
        return "Hot demand"
    if subscription_multiple >= 5:
        return "Healthy demand"
    if subscription_multiple >= 2:
        return "Measured demand"
    return "Subdued demand"


def _risk_level(gmp: int, subscription_multiple: float) -> str:
    if gmp >= 100 and subscription_multiple >= 10:
        return "Aggressive"
    if gmp >= 40 or subscription_multiple >= 5:
        return "Balanced"
    return "Cautious"


def _to_ipo_insight(item: dict) -> IpoInsight:
    return IpoInsight(
        name=item["name"],
        gmp=item["gmp"],
        subscription_multiple=item["subscription_multiple"],
        allotment_probability=item["allotment_probability"],
        demand_label=_demand_label(item["subscription_multiple"]),
        risk_level=_risk_level(item["gmp"], item["subscription_multiple"]),
        summary=item["summary"],
        cutoff_price=item.get("cutoff_price"),
        listing_date=item.get("listing_date"),
    )


def list_active_ipos() -> list[IpoInsight]:
    return sorted(
        [_to_ipo_insight(item) for item in repository.get_ipos()],
        key=lambda ipo: (-ipo.subscription_multiple, -ipo.gmp),
    )


def get_ipo_by_name(name: str) -> IpoInsight:
    normalized = name.lower().replace("-", " ").replace("_", " ")
    for item in repository.get_ipos():
        if normalized in item["name"].lower():
            return _to_ipo_insight(item)
    raise KeyError(name)
