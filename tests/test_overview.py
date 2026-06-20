from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.api.pessoa import format_cpf, is_valid_cpf
from app.data.gateway import DataSourceError, get_data_gateway
from app.main import app


client = TestClient(app)


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/financeiro/contas-pagar",
        "/api/v1/financeiro/contas-pagar/summary",
        "/api/v1/financeiro/contas-receber",
        "/api/v1/financeiro/contas-receber/summary",
        "/api/v1/financeiro/lancamentos-caixa",
        "/api/v1/financeiro/lancamentos-caixa/lojas",
        "/api/v1/financeiro/lancamentos-caixa/despesas",
        "/api/v1/financeiro/saldo-banco",
        "/api/v1/financeiro/saldo-banco/summary",
        "/api/v1/faturamento",
        "/api/v1/faturamento/summary",
        "/api/v1/compras",
        "/api/v1/compras/summary",
        "/api/v1/compras/por-status",
        "/api/v1/compras/por-tipo",
        "/api/v1/produtos",
        "/api/v1/produtos/summary",
        "/api/v1/produtos/materiais",
        "/api/v1/produtos/fornecedores",
        "/api/v1/produtos/prd-1",
        "/api/v1/pessoa",
        "/api/v1/pessoa/pes-1",
        "/api/v1/venda/empresas",
        "/api/v1/venda/vendedores",
        "/api/v1/venda/vendedores/summary",
        "/api/v1/venda/lojas",
        "/api/v1/venda/vendas",
        "/api/v1/venda/vendas/summary",
    ],
)
def test_overview_endpoint_is_available(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200, response.text


def test_payables_apply_dynamic_status_search_and_pagination() -> None:
    response = client.get(
        "/api/v1/financeiro/contas-pagar",
        params={"q": "Calçados", "status": "vencido", "page": 1, "limit": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"] == {"page": 1, "limit": 1, "total": 1, "pages": 1}
    assert payload["items"][0]["status"] == "vencido"


def test_bank_balance_percentages_total_one_hundred() -> None:
    response = client.get("/api/v1/financeiro/saldo-banco")

    percentages = sum(item["percentual_total"] for item in response.json()["items"])
    assert percentages == pytest.approx(100.0, abs=0.02)


def test_invoice_type_mapping_and_summary() -> None:
    listing = client.get("/api/v1/faturamento", params={"tipo": "devolucao"})
    summary = client.get("/api/v1/faturamento/summary")

    assert {item["tipo"] for item in listing.json()["items"]} == {"devolucao"}
    assert summary.json()["vendas"] == {"valor": 899.9, "quantidade": 1}


def test_purchase_calculates_pending_and_delay() -> None:
    response = client.get("/api/v1/compras", params={"status": "parcial"})

    purchase = response.json()["items"][0]
    assert purchase["pendente"] == 20
    assert purchase["atraso"] >= 2


def test_products_filters_and_returns_detail() -> None:
    listing = client.get(
        "/api/v1/produtos",
        params={"q": "runner", "categoria": "Tênis", "status": "ativo"},
    )
    detail = client.get("/api/v1/produtos/prd-1")

    assert listing.json()["pagination"]["total"] == 1
    assert detail.json()["referencia"] == "TEN-001"
    assert client.get("/api/v1/produtos/inexistente").status_code == 404


def test_people_format_cpf_and_include_modal_data() -> None:
    listing = client.get("/api/v1/pessoa", params={"q": "529.982"})
    detail = client.get("/api/v1/pessoa/pes-1")

    assert listing.json()["items"][0]["cpf"] == "529.982.247-25"
    assert detail.json()["endereco"]["uf"] == "SP"
    assert detail.json()["historico_compras"]


@pytest.mark.parametrize(
    ("cpf", "valid"),
    [("529.982.247-25", True), ("111.111.111-11", False), ("123", False)],
)
def test_cpf_validation(cpf: str, valid: bool) -> None:
    assert is_valid_cpf(cpf) is valid


def test_cpf_format_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        format_cpf("111.111.111-11")


def test_sales_calculations_and_company_achievement() -> None:
    sales = client.get("/api/v1/venda/vendas/summary").json()
    companies = client.get("/api/v1/venda/empresas").json()["items"]

    assert sales["digital"] == 589.8
    assert sales["fisica"] == 219.9
    assert sales["comissao_total"] == 38.29
    assert sales["ticket_medio"] == 269.9
    assert companies[0]["atingimento"] == 92.0


def test_period_validation() -> None:
    response = client.get(
        "/api/v1/faturamento",
        params={"de": date.today().isoformat(), "ate": "2020-01-01"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "de não pode ser posterior a ate"


def test_pagination_validation() -> None:
    assert client.get("/api/v1/produtos", params={"page": 0}).status_code == 422
    assert client.get("/api/v1/produtos", params={"limit": 101}).status_code == 422


def test_invalid_order_is_rejected() -> None:
    response = client.get(
        "/api/v1/financeiro/contas-pagar",
        params={"orderBy": "campo_inexistente"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "orderBy inválido"


def test_data_source_failure_returns_bad_gateway() -> None:
    class FailingGateway:
        async def list(self, resource: str) -> list[dict[str, object]]:
            raise DataSourceError(resource)

    app.dependency_overrides[get_data_gateway] = lambda: FailingGateway()
    try:
        response = client.get("/api/v1/produtos")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"] == "Provedor de dados indisponível"
