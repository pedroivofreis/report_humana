# Check-in Lite → API Humana (FastAPI): o que já existe e o que o time precisa criar

Objetivo: **sair do mock** (`localStorage`, CPFs fixos, fila de sync simulada) e apontar o app para a API em `api-main`.  
Base de path padrão no código: **`API_STR=/api`** → rotas documentadas em **`/api/...`**.  
Documentação interativa: **`GET /docs`**, esquema: **`GET /api/openapi.json`**.

**Autenticação do app:** o login real é **`POST /api/auth/login`**, que devolve tokens; as rotas protegidas usam **`Authorization: Bearer <access_token>`** (ver `app/api/dependencies/authentication.py`). O README antigo cita `x-api-key` para “microserviço”; para o **app médico**, o fluxo esperado é **OAuth2 Bearer** após login.

---

## 1. O que o Check-in Lite faz hoje (mock) — inventário para integração

| Área no app | Comportamento mock | “Evento” na fila offline (`enqueueSyncAction`) |
|-------------|-------------------|-----------------------------------------------|
| Entrada | CPF sem senha; usuários seed | `login` |
| Lista Meus plantões (+ abas Próximos / Realizados) | `shifts[]` em `localStorage` | — |
| Agenda / calendário | Mesmo array de plantões | — |
| Banner “próximo plantão” | Calculado em memória | — |
| Anúncios + “Pegar plantão” | Lista seed + remove item | `take-announcement` |
| Check-in (foto, GPS, IP, hash imagem) | Grava em objeto do plantão | `start-shift` |
| Check-out | Completa plantão | `stop-shift` |
| “Mandar para revisão” | Texto livre ligado ao plantão | `submit-review` |
| Financeiro | Valores derivados por `shift.id` (mock) | — |
| Preferências de alertas | Flag em `localStorage` por médico | — |
| IP público | `fetch` api.ipify (externo) | — |

Nada disso chama o backend Humana hoje, exceto o IP externo.

---

## 2. O que **já existe** no FastAPI (pode usar para tirar parte do mock)

Para cada linha: **endpoint** + **alinhar com o lite**.

### 2.1 Autenticação e usuário

| Precisa no lite | Já existe | Notas |
|-----------------|-----------|-------|
| Login com CPF + senha | `POST /api/auth/login` | Body: `cpf`, `password`, `remember_me`. Trocar tela de só CPF. |
| Manter sessão | `POST /api/auth/refresh` | Refresh token |
| Usuário atual | `GET /api/auth/me` | Bearer |
| Esqueci senha | `POST /api/auth/forgot-password`, `POST /api/auth/reset-password` | Opcional para o lite |
| CPF já cadastrado? | `GET /api/users/is-registered/{cpf}` | Útil antes do cadastro/login |

### 2.2 Plantões do médico (núcleo do app)

| Precisa no lite | Já existe | Notas |
|-----------------|-----------|-------|
| Listar plantões por instituição + competência (mês) | `GET /api/user-shifts` | Query obrigatória: `institution_id`, `date` (YYYY-MM); opcional: `user_id`, `sector_id`. Resposta agrupada por setor. |
| Detalhe de um plantão do usuário | `GET /api/user-shifts/{shift_id}` | UUID |
| Atualizar plantão | `PUT /api/user-shifts/{shift_id}` | |
| Cancelar plantão | `POST /api/user-shifts/{shift_id}/cancel` | |
| Troca de plantão | `POST /api/user-shifts/{shift_id}/exchange` | Lite não tem tela |
| Check-in geolocalizado | `POST /api/user-shifts/checkin/{user_id}` | Query: `lat`, `long`. Ver **§3 gap importante**. |
| Check-out | `POST /api/user-shifts/checkout/{user_id}` | Ver **§3**. |

### 2.3 Cadastros auxiliares (hospital, endereço, setor)

| Precisa no lite | Já existe |
|-----------------|-----------|
| Instituições | `GET/POST/PUT/DELETE /api/institutions`, `GET /api/institutions/{id}` |
| Setores | `GET/POST/PUT/DELETE /api/sectors` |
| Endereços | `GET/POST/PUT/DELETE /api/addresses` (há dois routers em `/addresses` no `api_router`; validar duplicidade no `/docs`) |

### 2.4 Modelo de plantão (tipo de escala)

| Precisa no lite | Já existe |
|-----------------|-----------|
| CRUD “tipo” de plantão | `POST/GET/PUT /api/shifts`, `GET/DELETE /api/shifts/{shift_id}` |
| Tipos nomeados | `POST/GET/PUT/DELETE /api/shift-types` |

Listagem `GET /api/shifts` **exige** query `sector_id` **ou** `institution_id`.

### 2.5 Financeiro / folha (substituir KPIs mock)

| Precisa no lite | Já existe |
|-----------------|-----------|
| Resumo por competência / setor | `GET /api/user-timesheets/summary` | Query: `competence_date` (YYYY-MM), opcional `user_id`, `sector_ids` |
| Detalhe folha | `GET /api/user-timesheets/summary/{user_timesheet_id}`, etc. |

Os campos retornados são do **domínio folha de ponto**; podem não bater 1:1 com “Plantões / A receber / Recebido” do mock — ver **§4**.

### 2.6 Evidência em arquivo (foto)

| Precisa no lite | Já existe |
|-----------------|-----------|
| Upload arquivo | `POST /api/attachments` | Multipart (`AttachmentCreateRequestForm`) |
| Listar por entidade | `GET /api/attachments/{entity_type}/{entity_id}` |

Fluxo típico: **upload** → recebe `attachment_id` → associar ao **user_shift** (hoje o check-in HTTP não recebe foto; ver §3).

### 2.7 “Revisão” / observação sobre pessoa

| Precisa no lite | Já existe |
|-----------------|-----------|
| Criar texto | `POST /api/user-observations` | Body exige `target_user_id`, `owner_id`, `observation` |

No lite a revisão está ligada ao **plantão** e ao **próprio médico**. Na API, observação é sobre **usuário alvo**. Pode servir com `target_user_id` = médico e texto livre, ou pode ser necessário endpoint específico de **revisão de plantão** — ver **§4**.

---

## 3. Gap crítico: check-in / check-out **como o lite** vs **como a API** hoje

Implementação atual em `UserShiftService.perform_checkin`:

- Recebe só **`user_id`, `lat`, `long`**.
- Busca **automaticamente** “um plantão planejado na janela de tempo” para esse usuário e grava check-in nele.

O **lite** permite escolher **qual plantão** abrir no modal (por `shift.id`) e envia **foto**, **precisão GPS**, **IP**, **device**, **código hash da imagem**.

**Conclusão para o time de backend:**

| Situação | Ação recomendada |
|----------|------------------|
| Manter UX “escolho o plantão na lista” | **Nova rota ou extensão**, ex.: `POST /api/user-shifts/{user_shift_id}/check-in` com body `{ lat, long, accuracy_m?, attachment_id? }` (e opcional IP/device para auditoria). |
| Manter apenas “próximo plantão na janela” | Adaptar o **frontend** ao comportamento atual (sem escolher card específico) — pode não ser aceitável para PO. |
| Foto obrigatória no check-in | Estender contrato do check-in com **`attachment_id`** (após `POST /attachments`) ou multipart no mesmo endpoint. |

**Check-out:** hoje `POST /api/user-shifts/checkout/{user_id}` fecha o plantão **em progresso** do usuário. Se no futuro houver mais de um “em progresso” ou fechamento pelo **id do plantão**, avaliar **`POST .../checkout` por `user_shift_id`**.

---

## 4. O que provavelmente **ainda não existe** e o time deve **criar** (ou definir estratégia)

| Necessidade do lite | Estado na API | Sugestão de trabalho |
|---------------------|----------------|----------------------|
| **Anúncios** (“pegar plantão” de vaga aberta) | Não há recurso homônimo no Swagger | Novo módulo (ex.: `shift-opportunities`, `announcements`) **ou** lista filtrada de `user-shifts`/slots com estado “aberto para candidatura”. Definir regra de negócio com PO. |
| **Aceitar plantão** (equiv. `take-announcement`) | Não mapeado 1:1 | Endpoint que **atribui** usuário a um slot aberto ou **POST** em `user-shifts` com regra específica. |
| **Preferências de alertas** (push antes do plantão) | Não há rota dedicada no inventário atual | `user` settings, `complementary-data`, ou nova tabela **notification_preferences**. |
| **Financeiro idêntico ao mock** (3 KPIs por lista filtrada) | `user-timesheets/summary` existe mas é modelo de **folha** | Ou adaptar UI aos campos reais do summary, ou novo endpoint **`GET /api/me/finance-summary`** agregando user-shifts + pagamentos. |
| **Revisão atrelada ao plantão** | `user-observations` é observação entre usuários | Novo recurso **`shift_review`** ou estender observação com `user_shift_id`. |
| **Sincronização offline confiável** | Apenas POSTs individuais | Opcional: **`POST /api/sync/batch`** com idempotência (`client_id`) ou repetir chamadas atuaises com retry. |

---

## 5. Matriz rápida: mock do lite → API

| Feature lite | Usar endpoint existente? | Criar/alterar API? |
|--------------|--------------------------|---------------------|
| Login CPF | Sim: `POST /auth/login` (+ senha) | — |
| Lista plantões | Sim: `GET /user-shifts` | Talvez paginação/filtro “realizados” se não vier no payload |
| Próximos vs realizados | Depende dos **status** no modelo (`ShiftStatus`) | Se front precisar só “COMPLETED”, filtrar no client ou query nova |
| Check-in com card escolhido | Parcial | **Sim** — check-in por `user_shift_id` + metadados |
| Check-out com card escolhido | Parcial | **Sim** — checkout por `user_shift_id` se regra mudar |
| Foto check-in | `POST /attachments` + vínculo | **Sim** — vínculo no check-in ou campo no modelo |
| Mapa / Google Maps | Externo | — |
| IP (ipify) | Externo | Opcional gravar no backend |
| Anúncios | Não | **Sim** — novo fluxo |
| Financeiro (UI atual) | Parcial (`user-timesheets/summary`) | Talvez **Sim** — agregação alinhada ao produto |
| Alertas | Não | **Sim** |
| Revisão texto | Parcial (`user-observations`) | Talvez **Sim** — semântica plantão vs usuário |

---

## 6. Ordem sugerida de integração (para o time)

1. **Auth**: login, refresh, me; persistir tokens no front (seguro).
2. **Institution + user-shifts**: listar plantões do médico por `institution_id` + competência (substituir lista mock).
3. **Check-in/out**: alinhar UX com backend (§3); depois attachments.
4. **Financeiro**: consumir `user-timesheets/summary` ou fechar contrato novo com PO.
5. **Anúncios / pegar plantão**: após definir RFC.
6. **Alertas** e **offline** como camada final.

---

## 7. Referência de arquivos no monorepo

| Onde | O quê |
|------|--------|
| `api-main/api-main/app/api/main.py` | Montagem de todos os routers sob `/api` |
| `api-main/api-main/app/api/routers/user_shifts.py` | Check-in/out, lista, cancel, exchange |
| `api-main/api-main/app/api/services/user_shift_service.py` | Regra de negócio do check-in na janela |
| `humana-checkin-lite/src/App.vue` | Toda a lógica mock e fila `syncQueue` |

---

*Documento gerado para planejamento de integração; ajustar paths se `API_STR` ou prefixos forem diferentes no ambiente (staging/produção).*
