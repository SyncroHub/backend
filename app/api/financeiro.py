from datetime import date, timedelta
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query

from app.api.common import (
    as_date,
    contains_query,
    distinct,
    filter_period,
    paginate,
    round_money,
    sort_items,
)
from app.data.gateway import DataGateway, get_data_gateway


router = APIRouter(prefix="/api/v1/financeiro", tags=["financeiro"])


def _payable_status(item: dict[str, Any]) -> str:
    if item.get("pago"):
        return "pago"
    return "vencido" if as_date(item["vencimento"]) <= date.today() else "a_vencer"


async def _payables(gateway: DataGateway) -> list[dict[str, Any]]:
    items = await gateway.list("financeiro/contas-pagar")
    return [{**item, "status": _payable_status(item)} for item in items]


@router.get("/contas-pagar")
async def list_payables(
    q: str | None = None,
    status: Literal["a_vencer", "vencido", "pago"] | None = None,
    order_by: str | None = Query(None, alias="orderBy"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    items = [
        item
        for item in await _payables(gateway)
        if contains_query(item, q, ("duplicata", "fornecedor"))
        and (status is None or item["status"] == status)
    ]
    items = sort_items(
        items,
        order_by,
        {
            "vencimento": ("vencimento", False),
            "vencimento_desc": ("vencimento", True),
            "valor": ("valor", False),
            "valor_desc": ("valor", True),
            "fornecedor": ("fornecedor", False),
        },
        ("vencimento", False),
    )
    return paginate(items, page, limit)


@router.get("/contas-pagar/summary")
async def payables_summary(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, float]:
    items = await _payables(gateway)
    today = date.today()
    week_end = today + timedelta(days=7)
    month_end = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    open_items = [item for item in items if item["status"] != "pago"]
    return {
        "total_aberto": round_money(sum(item["valor"] for item in open_items)),
        "vence_hoje": round_money(
            sum(
                item["valor"]
                for item in open_items
                if as_date(item["vencimento"]) == today
            )
        ),
        "semana": round_money(
            sum(
                item["valor"]
                for item in open_items
                if today <= as_date(item["vencimento"]) <= week_end
            )
        ),
        "mes": round_money(
            sum(
                item["valor"]
                for item in open_items
                if today <= as_date(item["vencimento"]) < month_end
            )
        ),
    }


@router.get("/contas-receber")
async def list_receivables(
    tipo: str | None = None,
    status: Literal["a_vencer", "vencido", "pago"] | None = None,
    order_by: str | None = Query(None, alias="orderBy"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    items = [
        item
        for item in await gateway.list("financeiro/contas-receber")
        if (tipo is None or item["tipo"] == tipo)
        and (status is None or item["status"] == status)
    ]
    items = sort_items(
        items,
        order_by,
        {
            "vencimento": ("vencimento", False),
            "vencimento_desc": ("vencimento", True),
            "valor": ("valor", False),
            "valor_desc": ("valor", True),
            "cliente": ("cliente", False),
        },
        ("vencimento", False),
    )
    return paginate(items, page, limit)


@router.get("/contas-receber/summary")
async def receivables_summary(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, float]:
    items = [
        item
        for item in await gateway.list("financeiro/contas-receber")
        if item["status"] != "pago"
    ]
    card_types = {"Cartão de Crédito", "Cartão de Débito"}
    return {
        "total": round_money(sum(item["valor"] for item in items)),
        "cartao": round_money(
            sum(item["valor"] for item in items if item["tipo"] in card_types)
        ),
        "outros": round_money(
            sum(item["valor"] for item in items if item["tipo"] not in card_types)
        ),
    }


@router.get("/lancamentos-caixa")
async def list_cash_entries(
    q: str | None = None,
    loja: str | None = None,
    despesa: str | None = None,
    order_by: str | None = Query(None, alias="orderBy"),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, list[dict[str, Any]]]:
    items = [
        item
        for item in await gateway.list("financeiro/lancamentos-caixa")
        if contains_query(item, q, ("duplicata", "fornecedor"))
        and (loja is None or item["loja"] == loja)
        and (despesa is None or item["despesa"] == despesa)
    ]
    items = sort_items(
        items,
        order_by,
        {
            "data": ("data", False),
            "data_desc": ("data", True),
            "valor": ("valor_original", False),
            "valor_desc": ("valor_original", True),
            "fornecedor": ("fornecedor", False),
        },
        ("data", True),
    )
    return {"items": items}


@router.get("/lancamentos-caixa/lojas")
async def cash_entry_stores(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, list[str]]:
    return {
        "items": distinct(await gateway.list("financeiro/lancamentos-caixa"), "loja")
    }


@router.get("/lancamentos-caixa/despesas")
async def cash_entry_expenses(
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, list[str]]:
    return {
        "items": distinct(
            await gateway.list("financeiro/lancamentos-caixa"),
            "despesa",
        )
    }


async def _bank_balances(
    gateway: DataGateway,
    start: str | None,
    end: str | None,
) -> list[dict[str, Any]]:
    return filter_period(
        await gateway.list("financeiro/saldo-banco"),
        "data",
        start,
        end,
    )


@router.get("/saldo-banco")
async def list_bank_balances(
    de: str | None = None,
    ate: str | None = None,
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, list[dict[str, Any]]]:
    items = await _bank_balances(gateway, de, ate)
    total = sum(item["saldo"] for item in items)
    enriched = [
        {
            **item,
            "percentual_total": round(item["saldo"] * 100 / total, 2) if total else 0.0,
        }
        for item in sorted(items, key=lambda item: item["saldo"], reverse=True)
    ]
    return {"items": enriched}


@router.get("/saldo-banco/summary")
async def bank_balances_summary(
    de: str | None = None,
    ate: str | None = None,
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, float | int]:
    items = await _bank_balances(gateway, de, ate)
    balances = [item["saldo"] for item in items]
    return {
        "saldo_total": round_money(sum(balances)),
        "maior_saldo": round_money(max(balances, default=0.0)),
        "empresas": len({item["empresa"] for item in items}),
    }
