# Tarefas de Backend no Trello

Fonte: [App - Gestão CnSOnline](https://trello.com/b/hnL7VmQm/app-gest%C3%A3o-cnsonline)

Extraído em 19 de junho de 2026 às 19:59.

## Critério de seleção

Foram incluídos os épicos e cards relacionados a backend, APIs, integração
com Totvs Moda, banco de dados, segurança, DevOps e infraestrutura.
Cards exclusivamente de frontend foram excluídos. Cópias arquivadas foram
deduplicadas; cards arquivados aparecem somente quando não há equivalente
na estrutura ativa do quadro.

## Resumo

| Grupo | Quantidade |
| --- | ---: |
| Backlog — Épicos | 5 |
| Sprint 1 — Backend: Módulo Usuários | 6 |
| Sprint 1 — Backend: Conexão API Totvs | 4 |
| Sprint 1 — Infraestrutura | 8 |
| Sprint 2 — Backend: Importar Pedidos | 4 |
| Sprint 3 — Backend: Visão Geral (APIs de Dados) | 6 |
| **Total** | **33** |

## Backlog — Épicos

### [ÉPICO] Sprint 1 — Módulo de Usuários: Autenticação e CRUD

- **Lista:** Backlog — Épicos
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/4AvZqu2B/99-%C3%A9pico-sprint-1-m%C3%B3dulo-de-usu%C3%A1rios-autentica%C3%A7%C3%A3o-e-crud)
- **Última atividade:** 17 de jun. de 2026, 10:55

#### Descrição

Épico que cobre todo o ciclo de vida dos usuários próprios do SaaS CnSOnline: autenticação, CRUD, RBAC e tipos de acesso.

**CONTEXTO TÉCNICO ATUAL:**
- Usuários armazenados em `localStorage` (chave `adm_usuarios_mock` em state.js)
- Sessão via `sessionStorage` (chave `adm_user` em auth.js)
- 35 usuários seed (USR_SEED) com senhas em texto puro (`senha:'1234'`)
- Nenhum backend real — toda lógica de permissão está no frontend

**TIPOS DE USUÁRIO:** super_admin (nível 5), supervisao_geral (4), supervisao_regional (3), financeiro/compras/rh_pessoal/administrativo/gerador_cotas/prev_receber/gerador_compras (3), loja/pdv (1)

### [ÉPICO] Sprint 1 — Conexão API Totvs Moda: OAuth2 Seguro

- **Lista:** Backlog — Épicos
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/5YSx6ypJ/100-%C3%A9pico-sprint-1-conex%C3%A3o-api-totvs-moda-oauth2-seguro)
- **Etiquetas:** label-critico
- **Última atividade:** 17 de jun. de 2026, 10:55

#### Descrição

Épico que cobre a integração OAuth2 com a API do Totvs Moda.

**PROBLEMA CRÍTICO DE SEGURANÇA (conexao-api.js):**
- `client_id`, `client_secret`, `username`, `password` e `access_token` armazenados em `localStorage`
- O fluxo OAuth2 Password Grant acontece diretamente no browser
- O access_token é exibido visualmente na tela

**RESOLUÇÃO:** Todo esse fluxo deve ocorrer exclusivamente no backend.

### [ÉPICO] Sprint 1 — Infraestrutura: Setup do Backend SaaS

- **Lista:** Backlog — Épicos
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/0omONf9E/101-%C3%A9pico-sprint-1-infraestrutura-setup-do-backend-saas)
- **Última atividade:** 17 de jun. de 2026, 10:55

#### Descrição

Épico de infraestrutura para suportar os módulos de Usuários e Conexão API Totvs.

**STACK RECOMENDADA:**
- Runtime: Node.js + TypeScript
- Framework: NestJS ou Fastify
- ORM: Prisma
- Banco: PostgreSQL
- Cache/Blacklist JWT: Redis
- Containerização: Docker + Docker Compose

### [ÉPICO] Sprint 2 — Módulo de Importação de Pedidos CSV → Totvs

- **Lista:** Backlog — Épicos
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/4y1R8qDZ/102-%C3%A9pico-sprint-2-m%C3%B3dulo-de-importa%C3%A7%C3%A3o-de-pedidos-csv-%E2%86%92-totvs)
- **Etiquetas:** label-sprint2
- **Última atividade:** 17 de jun. de 2026, 10:55

#### Descrição

Épico que cobre o módulo operacional de Importar Pedidos (retaguarda/pages/importar.html).

**FLUXO ATUAL (3 passos no frontend):**
1. **Carregar CSV** — upload de `pedidos_postman.csv` (gerado pelo converter.py)
2. **Revisar Pedidos** — tabela de preview com: Nr. Pedido Fornecedor, Filial, Cód. Forn., Fornecedor, Data Pedido, Previsão Entrega, Prazo Limite, Itens, Total (R$)
3. **Enviar para Totvs** — barra de progresso, log em tempo real, estatísticas de ok/erros

**DEPENDÊNCIAS CRÍTICAS:**
- BKAT-002 (proxy OAuth2 Totvs) deve estar pronto
- BKAT-003 (proxy de requisições Totvs) deve estar pronto
- O envio dos pedidos usa o mesmo Bearer token gerenciado pelo vault

**PROBLEMA ATUAL:** A lógica de envio chama a API Totvs diretamente do browser, expondo o token. Deve ser migrada para o backend via proxy.

### [ÉPICO] Sprint 3 — Visão Geral: Integração das 6 Páginas de Dados

- **Lista:** Backlog — Épicos
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/0l2jjVjq/103-%C3%A9pico-sprint-3-vis%C3%A3o-geral-integra%C3%A7%C3%A3o-das-6-p%C3%A1ginas-de-dados)
- **Última atividade:** 17 de jun. de 2026, 10:55

#### Descrição

Épico que cobre a integração das 6 páginas de dados da seção 'Visão Geral' com APIs reais do backend.

**PÁGINAS:**
- **Financeiro** — Contas a Pagar, Contas a Receber, Lançamentos Caixa, Saldo Banco
- **Faturamento** — Notas fiscais (vendas, transferências, compras, devoluções)
- **Pedidos de Compra** — Pedidos por status, fornecedor, tipo; gráficos de status e tipos de produto
- **Produtos** — Cadastro de produtos com estoque, preços e status
- **Pessoa** — Clientes, fornecedores e funcionários com modal de detalhes
- **Venda** — Empresas (meta/realizado), Vendedores e Vendas (digital + física)

**STATUS ATUAL:** Todas essas páginas usam dados mock hardcoded no JavaScript. Devem ser migradas para consumir APIs reais que obtêm dados via proxy Totvs.


## Sprint 1 — Backend: Módulo Usuários

### [BKU-001] Modelagem do Banco de Dados — Entidade Usuário

- **Lista:** Sprint 1 — Backend: Módulo Usuários
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/FapXCP0I/93-bku-001-modelagem-do-banco-de-dados-entidade-usu%C3%A1rio)
- **Etiquetas:** label-banco
- **Última atividade:** 17 de jun. de 2026, 10:54

#### Descrição

Criar o schema/modelo da entidade User com todos os campos identificados no frontend.

**CAMPOS DA ENTIDADE USER:**
- `id` UUID (PK)
- `nome` VARCHAR(255) NOT NULL
- `email` VARCHAR(255) UNIQUE NOT NULL
- `senha_hash` VARCHAR(255) NOT NULL
- `tipo` ENUM (super_admin, supervisao_geral, supervisao_regional, loja, pdv, financeiro, compras, rh_pessoal, administrativo, gerador_cotas, prev_receber, gerador_compras)
- `cargo` VARCHAR(100)
- `nivel` INTEGER (super_admin=5, supervisao_geral=4, supervisao_regional=3, outros=1-3)
- `ativo` BOOLEAN DEFAULT true
- `force_password_change` BOOLEAN DEFAULT false
- `loja_id` UUID FK NULL
- `created_at`, `updated_at`, `deleted_at` TIMESTAMP

**OBSERVAÇÃO:** Os 35 usuários seed têm senha='1234' em texto puro. Devem ser migrados com bcrypt e force_password_change=true.

#### Checklists

**Tarefas de Implementação**

- [ ] Definir SGBD: PostgreSQL
- [ ] Criar migração: tabela users com todos os campos mapeados
- [ ] Criar enum tipo_usuario com os 12 tipos
- [ ] Criar migração: tabela lojas (id, nome, cidade, uf, ativo)
- [ ] Criar migração: tabela tipos_acesso (id, nome, descricao, cor, ativo, sistema)
- [ ] Criar migração: tabela users_tipos_acesso (pivot: user_id, tipo_acesso_id)
- [ ] Criar migração: tabela modulos_catalogo (19 módulos do sistema)
- [ ] Criar migração: tabela funcs_catalogo (16 funções de permissão)
- [ ] Criar migração: tabela rels_catalogo (25 relatórios)
- [ ] Documentar diagrama ER

### [BKU-002] API de Autenticação — Login / Logout / Refresh / Me

- **Lista:** Sprint 1 — Backend: Módulo Usuários
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/CkaZCdE8/94-bku-002-api-de-autentica%C3%A7%C3%A3o-login-logout-refresh-me)
- **Etiquetas:** label-seguranca
- **Última atividade:** 17 de jun. de 2026, 10:54

#### Descrição

Implementar endpoints de autenticação própria do SaaS (independente do ERP).

**ENDPOINTS A CRIAR:**
- `POST /api/v1/auth/login` — email + senha → JWT
- `POST /api/v1/auth/logout` — invalida refresh_token
- `POST /api/v1/auth/refresh` — rotação do refresh_token
- `GET /api/v1/auth/me` — dados do usuário logado (sem senha_hash)
- `POST /api/v1/auth/change-password` — obrigatório para force_password_change=true

**SEGURANÇA JWT:**
- access_token: expiração 15 minutos
- refresh_token: opaco, expiração 7 dias, armazenado em banco para blacklist
- Rotação obrigatória do refresh_token a cada uso

#### Checklists

**Tarefas de Implementação**

- [ ] Implementar hash de senha com bcrypt (mínimo 12 rounds)
- [ ] Gerar JWT access_token com expiração de 15 minutos
- [ ] Gerar refresh_token opaco com expiração de 7 dias
- [ ] Criar tabela refresh_tokens para blacklist/rotação
- [ ] Endpoint POST /api/v1/auth/login (email + senha)
- [ ] Endpoint POST /api/v1/auth/logout (invalida refresh_token atual)
- [ ] Endpoint POST /api/v1/auth/refresh (rotação obrigatória do refresh_token)
- [ ] Endpoint GET /api/v1/auth/me (retorna dados sem senha_hash)
- [ ] Endpoint POST /api/v1/auth/change-password
- [ ] Rate-limiting: máximo 5 tentativas de login por IP por minuto (Redis counter)
- [ ] Testes de integração para todos os endpoints
- [ ] Teste: verificar que senha_hash nunca aparece em nenhum response

### [BKU-003] CRUD de Usuários — Endpoints REST

- **Lista:** Sprint 1 — Backend: Módulo Usuários
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/I7VGtHnP/95-bku-003-crud-de-usu%C3%A1rios-endpoints-rest)
- **Etiquetas:** label-crud
- **Última atividade:** 17 de jun. de 2026, 10:54

#### Descrição

Implementar os endpoints REST para gerenciamento de usuários.

**REGRAS DE NEGÓCIO:**
- Apenas usuários com permissão `usuarios_criar` podem criar usuários
- Apenas usuários com permissão `usuarios_editar` podem editar e remover
- Um usuário só pode criar/editar usuários com nível MENOR que o seu
- super_admin (nível 5) pode gerenciar todos

**PAGINAÇÃO:** A listagem atual é client-side (_usrPerPage=15). Deve ser convertida para server-side com parâmetros page e limit.

#### Checklists

**Endpoints a Implementar**

- [ ] GET /api/v1/users?page=1&limit=15&tipo=&status=&tiposAcesso=&q= (paginação server-side)
- [ ] GET /api/v1/users/summary (métricas: total, admins, supervisoes, lojas, inativos)
- [ ] GET /api/v1/users/:id
- [ ] POST /api/v1/users (criar usuário — requer permissão usuarios_criar)
- [ ] PUT /api/v1/users/:id (editar — requer permissão usuarios_editar)
- [ ] PATCH /api/v1/users/:id/status (ativar/desativar — requer permissão usuarios_desativar)
- [ ] DELETE /api/v1/users/:id (soft delete — requer permissão usuarios_editar)
- [ ] Middleware de autorização: verificar permissão antes de cada operação
- [ ] Middleware de hierarquia: impedir edição de usuário com nível >= o do solicitante
- [ ] Validação: email único (retornar 409 Conflict com mensagem clara)
- [ ] Validação: senha com política mínima (8 chars, maiúscula, número, símbolo)
- [ ] Nunca retornar senha_hash em nenhum response
- [ ] Testes de autorização RBAC (tentar operações sem permissão → 403)

### [BKU-004] Sistema de Permissões RBAC — Backend

- **Lista:** Sprint 1 — Backend: Módulo Usuários
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/sDHJ9rDw/96-bku-004-sistema-de-permiss%C3%B5es-rbac-backend)
- **Etiquetas:** label-seguranca
- **Última atividade:** 17 de jun. de 2026, 10:54

#### Descrição

Implementar o sistema RBAC no backend espelhando a lógica do frontend (tipos-acesso.js).

**SISTEMA ATUAL NO FRONTEND:**
- 19 módulos em MODULOS_CATALOGO
- 16 funções em FUNCS_CATALOGO (ex: usuarios_criar, usuarios_editar, conexao_api_editar)
- 25 relatórios em RELS_CATALOGO
- 13 tipos de acesso em TIPOS_ACESSO (sistema=true, não editáveis)

**IMPLEMENTAÇÃO NO BACKEND:**
- O JWT deve incluir no payload os funcIds do usuário
- Um middleware `checkPermission('codigo_funcao')` deve ser aplicado nos endpoints
- Nunca confiar em permissões enviadas pelo cliente

#### Checklists

**Tarefas de Implementação**

- [ ] Criar tabela permissions com os 16 códigos de funcionalidade
- [ ] Criar tabela role_permissions associando tipos_acesso às permissions
- [ ] Implementar middleware checkPermission(codigoFuncao) reutilizável
- [ ] Seed: popular os 13 tipos de acesso do sistema (sistema=true)
- [ ] Seed: popular os 16 funcs do catálogo
- [ ] Seed: popular os 25 relatórios do catálogo
- [ ] Seed: popular os 19 módulos do catálogo
- [ ] Teste: super_admin passa em TODAS as permissões
- [ ] Teste: usuário sem tiposAcesso recebe 403 em endpoints protegidos
- [ ] Teste: usuário com tipo='loja' não acessa endpoints administrativos

### [BKU-005] CRUD de Tipos de Acesso (Perfis) — Backend

- **Lista:** Sprint 1 — Backend: Módulo Usuários
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/BcGRRJTZ/97-bku-005-crud-de-tipos-de-acesso-perfis-backend)
- **Etiquetas:** label-crud
- **Última atividade:** 17 de jun. de 2026, 10:55

#### Descrição

Implementar endpoints para gerenciamento dos tipos_acesso.

**REGRAS DE NEGÓCIO:**
- 13 perfis seed (sistema=true) NÃO podem ser removidos via API
- Perfis customizados (sistema=false) podem ser criados, editados e removidos
- Apenas usuários com permissão `tipos_acesso_gerenciar` podem acessar
- Impedir remoção se houver usuários vinculados
- Nome deve ser único (case-insensitive)

#### Checklists

**Endpoints a Implementar**

- [ ] GET /api/v1/access-types (listar todos)
- [ ] POST /api/v1/access-types (criar perfil customizado)
- [ ] PUT /api/v1/access-types/:id (editar — impedir se sistema=true para campos protegidos)
- [ ] DELETE /api/v1/access-types/:id (impedir se sistema=true)
- [ ] PATCH /api/v1/access-types/:id/status (ativar/desativar)
- [ ] Validação: nome único case-insensitive
- [ ] Validação: impedir remoção se houver usuários vinculados (retornar contagem no erro 409)

### [BKU-006] Migração de Dados Mock → Banco Real

- **Lista:** Sprint 1 — Backend: Módulo Usuários
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/AU0oIdOh/98-bku-006-migra%C3%A7%C3%A3o-de-dados-mock-%E2%86%92-banco-real)
- **Etiquetas:** label-seguranca, label-banco
- **Última atividade:** 17 de jun. de 2026, 10:55

#### Descrição

Criar scripts de seed e migração para levar os dados do USR_SEED para o banco de dados.

**ATENÇÃO CRÍTICA DE SEGURANÇA:**
Os 33 usuários PDV do USR_SEED têm `senha:'1234'` em texto puro. ISSO NÃO PODE SER MIGRADO COMO ESTÁ.

**ESTRATÉGIA DE MIGRAÇÃO:**
1. Gerar senhas temporárias aleatórias e seguras (mínimo 12 chars) para cada usuário
2. Aplicar bcrypt (12 rounds) em todas as senhas
3. Setar `force_password_change=true` para todos os usuários migrados
4. Documentar senhas temporárias de forma segura (vault, não em código-fonte)
5. Comunicar os super_admins sobre as credenciais iniciais por canal seguro

#### Checklists

**Tarefas de Migração**

- [ ] Script de seed: criar as 32 lojas do LOJAS (state.js)
- [ ] Script de seed: criar os 19 módulos do MODULOS_CATALOGO
- [ ] Script de seed: criar as 16 funções do FUNCS_CATALOGO
- [ ] Script de seed: criar os 25 relatórios do RELS_CATALOGO
- [ ] Script de seed: criar os 13 tipos_acesso do sistema
- [ ] Script de seed: criar os 35 usuários do USR_SEED com bcrypt (12 rounds)
- [ ] Gerar senhas temporárias aleatórias para todos os usuários PDV (nunca '1234')
- [ ] Setar force_password_change=true para todos os usuários migrados
- [ ] Criar endpoint POST /api/v1/auth/change-password
- [ ] Documentar processo de distribuição de credenciais iniciais com segurança
- [ ] Testar que nenhum usuário consegue logar sem trocar a senha temporária


## Sprint 1 — Backend: Conexão API Totvs

### [BKAT-001] Vault Seguro para Credenciais Totvs Moda — CRÍTICO DE SEGURANÇA

- **Lista:** Sprint 1 — Backend: Conexão API Totvs
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/AJqfKUnG/85-bkat-001-vault-seguro-para-credenciais-totvs-moda-cr%C3%ADtico-de-seguran%C3%A7a)
- **Etiquetas:** label-seguranca, label-critico, label-banco
- **Última atividade:** 17 de jun. de 2026, 10:53

#### Descrição

**TAREFA CRÍTICA DE SEGURANÇA.**

**PROBLEMA ATUAL (conexao-api.js):**
client_secret, password e access_token salvos em localStorage (chave 'totvs_config'). Qualquer script na mesma origem pode ler tudo isso.

**SOLUÇÃO:**
- Criar tabela `totvs_configurations` no banco de dados
- Criptografar client_secret, password e token com AES-256-GCM
- Chave de criptografia exclusivamente via variável de ambiente ENCRYPTION_KEY
- A API NUNCA deve retornar client_secret, password ou token em texto puro

#### Checklists

**Schema da Tabela**

- [ ] Criar migração: tabela totvs_configurations
- [ ] Campos: id, tenant_id, endpoint, client_id, client_secret_enc, username, password_enc
- [ ] Campos: modulos_json, order_defaults_json, delay_ms (default 500), retries (default 2)
- [ ] Campos: status (enum: conectado, desconectado, erro), token_enc, token_type, expires_at
- [ ] Campos: last_connected_at, status_msg, created_at, updated_at

**Implementação do Vault**

- [ ] Implementar utilitário de criptografia AES-256-GCM
- [ ] Chave de criptografia via variável de ambiente ENCRYPTION_KEY (nunca no código)
- [ ] Endpoint GET /api/v1/totvs/config — retornar client_secret e password SEMPRE mascarados
- [ ] Endpoint PUT /api/v1/totvs/config — receber, criptografar e salvar
- [ ] Middleware: apenas usuários com permissão 'conexao_api_editar' acessam
- [ ] Nunca logar client_secret, password ou token em nenhum log
- [ ] Teste: verificar que GET /api/v1/totvs/config nunca retorna secrets em texto puro
- [ ] Teste: verificar que colunas _enc no banco não são decifráveis sem a ENCRYPTION_KEY

### [BKAT-002] Proxy OAuth2 Totvs — Autenticação Exclusivamente no Backend

- **Lista:** Sprint 1 — Backend: Conexão API Totvs
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/4YUOntjf/86-bkat-002-proxy-oauth2-totvs-autentica%C3%A7%C3%A3o-exclusivamente-no-backend)
- **Etiquetas:** label-seguranca, label-critico
- **Última atividade:** 17 de jun. de 2026, 10:53

#### Descrição

Mover o fluxo OAuth2 Password Grant para o backend.

**PROBLEMA ATUAL (conexao-api.js):** O browser faz fetch() diretamente para o endpoint da Totvs com client_secret exposto, causando também erro de CORS.

**SOLUÇÃO:**
- Endpoint `POST /api/v1/totvs/connect` no backend
- Backend lê credenciais do vault (BKAT-001), não do body da requisição
- Executa o OAuth2 server-side
- Retorna ao frontend APENAS: `{ status, expires_at, token_type, last_connected_at, message }`

#### Checklists

**Tarefas de Implementação**

- [ ] Endpoint POST /api/v1/totvs/connect (disparar autenticação OAuth2 server-side)
- [ ] Ler credenciais do vault — NUNCA do body da requisição
- [ ] Executar POST OAuth2 com grant_type=password para o endpoint da Totvs
- [ ] Armazenar access_token criptografado (AES-256-GCM) no banco
- [ ] Calcular e salvar expires_at = now + expires_in segundos
- [ ] Retornar ao frontend apenas: { status, expires_at, token_type, last_connected_at }
- [ ] Rate-limiting: máximo 10 tentativas de conexão por minuto por tenant
- [ ] Renovação automática: se token expira em menos de 2 minutos, renovar automaticamente
- [ ] Log de auditoria: registrar tentativa, resultado, timestamp (sem dados sensíveis)
- [ ] Tratamento de erros Totvs: mapear error_description para mensagens em português
- [ ] Teste: verificar que o frontend não recebe o access_token em nenhuma resposta

### [BKAT-003] Proxy de Requisições para Módulos da API Totvs

- **Lista:** Sprint 1 — Backend: Conexão API Totvs
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/vOKvX6M6/87-bkat-003-proxy-de-requisi%C3%A7%C3%B5es-para-m%C3%B3dulos-da-api-totvs)
- **Última atividade:** 17 de jun. de 2026, 10:53

#### Descrição

Criar endpoints proxy que encapsulam as chamadas aos módulos da API Totvs.

**MÓDULOS DA API TOTVS:** vendas, estoque, clientes, produtos, financeiro, vendedores

**FLUXO DO PROXY:**
1. Frontend chama o endpoint proxy do backend
2. Backend recupera o token do vault (decripta)
3. Backend verifica validade do token (se expirado, renova via BKAT-002)
4. Backend faz a requisição para a API Totvs com o Bearer token
5. Backend retorna a resposta para o frontend (sem expor o token)

#### Checklists

**Tarefas de Implementação**

- [ ] Middleware de injeção de Bearer token (recuperar do vault, verificar e renovar se necessário)
- [ ] Endpoint GET /api/v1/totvs/proxy/purchase-orders (importação de pedidos de compra)
- [ ] Implementar retry com backoff exponencial (respeitar valor de retries: 0, 1, 2 ou 3)
- [ ] Implementar delay configurável entre requisições (respeitar delay_ms, máximo 5000ms)
- [ ] Timeout por requisição: 30 segundos
- [ ] Log de auditoria: status HTTP, tempo de resposta, erros — sem logar payload completo
- [ ] Tratamento de token expirado mid-request: renovar e retentar automaticamente
- [ ] Endpoint GET /api/v1/totvs/modules-status (listar módulos e seus estados)

### [BKAT-004] Configurações de Pedido (Valores Padrão) — Backend

- **Lista:** Sprint 1 — Backend: Conexão API Totvs
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/yjxU7Wmp/88-bkat-004-configura%C3%A7%C3%B5es-de-pedido-valores-padr%C3%A3o-backend)
- **Última atividade:** 17 de jun. de 2026, 10:53

#### Descrição

Migrar os valores padrão de pedido do localStorage para o banco de dados.

**CAMPOS DO FORMULÁRIO (configuracoes.html):**
- `cfgBranch` → Cód. Filial Padrão
- `cfgBuyer` → Cód. Comprador Padrão
- `cfgOperation` → Cód. Operação Padrão
- `cfgPayCond` → Cód. Cond. Pagamento
- `cfgPayType` → Tipo de Pagamento
- `cfgFreight` → Tipo de Frete
- `cfgDelay` → Delay entre requisições (ms)
- `cfgRetries` → Tentativas em caso de erro (select: 0,1,2,3)

#### Checklists

**Endpoints a Implementar**

- [ ] GET /api/v1/totvs/order-defaults — retornar valores padrão do tenant
- [ ] PUT /api/v1/totvs/order-defaults — salvar valores padrão
- [ ] Campos: branchCode, buyerCode, operationCode, payCondCode, payType, freightType (integer)
- [ ] Campos: delayMs (0-5000), retries (0-3)
- [ ] Validações: valores numéricos, ranges corretos
- [ ] Apenas usuários com permissão 'conexao_api_editar' podem alterar


## Sprint 1 — Infraestrutura

### [INF-001] Definição de Stack e Arquitetura do Backend

- **Lista:** Sprint 1 — Infraestrutura
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/rEvkgHSY/77-inf-001-defini%C3%A7%C3%A3o-de-stack-e-arquitetura-do-backend)
- **Última atividade:** 17 de jun. de 2026, 10:52

#### Descrição

Definir e documentar a stack tecnológica do backend SaaS CnSOnline.

**STACK RECOMENDADA:**
- Runtime: Node.js 20 LTS + TypeScript 5
- Framework: NestJS (estrutura modular, DI, guards para RBAC) ou Fastify
- ORM: Prisma (type-safe migrations)
- Banco: PostgreSQL 15+
- Cache/Blacklist JWT: Redis 7

**DECISÕES ARQUITETURAIS:**
- Monolito modular para início
- Versionamento de API: /api/v1/
- Multi-tenant preparado desde o início (tenant_id nas tabelas principais)

#### Checklists

**Decisões e Setup**

- [ ] Escolher e documentar framework backend (NestJS ou Fastify)
- [ ] Definir ORM (Prisma recomendado) e configurar
- [ ] Definir estrutura de pastas do projeto
- [ ] Criar repositório git do backend
- [ ] Configurar TypeScript com strict mode
- [ ] Configurar ESLint + Prettier
- [ ] Documentar ADRs para as principais decisões técnicas
- [ ] Definir convenção de resposta de erro padrão { statusCode, message, errors[] }

### [INF-002] Ambiente de Desenvolvimento com Docker Compose

- **Lista:** Infraestrutura (arquivada)
- **Status:** arquivado
- **Trello:** [abrir card](https://trello.com/c/NiDQjY3j/22-inf-002-ambiente-de-desenvolvimento-com-docker-compose)
- **Última atividade:** 17 de jun. de 2026, 09:49

#### Descrição

Criar ambiente de desenvolvimento local reproduzível.

**SERVIÇOS DO DOCKER COMPOSE:**
- `backend` — aplicação Node.js/TypeScript
- `postgres` — PostgreSQL 15 com volume persistente
- `redis` — Redis 7 para blacklist de tokens JWT
- `adminer` — interface web para o banco (apenas dev)

**VARIÁVEIS DE AMBIENTE MÍNIMAS (.env.example):**
```
DATABASE_URL=postgresql://user:pass@localhost:5432/syncro
REDIS_URL=redis://localhost:6379
JWT_SECRET=<mínimo 256 bits de entropia>
JWT_REFRESH_SECRET=<mínimo 256 bits de entropia>
ENCRYPTION_KEY=<32 bytes hex — para AES-256-GCM do vault Totvs>
PORT=3000
CORS_ORIGINS=http://localhost:8080
```

### [INF-003] Gestão de Segredos e Variáveis de Ambiente

- **Lista:** Sprint 1 — Infraestrutura
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/QhGE7zL7/78-inf-003-gest%C3%A3o-de-segredos-e-vari%C3%A1veis-de-ambiente)
- **Etiquetas:** label-seguranca
- **Última atividade:** 17 de jun. de 2026, 10:52

#### Descrição

Definir e implementar a estratégia de gestão de segredos.

**VARIÁVEIS CRÍTICAS:**
- `DATABASE_URL`, `JWT_SECRET`, `JWT_REFRESH_SECRET`
- `ENCRYPTION_KEY` — chave AES-256-GCM para o vault de credenciais Totvs (32 bytes hex)
- `REDIS_URL`, `CORS_ORIGINS`

**REGRA DE OURO:** A aplicação deve falhar imediatamente na inicialização se qualquer variável obrigatória estiver ausente.

#### Checklists

**Tarefas de Implementação**

- [ ] Definir ferramenta de gestão de segredos para produção (AWS Secrets Manager ou equivalente)
- [ ] Configurar .gitignore: .env, .env.local, .env.*.local, *.key
- [ ] Criar .env.example com TODAS as variáveis documentadas (sem valores reais)
- [ ] Implementar validação de variáveis na inicialização (ex: Zod schema ou class-validator)
- [ ] A aplicação deve lançar exceção e parar se ENCRYPTION_KEY, JWT_SECRET ou DATABASE_URL estiverem ausentes
- [ ] Definir política de rotação de chaves (ENCRYPTION_KEY, JWT_SECRET)
- [ ] Documentar impacto da rotação: JWT_SECRET → invalidar todos os access_tokens

### [INF-004] HTTPS, CORS e Headers de Segurança HTTP

- **Lista:** Sprint 1 — Infraestrutura
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/8T4eaRMt/79-inf-004-https-cors-e-headers-de-seguran%C3%A7a-http)
- **Etiquetas:** label-seguranca
- **Última atividade:** 17 de jun. de 2026, 10:52

#### Descrição

Garantir HTTPS e configurar headers de segurança.

**CORS DA API PRÓPRIA:**
- Whitelist de origens do frontend SaaS
- Sem wildcard (*) em produção
- Credentials: true (para cookies httpOnly do refresh_token)

**HEADERS DE SEGURANÇA:** Content-Security-Policy, HSTS, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Referrer-Policy

#### Checklists

**Tarefas de Implementação**

- [ ] Certificado SSL/TLS para domínio da API (Let's Encrypt ou equivalente)
- [ ] Configurar CORS: whitelist de origens (nunca * em produção)
- [ ] CORS credentials: true (necessário para cookies httpOnly do refresh_token)
- [ ] Configurar Helmet.js: todos os headers de segurança recomendados
- [ ] HSTS: preload, includeSubDomains, max-age mínimo 1 ano
- [ ] Configurar proxy reverso Nginx ou Caddy
- [ ] Redirecionar HTTP→HTTPS com 301

### [INF-005] Pipeline CI/CD — Backend

- **Lista:** Infraestrutura (arquivada)
- **Status:** arquivado
- **Trello:** [abrir card](https://trello.com/c/WNuQ8UJC/25-inf-005-pipeline-ci-cd-backend)
- **Última atividade:** 17 de jun. de 2026, 09:49

#### Descrição

Configurar pipeline de integração e entrega contínua.

**STAGES DO PIPELINE:**
1. `lint` — ESLint + type-check TypeScript
2. `test:unit` — testes unitários
3. `test:integration` — testes de integração com PostgreSQL e Redis reais (não mocks)
4. `build` — compilar TypeScript
5. `deploy:staging` — deploy automático ao merge em `develop`
6. `deploy:production` — deploy manual com aprovação ao merge em `main`

**COBERTURA MÍNIMA:** 80% de linhas em testes unitários.

### [INF-006] Observabilidade — Logs Estruturados e Auditoria

- **Lista:** Sprint 1 — Infraestrutura
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/Uqij0mfw/80-inf-006-observabilidade-logs-estruturados-e-auditoria)
- **Etiquetas:** label-seguranca
- **Última atividade:** 17 de jun. de 2026, 10:52

#### Descrição

Implementar logging estruturado e auditoria de segurança.

**EVENTOS QUE DEVEM SER AUDITADOS:**
- Login: quem, quando, IP, user-agent, sucesso ou falha
- CRUD de usuários: quem fez, o que mudou, quando
- Configuração Totvs: quem, quando
- Acessos negados (403)

**NUNCA LOGAR:** Senhas, tokens, client_secret, password Totvs

#### Checklists

**Tarefas de Implementação**

- [ ] Implementar logging estruturado em JSON (Pino ou Winston)
- [ ] Níveis de log: error, warn, info, debug
- [ ] Criar tabela audit_logs: user_id, action, entity, entity_id, ip, user_agent, created_at
- [ ] Middleware de auditoria para endpoints sensíveis (auth, users, totvs/config)
- [ ] Definir lista de campos PROIBIDOS de logar (senha, token, client_secret, etc.)
- [ ] Integrar Sentry (ou equivalente) para monitoramento de erros em produção
- [ ] Alertas: múltiplas falhas de login por IP (possível ataque de força bruta)

### [INF-007] Política de Segurança de Autenticação

- **Lista:** Sprint 1 — Infraestrutura
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/HxWzhbmG/81-inf-007-pol%C3%ADtica-de-seguran%C3%A7a-de-autentica%C3%A7%C3%A3o)
- **Etiquetas:** label-seguranca
- **Última atividade:** 17 de jun. de 2026, 10:52

#### Descrição

Implementar políticas de proteção do sistema de autenticação.

**POLÍTICAS A IMPLEMENTAR:**
- Rate-limiting: 5 tentativas de login por IP por 15 minutos (Redis)
- Bloqueio de conta: 10 tentativas falhas → lockout de 30 minutos
- Política de senha: mínimo 8 chars, 1 maiúscula, 1 minúscula, 1 número, 1 símbolo
- force_password_change: todos os usuários seed devem trocar na primeira autenticação

#### Checklists

**Políticas de Segurança**

- [ ] Rate-limiting no /api/v1/auth/login: 5 tentativas por IP por 15 minutos (Redis)
- [ ] Bloqueio temporário de conta após 10 falhas consecutivas (30 minutos)
- [ ] Política de senha mínima: 8 chars, 1 maiúscula, 1 minúscula, 1 número, 1 símbolo
- [ ] Validar política no backend (não confiar na validação client-side)
- [ ] Endpoint POST /api/v1/auth/change-password com verificação da senha atual
- [ ] Bloquear login se force_password_change=true e redirecionar para troca de senha
- [ ] Endpoint POST /api/v1/auth/logout-all — invalida todos os refresh_tokens do usuário
- [ ] Invalidar todos os refresh_tokens ao trocar a senha
- [ ] Registrar todos os eventos de autenticação na tabela audit_logs

### [INF-008] Banco de Dados — Estratégia de Backup e Recovery

- **Lista:** Infraestrutura (arquivada)
- **Status:** arquivado
- **Trello:** [abrir card](https://trello.com/c/u6iGQche/28-inf-008-banco-de-dados-estrat%C3%A9gia-de-backup-e-recovery)
- **Última atividade:** 17 de jun. de 2026, 09:49

#### Descrição

Implementar estratégia de backup para o PostgreSQL de produção.

**REQUISITOS MÍNIMOS:**
- Backup automático diário
- Retenção de 30 dias
- Backup offsite (bucket S3 ou equivalente)
- Processo de restore documentado e testado


## Sprint 2 — Backend: Importar Pedidos

### [IMP-001] Endpoint de Recebimento e Validação do CSV

- **Lista:** Sprint 2 — Backend: Importar Pedidos
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/wqnzMdte/73-imp-001-endpoint-de-recebimento-e-valida%C3%A7%C3%A3o-do-csv)
- **Etiquetas:** label-crud, label-sprint2
- **Última atividade:** 17 de jun. de 2026, 10:52

#### Descrição

Criar o endpoint backend que recebe o arquivo CSV (`pedidos_postman.csv`) gerado pelo `converter.py` e retorna o preview dos pedidos para o frontend.

**ESTRUTURA DO CSV (colunas esperadas):**
- nr_pedido_fornecedor, filial, cod_fornecedor, ds_fornecedor
- data_pedido, previsao_entrega, prazo_limite
- itens (JSON serializado ou campo com contagem)
- total_valor (decimal com ponto como separador)

**REGRAS DE VALIDAÇÃO:**
- Verificar presença de todas as colunas obrigatórias
- Verificar formato das datas (DD/MM/YYYY ou ISO)
- Verificar que total_valor é número positivo
- Verificar que nr_pedido_fornecedor é único no arquivo
- Retornar lista de erros com número da linha em caso de falha de validação

**DEPENDÊNCIAS:** BKAT-002 e BKAT-003 devem estar prontos.

#### Checklists

**Tarefas de Implementação**

- [ ] Endpoint POST /api/v1/importar/upload (multipart/form-data)
- [ ] Parser de CSV: separador vírgula, decimal ponto (conforme importar.html)
- [ ] Validar estrutura: colunas obrigatórias presentes
- [ ] Validar dados: formatos de data, valores numéricos positivos, pedidos únicos
- [ ] Retornar preview: lista de pedidos parseados com todos os campos da tabela
- [ ] Retornar erros: lista de linhas com problema e descrição do erro
- [ ] Limitar tamanho: máximo 10MB por arquivo
- [ ] Armazenar CSV temporariamente (Redis com TTL de 30 min) para uso no Step 3
- [ ] Endpoint DELETE /api/v1/importar/cancelar (limpar CSV da sessão)

### [IMP-002] Serviço de Envio de Pedidos para Totvs via Proxy

- **Lista:** Sprint 2 — Backend: Importar Pedidos
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/Gt9ZzVtX/74-imp-002-servi%C3%A7o-de-envio-de-pedidos-para-totvs-via-proxy)
- **Etiquetas:** label-sprint2
- **Última atividade:** 17 de jun. de 2026, 10:52

#### Descrição

Implementar o serviço que processa e envia os pedidos de compra para a API Totvs, usando o proxy seguro (BKAT-003).

**FLUXO DE ENVIO:**
1. Frontend dispara POST /api/v1/importar/executar com a lista de pedidos confirmados
2. Backend processa um pedido por vez, respeitando delay_ms e retries das configurações
3. Para cada pedido: recuperar token do vault → fazer POST para Totvs → registrar resultado
4. Progresso disponível via polling GET /api/v1/importar/progresso/:jobId
5. Ao finalizar: retornar relatório com total/ok/erros

**CONFIGURAÇÕES USADAS (de totvs_configurations):**
- branchCode (Cód. Filial Padrão)
- buyerCode (Cód. Comprador Padrão)
- operationCode (Cód. Operação Padrão)
- payCondCode, payType, freightType
- delayMs (delay entre pedidos)
- retries (tentativas por pedido)

#### Checklists

**Tarefas de Implementação**

- [ ] Endpoint POST /api/v1/importar/executar (iniciar processamento dos pedidos)
- [ ] Criar job assíncrono: processar um pedido por vez com delay e retry configurados
- [ ] Recuperar token do vault a cada pedido (verificar validade, renovar se necessário)
- [ ] Endpoint GET /api/v1/importar/progresso/:jobId (polling: total/ok/erros/pedido_atual)
- [ ] Aplicar delay entre pedidos (respeitar delayMs de BKAT-004)
- [ ] Implementar retry com backoff exponencial por pedido (respeitar retries de BKAT-004)
- [ ] Endpoint DELETE /api/v1/importar/cancelar/:jobId (interromper job em andamento)
- [ ] Registrar cada pedido enviado na tabela import_logs
- [ ] Timeout por pedido individual: 30 segundos
- [ ] Tratamento de erros Totvs: mapear respostas de erro para mensagens legíveis

### [IMP-003] Banco de Dados — Histórico e Log de Importações

- **Lista:** Sprint 2 — Backend: Importar Pedidos
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/J3sX95pb/75-imp-003-banco-de-dados-hist%C3%B3rico-e-log-de-importa%C3%A7%C3%B5es)
- **Etiquetas:** label-sprint2, label-banco
- **Última atividade:** 17 de jun. de 2026, 10:52

#### Descrição

Criar as tabelas para persistir o histórico de importações e os logs de execução.

**TABELAS A CRIAR:**

`import_sessions` — Uma entrada por importação iniciada:
- id UUID, user_id FK, started_at, finished_at, status (pendente/executando/concluido/cancelado/erro)
- total_pedidos, ok_pedidos, erro_pedidos
- arquivo_nome, arquivo_tamanho

`import_logs` — Uma entrada por pedido processado:
- id UUID, session_id FK
- nr_pedido_fornecedor, filial, cod_fornecedor, ds_fornecedor
- total_valor, status (ok/erro), mensagem_erro
- tentativas, tempo_ms, created_at

#### Checklists

**Tarefas de Implementação**

- [ ] Criar migração: tabela import_sessions com todos os campos
- [ ] Criar migração: tabela import_logs com referência à sessão
- [ ] Endpoint GET /api/v1/importar/historico (listar sessões com paginação)
- [ ] Endpoint GET /api/v1/importar/historico/:id (detalhe de uma sessão com logs)
- [ ] Seed de exemplo com dados mock para testes (session + logs)
- [ ] Índices: import_logs.session_id, import_sessions.user_id, import_sessions.started_at

### [IMP-004] Validações de Negócio dos Pedidos de Compra

- **Lista:** Sprint 2 — Backend: Importar Pedidos
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/q22Bl8sf/76-imp-004-valida%C3%A7%C3%B5es-de-neg%C3%B3cio-dos-pedidos-de-compra)
- **Etiquetas:** label-sprint2
- **Última atividade:** 17 de jun. de 2026, 10:52

#### Descrição

Implementar validações específicas de negócio antes do envio para a Totvs.

**VALIDAÇÕES NECESSÁRIAS:**
- Filial (branchCode) deve existir no cadastro de lojas do sistema
- Cód. Fornecedor deve ser validado (se existir API Totvs para consulta)
- Data do pedido não pode ser no futuro
- Previsão de entrega não pode ser anterior à data do pedido
- Total do pedido deve ser > R$ 0,00
- Nr. Pedido Fornecedor não pode estar duplicado em importações anteriores (verificar import_logs)

**COMPORTAMENTO:** Pedidos com erro de negócio devem ser marcados como 'erro' no log sem bloquear o restante da importação (continuar para o próximo pedido).

#### Checklists

**Validações de Negócio**

- [ ] Validar filial: branchCode existe no cadastro de lojas
- [ ] Validar datas: data_pedido não no futuro, previsao_entrega >= data_pedido
- [ ] Validar valor: total > 0
- [ ] Verificar duplicidade: nr_pedido_fornecedor não importado anteriormente (import_logs)
- [ ] Configurar comportamento: pedido com erro de negócio → marcar erro e prosseguir
- [ ] Retornar mensagem de erro descritiva para cada tipo de falha de negócio
- [ ] Endpoint GET /api/v1/importar/verificar-duplicatas (pré-verificação antes de executar)


## Sprint 3 — Backend: Visão Geral (APIs de Dados)

### [FIN-001] API Financeiro — Contas a Pagar, Receber, Caixa e Saldo Banco

- **Lista:** Sprint 3 — Backend: Visão Geral (APIs de Dados)
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/BWcbof3k/63-fin-001-api-financeiro-contas-a-pagar-receber-caixa-e-saldo-banco)
- **Etiquetas:** label-crud
- **Última atividade:** 17 de jun. de 2026, 10:51

#### Descrição

Implementar os endpoints do módulo Financeiro que alimentam as 4 abas da tela financeiro.html.

**ABA 1 — Contas a Pagar:**
- Tabela: Duplicata, Cód. Forn., Fornecedor, Despesa, Emissão, Vencimento, Valor, Status
- Filtros: busca (duplicata/fornecedor), status (a_vencer/vencido/pago), ordenar
- Stats: Total em Aberto, Vence Hoje, Esta Semana, Este Mês

**ABA 2 — Contas a Receber:**
- Tabela: Empresa, Fatura, Parcela, Cód. Cliente, Cliente, Documento, Emissão, Vencimento, Valor
- Filtros: tipo (Cartão/Boleto/PIX/Crediário), status, ordenar
- Stats: Total em Aberto, Cartões, Boleto/PIX/Crediário

**ABA 3 — Lançamentos Caixa:**
- Tabela: Loja, Duplicata, Fornecedor, Despesa, Data, Valor Orig., Juros, Desc., Pago, CC, Usuário, Situação
- Filtros: busca, loja, despesa, ordenar

**ABA 4 — Saldo Banco:**
- Tabela: Empresa, CNPJ, Banco, Agência, Conta, Tipo, Saldo, % do Total
- Filtros: de/até (data)
- Stats: Saldo Total, Maior Saldo, Empresas

#### Checklists

**Contas a Pagar**

- [ ] Endpoint GET /api/v1/financeiro/contas-pagar (filtros: q, status, orderBy, page, limit)
- [ ] Endpoint GET /api/v1/financeiro/contas-pagar/summary (stats: total_aberto, vence_hoje, semana, mes)
- [ ] Calcular status dinâmico: a_vencer (vencimento > hoje), vencido (vencimento <= hoje e não pago), pago
- [ ] Obter dados via proxy Totvs ou tabela própria (definir estratégia de sincronização)

**Contas a Receber**

- [ ] Endpoint GET /api/v1/financeiro/contas-receber (filtros: tipo, status, orderBy, page, limit)
- [ ] Endpoint GET /api/v1/financeiro/contas-receber/summary (stats: total, cartao, outros)
- [ ] Mapear tipos: Cartão de Crédito, Cartão de Débito, Boleto, PIX, Crediário

**Lançamentos Caixa e Saldo**

- [ ] Endpoint GET /api/v1/financeiro/lancamentos-caixa (filtros: q, loja, despesa, orderBy)
- [ ] Endpoint GET /api/v1/financeiro/lancamentos-caixa/lojas (lista de lojas disponíveis para filtro)
- [ ] Endpoint GET /api/v1/financeiro/lancamentos-caixa/despesas (categorias de despesas)
- [ ] Endpoint GET /api/v1/financeiro/saldo-banco (filtros: de, ate)
- [ ] Endpoint GET /api/v1/financeiro/saldo-banco/summary (saldo total, maior saldo, qtd empresas)

### [FAT-001] API Faturamento — Notas Fiscais (Vendas, Transferências, Compras, Devoluções)

- **Lista:** Sprint 3 — Backend: Visão Geral (APIs de Dados)
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/hJJCJpuS/64-fat-001-api-faturamento-notas-fiscais-vendas-transfer%C3%AAncias-compras-devolu%C3%A7%C3%B5es)
- **Etiquetas:** label-crud
- **Última atividade:** 17 de jun. de 2026, 10:51

#### Descrição

Implementar os endpoints do módulo Faturamento que alimentam faturamento.html.

**DADOS DA TABELA:**
- Emp., NF, Série, Destinatário, Data Emissão, Data Saída, Situação, Frete, Transportadora, Valor, Tipo

**FILTROS:**
- Tipo: all / vendas / transf / compra / devolucao
- Período: de / até (datas)

**STATS (cards clicáveis):**
- Vendas: valor total + qtd de notas
- Transferências: valor total + qtd de notas
- Compras/Entradas: valor total + qtd de notas
- Devoluções: valor total + qtd de notas

#### Checklists

**Endpoints a Implementar**

- [ ] Endpoint GET /api/v1/faturamento (filtros: tipo, de, ate, page, limit)
- [ ] Endpoint GET /api/v1/faturamento/summary (stats por tipo: vendas, transf, compra, devolucao)
- [ ] Mapear tipos de nota: vendas (op=S), transf (op=T), compra/entrada (op=E), devolucao (op=D)
- [ ] Paginação server-side com page e limit
- [ ] Ordenação por data de emissão (desc por padrão)
- [ ] Índices: faturamento.tipo, faturamento.data_emissao

### [CPR-001] API Pedidos de Compra — Status, Fornecedores e Estatísticas

- **Lista:** Sprint 3 — Backend: Visão Geral (APIs de Dados)
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/LX4likkY/65-cpr-001-api-pedidos-de-compra-status-fornecedores-e-estat%C3%ADsticas)
- **Etiquetas:** label-crud
- **Última atividade:** 17 de jun. de 2026, 10:51

#### Descrição

Implementar os endpoints do módulo Pedidos de Compra que alimentam compras.html.

**DADOS DA TABELA:**
- Emp., Pedido, Cód. Forn., Fornecedor, Tipo, Status, Solicit., Atend., Pend., Inclusão, Prev. Entrega, Lim. Entrada, Atraso (dias)

**FILTROS:**
- Busca: pedido ou fornecedor
- Status: em_andamento / parcial / atendido / cancelado
- Tipo: Calçados / Acessórios

**STATS:**
- Total Solicitado (valor R$), Em Andamento (qtd), Atrasados (qtd), Fornecedores (qtd único)

**GRÁFICOS:**
- Qtd por Status (barras)
- Tipos de Produtos (barras)

#### Checklists

**Endpoints a Implementar**

- [ ] Endpoint GET /api/v1/compras (filtros: q, status, tipo, page, limit)
- [ ] Endpoint GET /api/v1/compras/summary (stats: total_valor, em_andamento, atrasados, fornecedores)
- [ ] Endpoint GET /api/v1/compras/por-status (para gráfico Qtd por Status)
- [ ] Endpoint GET /api/v1/compras/por-tipo (para gráfico Tipos de Produtos)
- [ ] Calcular campo atraso: dias entre Lim. Entrada e hoje (se não atendido e lim < hoje)
- [ ] Calcular campo pendente: solicitado - atendido

### [PRD-001] API Produtos — Cadastro, Estoque e Preços

- **Lista:** Sprint 3 — Backend: Visão Geral (APIs de Dados)
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/Q1GW6G8a/66-prd-001-api-produtos-cadastro-estoque-e-pre%C3%A7os)
- **Etiquetas:** label-crud
- **Última atividade:** 17 de jun. de 2026, 10:51

#### Descrição

Implementar os endpoints do módulo Produtos que alimentam produtos.html.

**DADOS DA TABELA:**
- Ref., Produto/Fornecedor, Categoria, Material, Cor, Custo, Full Price, Outlet, Digital (de), Digital (para), Estoque, Status

**FILTROS:**
- Busca: nome, referência ou fornecedor
- Categoria: Tênis / Sandálias / Botas / Chinelos / Sapatênis / Acessórios
- Material: dinâmico (carregar da base)
- Fornecedor: dinâmico (carregar da base)
- Status: ativo / inativo

**STATS:**
- Total de Produtos, Produtos Ativos, Total Estoque (soma), Produtos Inativos

#### Checklists

**Endpoints a Implementar**

- [ ] Endpoint GET /api/v1/produtos (filtros: q, categoria, material, fornecedor, status, page, limit)
- [ ] Endpoint GET /api/v1/produtos/summary (stats: total, ativos, total_estoque, inativos)
- [ ] Endpoint GET /api/v1/produtos/materiais (lista de materiais para filtro dinâmico)
- [ ] Endpoint GET /api/v1/produtos/fornecedores (lista de fornecedores para filtro dinâmico)
- [ ] Endpoint GET /api/v1/produtos/:id (detalhes de produto específico)
- [ ] Índices: produtos.categoria, produtos.material, produtos.fornecedor_id, produtos.status

### [PES-001] API Pessoa — Clientes, Fornecedores e Funcionários

- **Lista:** Sprint 3 — Backend: Visão Geral (APIs de Dados)
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/FC0whbix/67-pes-001-api-pessoa-clientes-fornecedores-e-funcion%C3%A1rios)
- **Etiquetas:** label-crud
- **Última atividade:** 17 de jun. de 2026, 10:51

#### Descrição

Implementar os endpoints do módulo Pessoa que alimentam pessoa.html.

**DADOS DA TABELA:**
- Cód, Nome, CPF, Tipo (cliente/fornecedor/funcionário), Status, Telefone, Cadastro

**MODAL DE DETALHES:**
- Ao clicar em uma pessoa abre modal (#pmodal-overlay) com dados completos
- Inclui: endereço, e-mail, histórico de compras (se cliente)

**FILTROS:**
- Busca: nome, CPF ou e-mail
- Tipo: cliente / fornecedor / funcionário
- Status: ativo / inativo

#### Checklists

**Endpoints a Implementar**

- [ ] Endpoint GET /api/v1/pessoa (filtros: q, tipo, status, page, limit)
- [ ] Endpoint GET /api/v1/pessoa/:id (dados completos para modal de detalhes)
- [ ] Validação: CPF com algoritmo de verificação
- [ ] Máscara de CPF: exibir formatado (XXX.XXX.XXX-XX)
- [ ] Índices: pessoa.tipo, pessoa.status, pessoa.cpf (único)
- [ ] Paginação server-side (a lista atual é client-side)

### [VND-001] API Venda — Empresas, Vendedores e Vendas (Digital + Física)

- **Lista:** Sprint 3 — Backend: Visão Geral (APIs de Dados)
- **Status:** aberto
- **Trello:** [abrir card](https://trello.com/c/tUF0MDhH/68-vnd-001-api-venda-empresas-vendedores-e-vendas-digital-f%C3%ADsica)
- **Etiquetas:** label-crud
- **Última atividade:** 17 de jun. de 2026, 10:51

#### Descrição

Implementar os endpoints do módulo Venda que alimentam as 3 abas de venda.html.

**ABA 1 — Empresa:**
- Tabela: Empresa, Cidade/UF, Meta, Realizado, Atingimento (%), Status
- Filtros: busca, status (ativo/inativo)

**ABA 2 — Vendedores:**
- Stats: Total Realizado, Qtd Vendedores, Ativos, Inativos
- Tabela: Vendedor, Loja, Meta, Realizado, Atingimento (%), Status
- Filtros: busca, loja, ordenar, status

**ABA 3 — Vendas:**
- Stats: Venda Digital, Venda Física, Total Comissão, Ticket Médio
- Vendas Digitais: Data, Canal (Shopify/Suri), Vendedor, Cliente, Produto, Total, Comissão, Status
- Vendas Físicas: Data, Loja, Vendedor, Cliente, Produto, Total, Comissão, Status
- Filtros: período (de/até), tipo (digital/física), status (confirmada/pendente/cancelada)

#### Checklists

**Empresas e Vendedores**

- [ ] Endpoint GET /api/v1/venda/empresas (filtros: q, status, page, limit)
- [ ] Endpoint GET /api/v1/venda/vendedores (filtros: q, loja, status, orderBy, page, limit)
- [ ] Endpoint GET /api/v1/venda/vendedores/summary (stats: total_realizado, count, ativos, inativos)
- [ ] Endpoint GET /api/v1/venda/lojas (lista de lojas para filtro de vendedores)

**Vendas**

- [ ] Endpoint GET /api/v1/venda/vendas (filtros: de, ate, tipo, status, page, limit)
- [ ] Endpoint GET /api/v1/venda/vendas/summary (stats: digital, fisica, comissao_total, ticket_medio)
- [ ] Separar vendas digitais (canal: Shopify, Suri) de físicas (lojas)
- [ ] Calcular comissão por venda (comissaoPct * total / 100)
- [ ] Calcular ticket médio: total_realizado / qtd_vendas
- [ ] Índices: vendas.tipo, vendas.data, vendas.status, vendas.vendedor_id
