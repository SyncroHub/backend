from typing import Any, Literal

from fastapi import APIRouter, Depends, Query

from app.api.common import (
    contains_query,
    distinct,
    filter_period,
    paginate,
    round_money,
    sort_items,
)
from app.data.gateway import DataGateway, get_data_gateway


router = APIRouter(prefix="/api/v1/venda", tags=["venda"])


def _achievement(item: dict[str, Any]) -> dict[str, Any]:
    target = item["meta"]
    return {
        **item,
        "atingimento": round(item["realizado"] * 100 / target, 2) if target else 0.0,
    }


@router.get("/empresas")
async def list_companies(
    q: str | None = None,
    status: Literal["ativo", "inativo"] | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    items = [
        _achievement(item)
        for item in await gateway.list("venda/empresas")
        if contains_query(item, q, ("empresa", "cidade", "uf"))
        and (status is None or item["status"] == status)
    ]
    items.sort(key=lambda item: item["empresa"])
    return paginate(items, page, limit)


@router.get("/vendedores")
async def list_sellers(
    q: str | None = None,
    loja: str | None = None,
    status: Literal["ativo", "inativo"] | None = None,
    order_by: str | None = Query(None, alias="orderBy"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    items = [
        _achievement(item)
        for item in await gateway.list("venda/vendedores")
        if contains_query(item, q, ("vendedor", "loja"))
        and (loja is None or item["loja"] == loja)
        and (status is None or item["status"] == status)
    ]
    items = sort_items(
        items,
        order_by,
        {
            "vendedor": ("vendedor", False),
            "realizado": ("realizado", False),
            "realizado_desc": ("realizado", True),
            "atingimento": ("atingimento", False),
            "atingimento_desc": ("atingimento", True),
        },
        ("vendedor", False),
    )
    return paginate(items, page, limit)


@router.get("/vendedores/summary")
async def sellers_summary(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, float | int]:
    items = await gateway.list("venda/vendedores")
    return {
        "total_realizado": round_money(sum(item["realizado"] for item in items)),
        "count": len(items),
        "ativos": sum(1 for item in items if item["status"] == "ativo"),
        "inativos": sum(1 for item in items if item["status"] == "inativo"),
    }


@router.get("/lojas")
async def seller_stores(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, list[str]]:
    return {"items": distinct(await gateway.list("venda/vendedores"), "loja")}


async def _sales(
    gateway: DataGateway,
    de: str | None,
    ate: str | None,
    tipo: str | None,
    status: str | None,
) -> list[dict[str, Any]]:
    items = filter_period(await gateway.list("venda/vendas"), "data", de, ate)
    items = [
        {
            **item,
            "comissao": round_money(item["comissao_pct"] * item["total"] / 100),
        }
        for item in items
        if (tipo is None or item["tipo"] == tipo)
        and (status is None or item["status"] == status)
    ]
    return sorted(items, key=lambda item: item["data"], reverse=True)


@router.get("/vendas")
async def list_sales(
    de: str | None = None,
    ate: str | None = None,
    tipo: Literal["digital", "fisica"] | None = None,
    status: Literal["confirmada", "pendente", "cancelada"] | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    return paginate(
        await _sales(gateway, de, ate, tipo, status),
        page,
        limit,
    )


@router.get("/vendas/summary")
async def sales_summary(
    de: str | None = None,
    ate: str | None = None,
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, float]:
    items = [
        item
        for item in await _sales(gateway, de, ate, None, None)
        if item["status"] != "cancelada"
    ]
    total = sum(item["total"] for item in items)
    return {
        "digital": round_money(
            sum(item["total"] for item in items if item["tipo"] == "digital")
        ),
        "fisica": round_money(
            sum(item["total"] for item in items if item["tipo"] == "fisica")
        ),
        "comissao_total": round_money(sum(item["comissao"] for item in items)),
        "ticket_medio": round_money(total / len(items)) if items else 0.0,
    }
