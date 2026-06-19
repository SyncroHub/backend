# Backend SyncroHUB

Aplicação Python/FastAPI responsável pela API e por servir o frontend localizado
em `../app-cnsonlineprd`.

## Executar

A partir da pasta `backend`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A aplicação ficará disponível em:

- Frontend: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/api/health
- Documentação da API: http://127.0.0.1:8000/docs

## Testes

```bash
pytest
```

