from re import sub
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.common import contains_query, paginate
from app.data.gateway import DataGateway, get_data_gateway


router = APIRouter(prefix="/api/v1/pessoa", tags=["pessoa"])


def only_digits(value: str) -> str:
    return sub(r"\D", "", value)


def is_valid_cpf(value: str) -> bool:
    cpf = only_digits(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for length in (9, 10):
        total = sum(int(cpf[index]) * (length + 1 - index) for index in range(length))
        digit = (total * 10 % 11) % 10
        if digit != int(cpf[length]):
            return False
    return True


def format_cpf(value: str) -> str:
    cpf = only_digits(value)
    if not is_valid_cpf(cpf):
        raise ValueError("CPF inválido")
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def _normalize_person(item: dict[str, Any]) -> dict[str, Any]:
    try:
        cpf = format_cpf(str(item["cpf"]))
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Pessoa {item.get('id', 'desconhecida')} possui CPF inválido na origem",
        ) from exc
    return {**item, "cpf": cpf}


async def _people(gateway: DataGateway) -> list[dict[str, Any]]:
    return [_normalize_person(item) for item in await gateway.list("pessoa")]


@router.get("")
async def list_people(
    q: str | None = None,
    tipo: Literal["cliente", "fornecedor", "funcionario"] | None = None,
    status: Literal["ativo", "inativo"] | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    items = [
        item
        for item in await _people(gateway)
        if contains_query(item, q, ("nome", "cpf", "email"))
        and (tipo is None or item["tipo"] == tipo)
        and (status is None or item["status"] == status)
    ]
    items.sort(key=lambda item: item["nome"])
    return paginate(items, page, limit)


@router.get("/{person_id}")
async def person_detail(
    person_id: str,
    gateway: DataGateway = Depends(get_data_gateway),
) -> dict[str, Any]:
    item = next(
        (item for item in await _people(gateway) if str(item["id"]) == person_id),
        None,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return item
