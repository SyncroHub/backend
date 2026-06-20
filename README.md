# Backend SyncroHUB

Aplicação Python/FastAPI responsável pela API e por servir o frontend localizado
em `../app-cnsonlineprd`.

## Executar com Docker

Pré-requisitos:

- Docker Engine com o plugin Docker Compose;
- o diretório `app-cnsonlineprd` ao lado deste repositório.

A partir da pasta `backend`:

```bash
docker compose up --build --detach
```

A aplicação ficará disponível em:

- Frontend: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/api/health
- Documentação da API: http://127.0.0.1:8000/docs

Para acompanhar os logs e encerrar o serviço:

```bash
docker compose logs --follow backend
docker compose down
```

Copie `.env.example` para `.env` caso precise alterar o nome da aplicação, o
ambiente ou a porta publicada no host:

```bash
cp .env.example .env
```

Dentro do contêiner, o backend sempre escuta em `0.0.0.0:8000`. A variável
`BACKEND_PORT` controla somente a porta publicada no host.

## Testes com Docker

Os testes usam um estágio separado da imagem, com dependências de
desenvolvimento:

```bash
docker compose build test
docker compose run --rm test
```

## Executar localmente

A partir da pasta `backend`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Testes

```bash
pytest
```

## APIs da Visão Geral

Os módulos Financeiro, Faturamento, Compras, Produtos, Pessoa e Venda estão
disponíveis sob `/api/v1`. Os contratos completos, filtros e modelos de
resposta podem ser consultados em `/docs`.

Em desenvolvimento, `DATA_PROVIDER=demo` disponibiliza dados de demonstração.
O Compose usa `totvs` por padrão e exige a URL do proxy interno:

```env
DATA_PROVIDER=totvs
TOTVS_PROXY_URL=http://totvs-proxy/api/v1
TOTVS_PROXY_API_KEY=
TOTVS_PROXY_TIMEOUT=15
```

O proxy deve expor recursos normalizados com os mesmos nomes usados pelas
rotas, por exemplo `financeiro/contas-pagar`, `faturamento`, `compras`,
`produtos`, `pessoa` e `venda/vendas`. A resposta pode ser uma lista JSON ou
um objeto no formato `{"items": [...]}`. Credenciais OAuth da Totvs permanecem
exclusivamente no serviço de proxy.
