# AGENTS - Humana

Este arquivo orienta agentes a entender e agir neste repositorio rapidamente.

## TL;DR

- Este repo tem 3 apps:
  - `./` (raiz): Next.js que serve/protege relatorio estatico.
  - `web-app-main/web-app-main`: frontend principal (Vue 3 + Vite + Vuetify).
  - `api-main/api-main`: backend principal (FastAPI + SQLAlchemy + PostgreSQL).
- Leia primeiro: `MAPA_PROJETO_HUMANA.md`.
- Nao altere codigo de apps fora do escopo pedido.

## Estrutura e responsabilidade

### 1) Raiz (Next.js)

- Entrada: `app/page.tsx`
- Protecao: `middleware.ts`
- Conteudo principal: `public/relatorio-funcionalidades.html`
- Uso: apenas relatorio e auth basica em producao.

### 2) Frontend (Vue)

- Caminho: `web-app-main/web-app-main`
- Entrada: `src/main.ts`
- Core: `src/@core`
- UI/paginas: `src/pages`, `src/views`, `src/components`

### 3) Backend (FastAPI)

- Caminho: `api-main/api-main`
- Entrada: `main.py`
- Endpoints: `app/api/routers`
- Negocio: `app/api/services`
- Dados: `app/api/repositories`, `app/api/models`, `app/db`

## Comandos padrao

### Raiz (Next.js)

```bash
npm install
npm run dev
npm run build
npm run start
```

### Frontend (Vue)

```bash
cd web-app-main/web-app-main
npm install
npm run dev
npm run build
npm run lint
npm run test
```

### Backend (FastAPI)

```bash
cd api-main/api-main
make install-dev
make run
make lint
make test
make migrate
make docker-dev
```

## Regras operacionais para agentes

1. Identifique primeiro qual app esta no escopo.
2. Edite o minimo necessario e mantenha estilo local.
3. Evite tocar em arquivos fora do modulo solicitado.
4. Rode validacao do modulo alterado (lint/test/build quando aplicavel).
5. Em mudancas grandes, atualize tambem `MAPA_PROJETO_HUMANA.md`.

## Ambiguidades conhecidas

- Pode haver duvida entre "frontend da raiz" (Next relatorio) e "frontend principal" (Vue).
- O frontend principal fica em pasta dupla: `web-app-main/web-app-main`.
- Ha arquivos `.zip` na raiz que nao fazem parte do fluxo comum de desenvolvimento.

## Checklist rapido antes de implementar

- Qual app foi pedido?
- Qual arquivo de entrada dessa app?
- Quais comandos de validacao devo rodar?
- Precisa atualizar documentacao (`MAPA_PROJETO_HUMANA.md`)?
