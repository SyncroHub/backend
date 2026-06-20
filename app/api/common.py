from collections.abc import Iterable
from datetime import date, datetime
from typing import Any
import unicodedata

from fastapi import HTTPException


def normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in text if not unicodedata.combining(char)).lower()


def contains_query(
    item: dict[str, Any], query: str | None, fields: Iterable[str]
) -> bool:
    if not query:
        return True
    needle = normalize(query)
    return any(needle in normalize(item.get(field)) for field in fields)


def parse_iso_date(value: str | None, field_name: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} deve usar o formato YYYY-MM-DD",
        ) from exc


def as_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def filter_period(
    items: list[dict[str, Any]],
    field: str,
    start: str | None,
    end: str | None,
) -> list[dict[str, Any]]:
    start_date = parse_iso_date(start, "de")
    end_date = parse_iso_date(end, "ate")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="de não pode ser posterior a ate")
    return [
        item
        for item in items
        if (start_date is None or as_date(item[field]) >= start_date)
        and (end_date is None or as_date(item[field]) <= end_date)
    ]


def sort_items(
    items: list[dict[str, Any]],
    order_by: str | None,
    allowed: dict[str, tuple[str, bool]],
    default: tuple[str, bool] | None = None,
) -> list[dict[str, Any]]:
    selected = default if order_by is None else allowed.get(order_by)
    if selected is None:
        if order_by:
            raise HTTPException(status_code=422, detail="orderBy inválido")
        return items
    field, descending = selected
    return sorted(
        items,
        key=lambda item: (item.get(field) is None, item.get(field)),
        reverse=descending,
    )


def paginate(items: list[dict[str, Any]], page: int, limit: int) -> dict[str, Any]:
    total = len(items)
    start = (page - 1) * limit
    return {
        "items": items[start : start + limit],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if total else 0,
        },
    }


def distinct(items: list[dict[str, Any]], field: str) -> list[str]:
    return sorted({str(item[field]) for item in items if item.get(field)})


def round_money(value: float) -> float:
    return round(value, 2)
