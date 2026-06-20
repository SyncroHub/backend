from copy import deepcopy
from functools import lru_cache
from typing import Any, Protocol

import httpx

from app.config import settings
from app.data.demo import DEMO_DATA


class DataGateway(Protocol):
    async def list(self, resource: str) -> list[dict[str, Any]]: ...


class DataSourceError(RuntimeError):
    """Falha ao consultar ou interpretar o provedor externo."""


class DemoDataGateway:
    async def list(self, resource: str) -> list[dict[str, Any]]:
        return deepcopy(DEMO_DATA.get(resource, []))


class TotvsProxyDataGateway:
    def __init__(self, base_url: str, api_key: str | None, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    async def list(self, resource: str) -> list[dict[str, Any]]:
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/{resource.lstrip('/')}",
                    headers=headers,
                )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise DataSourceError(
                f"Falha ao consultar o recurso normalizado {resource}"
            ) from exc
        items = payload.get("items") if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise DataSourceError(f"Resposta inválida do proxy para {resource}")
        return items


@lru_cache
def get_data_gateway() -> DataGateway:
    provider = settings.data_provider.lower()
    if provider == "demo":
        return DemoDataGateway()
    if provider == "totvs" and settings.totvs_proxy_url:
        return TotvsProxyDataGateway(
            settings.totvs_proxy_url,
            settings.totvs_proxy_api_key,
            settings.totvs_proxy_timeout,
        )
    raise DataSourceError(
        "DATA_PROVIDER deve ser 'demo' ou 'totvs' com TOTVS_PROXY_URL configurada"
    )
