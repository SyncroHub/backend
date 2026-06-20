from typing import Any, Literal

from fastapi import APIRouter, Depends, Query

from app.api.common import filter_period, paginate, round_money, sort_items
from app.data.gateway import DataGateway, get_data_gateway


router = APIRouter(prefix="/api/v1/faturamento", tags=["faturamento"])

TYPE_BY_OPERATION = {
    "S": "vendas",
    "T": "transf",
    "E": "compra",
    "D": "devolucao",
}


async def _invoices(
    gateway: DataGateway,
    tipo: str | None,
    de: str | None,
    ate: str | None,
) -> list[dict[str, Any]]:
    items = [
        {**item, "tipo": TYPE_BY_OPERATION.get(item["operacao"], "desconhecido")}
        for item in await gateway.list("faturamento")
    ]
    items = filter_period(items, "data_emissao", de, ate)
    if tipo and tipo != "all":
        items = [item for item in items if item["tipo"] == tipo]
    return sort_items(items, None, {}, ("data_emissao", True))


@router.get("")
async def list_invoices(
    tipo: Literal["all", "vendas", "transf", "compra", "devolucao"] = "all",
    de: str | None = None,
    ate: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    return paginate(await _invoices(gateway, tipo, de, ate), page, limit)


@router.get("/summary")
async def invoices_summary(
    de: str | None = None,
    ate: str | None = None,
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, dict[str, float | int]]:
    items = await _invoices(gateway, None, de, ate)
    return {
        tipo: {
            "valor": round_money(
                sum(item["valor"] for item in items if item["tipo"] == tipo)
            ),
            "quantidade": sum(1 for item in items if item["tipo"] == tipo),
        }
        for tipo in ("vendas", "transf", "compra", "devolucao")
    }
