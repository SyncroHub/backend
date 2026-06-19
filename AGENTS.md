# Repository Guidelines

## Escopo de Trabalho

Este repositório `backend/` é o diretório padrão para todas as tarefas. Não procure, leia ou altere arquivos em outros diretórios sem solicitação explícita do usuário. A única dependência externa esperada é o frontend estático em `../app-cnsonlineprd`, configurado em `app/config.py`.

## Fluxo Git Obrigatório

Antes de iniciar qualquer tarefa, sincronize a `main` e crie uma branch nova a partir dela:

```bash
git switch main
git pull --ff-only origin main
```

Use sempre um destes prefixos, seguido de uma descrição curta em kebab-case:

```bash
git switch -c fix/nome-da-correcao
git switch -c feat/nome-da-funcionalidade
```

Use `fix/` para correções e `feat/` para funcionalidades, documentação ou melhorias. Nunca implemente diretamente na `main`. Antes de trocar de branch, confirme com `git status` que alterações locais do usuário não serão sobrescritas.

## Estrutura do Projeto

- `app/main.py`: fábrica FastAPI, rotas, CORS e montagem dos arquivos estáticos.
- `app/config.py`: variáveis de ambiente e caminhos da aplicação.
- `tests/test_app.py`: testes de API e integração com o frontend estático.
- `requirements.txt`: dependências de execução e testes.
- `README.md`: instruções de execução local.

Mantenha novas rotas e configurações dentro de `app/`. Testes correspondentes devem ficar em `tests/`.

## Desenvolvimento e Testes

Execute a partir da raiz de `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

O servidor usa `http://127.0.0.1:8000`; o health check está em `/api/health` e a documentação em `/docs`. Execute `pytest` após qualquer alteração. Mudanças de rotas devem testar status, corpo da resposta e casos de erro relevantes.

## Estilo e Convenções

Use Python com quatro espaços, type hints e imports agrupados. Adote `snake_case` para funções e módulos, `PascalCase` para classes e `UPPER_CASE` para constantes. Testes devem seguir `test_<comportamento>`. Prefira funções pequenas e preserve a fábrica `create_app()`.

## Commits e Pull Requests

Use mensagens curtas e imperativas, preferencialmente no padrão Conventional Commits, como `fix: corrige rota de login` ou `feat(api): adiciona endpoint`. Cada commit deve representar uma mudança lógica. Pull requests devem resumir o comportamento, listar os testes executados, vincular issues e informar impactos em configuração. Não versione `.env`, credenciais, ambientes virtuais ou dados de clientes.
