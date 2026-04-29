# Mapa do Projeto Humana

Este arquivo resume o projeto para leitura rapida sempre que voce (ou um agente) precisar retomar o contexto.

## Visao Geral

Este repositorio concentra 3 partes:

1. `./` (raiz): app Next.js simples para servir e proteger o relatorio de funcionalidades.
2. `web-app-main/web-app-main`: frontend principal em Vue 3 + Vite + Vuetify.
3. `api-main/api-main`: backend principal em FastAPI + SQLAlchemy + PostgreSQL.

---

## 1) Aplicacao da Raiz (Next.js)

### Objetivo

- Servir o relatorio em HTML estatico.
- Aplicar autenticacao basica (senha) em producao.

### Arquivos-chave

- `app/page.tsx`: redireciona para `/relatorio-funcionalidades.html`.
- `public/relatorio-funcionalidades.html`: relatorio publicado.
- `middleware.ts`: protege rotas com Basic Auth em producao.
- `package.json`: scripts `dev`, `build`, `start`.

### Como rodar

```bash
npm install
npm run dev
```

---

## 2) Frontend Principal (Vue)

### Caminho

- `web-app-main/web-app-main`

### Stack

- Vue 3, Vite 6, TypeScript, Vuetify 3
- Pinia (estado), Vue Router, Axios/ofetch
- ESLint, Stylelint, Vitest, Husky

### Estrutura essencial (`src/`)

- `src/@core`: base tecnica (stores, servicos de API, utilitarios, constantes, interfaces).
- `src/pages`: paginas/rotas principais.
- `src/views`: componentes por feature e composicao de telas.
- `src/components`: componentes reutilizaveis.
- `src/plugins`: plugins (router, iconify etc).
- `src/main.ts`: bootstrap da aplicacao Vue.

### Scripts uteis

```bash
cd web-app-main/web-app-main
npm install
npm run dev
npm run build
npm run lint
npm run test
```

---

## 3) Backend Principal (FastAPI)

### Caminho

- `api-main/api-main`

### Stack

- FastAPI, Uvicorn
- SQLAlchemy 2 (async), Alembic
- PostgreSQL (psycopg2/asyncpg)
- Pydantic Settings, JWT, SlowAPI (rate limit)
- Docker e Docker Compose

### Estrutura essencial

- `app/api/routers`: endpoints por dominio.
- `app/api/services`: regras de negocio.
- `app/api/repositories`: acesso a dados.
- `app/api/models`: modelos ORM.
- `app/api/schemas`: validacao e contratos.
- `app/core`: configuracoes, seguranca, logging, excecoes.
- `app/db`: engine, sessao e base SQLAlchemy.
- `main.py`: inicializacao da API, middlewares e roteadores.

### Comandos uteis (Makefile)

```bash
cd api-main/api-main
make install-dev
make run
make lint
make test
make migrate
make docker-dev
```

---

## Fluxo Recomendado de Leitura (5 minutos)

1. Ler este arquivo (`MAPA_PROJETO_HUMANA.md`).
2. Confirmar qual aplicacao voce quer mexer:
   - Relatorio/protecao: raiz Next.js.
   - Produto web: frontend Vue.
   - API/dados: backend FastAPI.
3. Abrir o arquivo de entrada da aplicacao alvo:
   - Raiz: `app/page.tsx` e `middleware.ts`.
   - Frontend: `web-app-main/web-app-main/src/main.ts`.
   - Backend: `api-main/api-main/main.py`.
4. Executar o comando de desenvolvimento da aplicacao alvo.

---

## Observacoes Importantes

- Existem arquivos `.zip` na raiz com snapshots (`api-main.zip`, `web-app-main.zip`); normalmente nao sao usados no fluxo diario.
- O frontend de produto esta dentro de `web-app-main/web-app-main` (pasta dupla).
- O backend possui Docker, mas tambem pode rodar local com Python + PostgreSQL.

---

## Quando atualizar este mapa

Atualize este arquivo quando ocorrer:

- mudanca de stack,
- mudanca de estrutura de pastas,
- entrada/saida de servicos,
- mudanca de comandos principais de execucao/teste/build.

Assim ele continua sendo o ponto unico de leitura rapida do projeto.
