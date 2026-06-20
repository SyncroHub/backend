# Backend SyncroHUB

Aplicação Python/FastAPI responsável pela API e por servir o frontend localizado
em `../app-cnsonlineprd`.

## Executar com Docker

Pré-requisitos:

- Docker Engine com o plugin Docker Compose;
- o diretório `app-cnsonlineprd` ao lado deste repositório.
- uma variável `JWT_SECRET` longa e aleatória.

A partir da pasta `backend`:

```bash
export JWT_SECRET="$(openssl rand -hex 32)"
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

O Compose também inicia PostgreSQL e Redis. Em produção, mantenha
`AUTO_CREATE_SCHEMA=false` e aplique migrações antes de subir a API:

```bash
docker compose run --rm backend alembic upgrade head
python -m app.seed \
  --credentials-output /diretorio-seguro/credenciais-iniciais.json
```

O seed é idempotente e nunca recria ou redefine senhas de usuários existentes.
O arquivo de credenciais é criado com permissão `0600` e não deve ser
versionado. Consulte `docs/credenciais-iniciais.md`.

## API de usuários

Os endpoints versionados ficam em `/api/v1`:

- `/auth/login`, `/auth/logout`, `/auth/refresh`, `/auth/me` e
  `/auth/change-password`;
- `/users` para paginação, filtros, resumo e CRUD com soft delete;
- `/access-types` para perfis customizados e associações RBAC.

Access tokens expiram em 15 minutos. Refresh tokens opacos expiram em sete
dias e são rotacionados a cada uso. O login aceita no máximo cinco tentativas
por IP a cada minuto.

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
