from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.common import contains_query, distinct, paginate
from app.data.gateway import DataGateway, get_data_gateway


router = APIRouter(prefix="/api/v1/produtos", tags=["produtos"])


@router.get("")
async def list_products(
    q: str | None = None,
    categoria: str | None = None,
    material: str | None = None,
    fornecedor: str | None = None,
    status: Literal["ativo", "inativo"] | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    items = [
        item
        for item in await gateway.list("produtos")
        if contains_query(item, q, ("produto", "referencia", "fornecedor"))
        and (categoria is None or item["categoria"] == categoria)
        and (material is None or item["material"] == material)
        and (fornecedor is None or item["fornecedor"] == fornecedor)
        and (status is None or item["status"] == status)
    ]
    items.sort(key=lambda item: item["produto"])
    return paginate(items, page, limit)


@router.get("/summary")
async def products_summary(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, int]:
    items = await gateway.list("produtos")
    return {
        "total": len(items),
        "ativos": sum(1 for item in items if item["status"] == "ativo"),
        "total_estoque": sum(item["estoque"] for item in items),
        "inativos": sum(1 for item in items if item["status"] == "inativo"),
    }


@router.get("/materiais")
async def product_materials(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, list[str]]:
    return {"items": distinct(await gateway.list("produtos"), "material")}


@router.get("/fornecedores")
async def product_suppliers(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, list[str]]:
    return {"items": distinct(await gateway.list("produtos"), "fornecedor")}


@router.get("/{product_id}")
async def product_detail(
    product_id: str,
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    item = next(
        (
            item
            for item in await gateway.list("produtos")
            if str(item["id"]) == product_id
        ),
        None,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return item
