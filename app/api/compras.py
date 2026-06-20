from collections import Counter
from datetime import date
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query

from app.api.common import as_date, contains_query, paginate, round_money
from app.data.gateway import DataGateway, get_data_gateway


router = APIRouter(prefix="/api/v1/compras", tags=["compras"])


async def _purchases(gateway: DataGateway) -> list[dict[str, Any]]:
    today = date.today()
    result = []
    for item in await gateway.list("compras"):
        pending = max(item["solicitado"] - item["atendido"], 0)
        delayed = (
            (today - as_date(item["limite_entrada"])).days
            if item["status"] not in {"atendido", "cancelado"}
            and as_date(item["limite_entrada"]) < today
            else 0
        )
        result.append({**item, "pendente": pending, "atraso": delayed})
    return result


@router.get("")
async def list_purchases(
    q: str | None = None,
    status: Literal["em_andamento", "parcial", "atendido", "cancelado"] | None = None,
    tipo: Literal["Calçados", "Acessórios"] | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    items = [
        item
        for item in await _purchases(gateway)
        if contains_query(item, q, ("pedido", "fornecedor"))
        and (status is None or item["status"] == status)
        and (tipo is None or item["tipo"] == tipo)
    ]
    items.sort(key=lambda item: item["inclusao"], reverse=True)
    return paginate(items, page, limit)


@router.get("/summary")
async def purchases_summary(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, float | int]:
    items = await _purchases(gateway)
    return {
        "total_valor": round_money(sum(item["valor"] for item in items)),
        "em_andamento": sum(1 for item in items if item["status"] == "em_andamento"),
        "atrasados": sum(1 for item in items if item["atraso"] > 0),
        "fornecedores": len({item["codigo_fornecedor"] for item in items}),
    }


def _distribution(
    items: list[dict[str, Any]], field: str
) -> dict[str, list[dict[str, Any]]]:
    counts = Counter(item[field] for item in items)
    return {
        "items": [
            {field: key, "quantidade": value} for key, value in sorted(counts.items())
        ]
    }


@router.get("/por-status")
async def purchases_by_status(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, list[dict[str, Any]]]:
    return _distribution(await _purchases(gateway), "status")


@router.get("/por-tipo")
async def purchases_by_type(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, list[dict[str, Any]]]:
    return _distribution(await _purchases(gateway), "tipo")
