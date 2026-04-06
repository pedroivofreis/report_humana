# Humana API

API RESTful desenvolvida com FastAPI e PostgreSQL.

## Requisitos

### Para executar com Docker (Recomendado)
- Docker 20.10+
- Docker Compose 2.0+

### Para executar localmente
- Python 3.12.7
- PostgreSQL
- pip (gerenciador de pacotes Python)

## 🚀 Início Rápido com Docker (Recomendado)

A forma mais rápida de executar a aplicação é usando Docker:

### 1. Configurar Variáveis de Ambiente

```bash
# Copie o template de variáveis de ambiente
cp env.template .env

# Edite o arquivo .env com suas configurações
# IMPORTANTE: Altere SECRET_KEY e API_KEY em produção!
```

### 2. Iniciar a Aplicação

```bash
# Construir e iniciar todos os serviços (API + PostgreSQL)
make docker-dev

# Ou usando docker-compose diretamente
docker-compose up -d --build
```

### 3. Acessar a Aplicação

- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 4. Ver Logs

```bash
# Ver logs de todos os serviços
make docker-logs

# Ver logs apenas da API
make docker-logs-api
```

### 5. Parar a Aplicação

```bash
# Parar os containers
make docker-down

# Parar e remover volumes (apaga dados do banco)
make docker-down-volumes
```

### Comandos Docker Úteis

```bash
# Ver todos os comandos Docker disponíveis
make help

# Acessar shell do container da API
make docker-exec-api

# Acessar PostgreSQL
make docker-exec-db

# Executar migrações
make docker-migrate

# Criar nova migração
make docker-migrate-create NAME="nome_da_migracao"

# Reiniciar API
make docker-restart-api

# Ver status dos containers
make docker-ps
```

Para mais detalhes sobre Docker, consulte [DOCKER.md](DOCKER.md).

---

## Configuração Local (Sem Docker)

1. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Linux/macOS
# ou
.\venv\Scripts\activate  # No Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=humana_db
SECRET_KEY=sua_chave_secreta
```

4. Configure o banco de dados:
```bash
# Crie o banco de dados
createdb humana_db

# Cria uma nova migração
alembic revision --autogenerate -m "Migration description"

# Execute as migrações
alembic upgrade head
```

## Executando a API Localmente

Para iniciar o servidor de desenvolvimento:
```bash
# Usando uvicorn diretamente
uvicorn main:app --reload

# Ou usando o Makefile
make run
```

A API estará disponível em `http://localhost:8000`

A documentação da API (Swagger) estará disponível em `http://localhost:8000/docs`

## Estrutura do Projeto

```
api/
├── alembic/              # Migrações do banco de dados
├── app/
│   ├── api/             # Endpoints da API
│   ├── core/           # Configurações e funcionalidades principais
│   └── db/             # Configurações do banco de dados
├── tests/              # Testes
├── .editorconfig       # Configuração de indentação
├── .flake8            # Configuração do Flake8
├── .gitignore         # Arquivos ignorados pelo Git
├── alembic.ini        # Configuração do Alembic
├── main.py            # Ponto de entrada da aplicação
├── Makefile           # Comandos úteis para desenvolvimento
├── pyproject.toml     # Configurações de ferramentas Python
├── requirements.txt   # Dependências de produção
└── requirements-dev.txt # Dependências de desenvolvimento
```

## Padrões de Código

O projeto utiliza as seguintes ferramentas para manter a qualidade do código:

### Formatação
- **Black**: Formatador de código automático
- **isort**: Organização de imports
- Linha máxima: 100 caracteres
- Indentação: 4 espaços

### Linting
- **Ruff**: Linter moderno e rápido
- **Flake8**: Verificação de estilo de código

### Type Checking
- **MyPy**: Verificação de tipos estáticos

### Instalação das Ferramentas de Desenvolvimento

```bash
pip install -r requirements-dev.txt
```

### Comandos Úteis (via Makefile)

```bash
# Ver todos os comandos disponíveis
make help

# Formatar código automaticamente
make format

# Executar linters
make lint

# Verificar tipos
make type-check

# Executar testes
make test

# Executar testes com cobertura
make test-cov

# Executar formatação, linting e verificação de tipos
make check

# Iniciar servidor de desenvolvimento
make run

# Criar nova migração
make migrate-create NAME="nome_da_migracao"

# Aplicar migrações
make migrate
```

### Antes de Commitar

Execute para garantir que o código está nos padrões:

```bash
make check
```


------------------------------- USER

# User Service API - Humana Project

> 🏥 Microserviço de gerenciamento de usuários para o projeto Humana

API RESTful robusta desenvolvida com FastAPI, PostgreSQL e arquitetura em camadas, oferecendo gerenciamento completo de usuários, roles e dados complementares.

[![Python](https://img.shields.io/badge/Python-3.12.7-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.120.2-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg)](https://www.postgresql.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Recursos](#-recursos)
- [Arquitetura](#-arquitetura)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Executando](#-executando)
- [Migrações de Banco de Dados](#-migrações-de-banco-de-dados)
- [Desenvolvimento](#-desenvolvimento)
- [Endpoints da API](#-endpoints-da-api)
- [Segurança](#-segurança)
- [Logging](#-logging)
- [Testes](#-testes)
- [Deploy](#-deploy)
- [Documentação Adicional](#-documentação-adicional)

## 🎯 Visão Geral

Este microserviço é responsável por gerenciar todos os aspectos relacionados a usuários no ecossistema Humana, incluindo:

- Gerenciamento de usuários (CRUD completo)
- Sistema de roles e permissões
- Dados complementares de usuários
- Autenticação via API Key
- Logging estruturado com rastreamento de requisições
- Validações robustas

## ✨ Recursos

- 🚀 **FastAPI**: Framework moderno e de alta performance
- 🗄️ **PostgreSQL**: Banco de dados relacional robusto
- 🔐 **Autenticação API Key**: Segurança via x-api-key header
- 📊 **Logging Estruturado**: Utilizando structlog para rastreabilidade completa
- 🔄 **Migrações Automáticas**: Alembic para versionamento de schema
- 🎨 **Code Quality**: Black, Ruff, Flake8, isort e MyPy
- 📝 **Documentação Interativa**: Swagger UI e ReDoc
- 🏗️ **Arquitetura em Camadas**: Separação clara de responsabilidades
- ⚡ **Async/Await**: Operações assíncronas para melhor performance
- 🧪 **Testável**: Estrutura preparada para testes unitários e de integração

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas bem definida:

```
┌─────────────────────────────────────────┐
│         Routers (API Endpoints)         │
├─────────────────────────────────────────┤
│      Services (Regras de Negócio)       │
├─────────────────────────────────────────┤
│   Repositories (Acesso ao Banco de Dados) │
├─────────────────────────────────────────┤
│       Models (Entidades SQLAlchemy)      │
└─────────────────────────────────────────┘
```

### Estrutura de Diretórios

```
user-service-api/
├── alembic/                      # Migrações do banco de dados
│   ├── versions/                 # Arquivos de migração versionados
│   └── env.py                    # Configuração do Alembic
├── app/
│   ├── api/                      # Camada de API
│   │   ├── middlewares/          # Middlewares customizados
│   │   ├── models/               # Modelos SQLAlchemy (ORM)
│   │   ├── repositories/         # Camada de acesso a dados
│   │   ├── routers/              # Definição de rotas/endpoints
│   │   │   ├── user.py           # Endpoints de usuários
│   │   │   ├── role.py           # Endpoints de roles
│   │   │   ├── complementary_data.py  # Dados complementares
│   │   │   └── health_check.py   # Health check endpoint
│   │   ├── schemas/              # Pydantic schemas (validação)
│   │   ├── services/             # Lógica de negócio
│   │   ├── utils/                # Utilitários
│   │   └── validators/           # Validadores customizados
│   ├── core/                     # Configurações centrais
│   │   ├── config.py             # Configurações da aplicação
│   │   ├── exceptions.py         # Exceções customizadas
│   │   ├── logging_config.py     # Configuração de logging
│   │   └── middleware/           # Middlewares globais
│   └── db/                       # Configuração de banco de dados
│       ├── base.py               # Base declarativa SQLAlchemy
│       └── session.py            # Sessão e engine do banco
├── docs/                         # Documentação adicional
│   ├── CONTRIBUTING.md           # Guia de contribuição
│   ├── DEVELOPMENT_GUIDELINES.md # Diretrizes de desenvolvimento
│   └── SETUP_EDITOR.md           # Configuração de editores
├── scripts/                      # Scripts utilitários
│   └── reset_database.py         # Script para resetar o banco
├── main.py                       # Ponto de entrada da aplicação
├── Makefile                      # Comandos úteis de desenvolvimento
├── pyproject.toml                # Configuração de ferramentas Python
├── requirements.txt              # Dependências de produção
├── requirements-dev.txt          # Dependências de desenvolvimento
├── .env.example                  # Exemplo de variáveis de ambiente
├── .editorconfig                 # Configuração de editores
├── .flake8                       # Configuração do Flake8
├── .gitignore                    # Arquivos ignorados pelo Git
└── .pre-commit-config.yaml       # Hooks de pre-commit
```

## 📦 Requisitos

- **Python**: 3.12.7+
- **PostgreSQL**: 14.0+
- **pip**: Gerenciador de pacotes Python
- **Make**: Para facilitar comandos de desenvolvimento (opcional)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <repository-url>
cd user-service-api
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

### 3. Instale as dependências

```bash
# Dependências de produção
pip install -r requirements.txt

# Dependências de desenvolvimento (recomendado)
pip install -r requirements-dev.txt
```

Ou use o Makefile:

```bash
make install        # Produção
make install-dev    # Desenvolvimento
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```bash
cp .env.example .env
```

Configure as seguintes variáveis:

```env
# Segurança
SECRET_KEY=your-super-secret-key-here-change-in-production
API_KEY=your-api-key-for-service-authentication

# PostgreSQL
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=humana_db

# Configurações de Token
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 dias
```

### Configuração do Banco de Dados

1. **Crie o banco de dados PostgreSQL:**

```bash
# Usando createdb
createdb humana_db

# Ou via psql
psql -U postgres -c "CREATE DATABASE humana_db;"
```

2. **Execute as migrações:**

```bash
alembic upgrade head

# Ou usando Makefile
make migrate
```

## 🏃 Executando

### Servidor de Desenvolvimento

```bash
# Usando uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ou usando Makefile
make run
```

A API estará disponível em:

- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Servidor de Produção

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔄 Migrações de Banco de Dados

O projeto usa Alembic para gerenciamento de migrações. Comandos disponíveis:

```bash
# Criar nova migração
make migrate-create NAME="adicionar_campo_usuario"
# Ou: alembic revision --autogenerate -m "adicionar_campo_usuario"

# Aplicar migrações
make migrate
# Ou: alembic upgrade head

# Reverter última migração
make migrate-rollback
# Ou: alembic downgrade -1

# Ver status das migrações
make migrate-status
# Ou: alembic current

# Ver histórico completo
alembic history

# Resetar todas as migrações (CUIDADO!)
make migrate-reset

# Resetar banco de dados completamente (DANGER!)
make db-reset
```

## 👨‍💻 Desenvolvimento

### Padrões de Código

O projeto utiliza várias ferramentas para garantir qualidade:

- **Black**: Formatação automática de código (linha max: 100)
- **isort**: Organização de imports
- **Ruff**: Linter moderno e rápido
- **Flake8**: Verificação de estilo
- **MyPy**: Type checking estático

### Comandos Úteis

```bash
# Ver todos os comandos disponíveis
make help

# Formatar código automaticamente
make format

# Executar linters
make lint

# Verificar tipos
make type-check

# Executar todas as verificações (format + lint + type-check)
make check

# Limpar arquivos temporários e cache
make clean

# Executar tudo (clean + install + check + test)
make all
```

### Workflow de Desenvolvimento

1. **Antes de começar a codar:**

   ```bash
   git checkout -b feature/minha-feature
   ```

2. **Durante o desenvolvimento:**

   ```bash
   # Execute formatação e verificações periodicamente
   make format
   make check
   ```

3. **Antes de commitar:**

   ```bash
   # Garanta que tudo está OK
   make check

   # Se houver testes
   make test
   ```

4. **Commit e push:**
   ```bash
   git add .
   git commit -m "feat: descrição da feature"
   git push origin feature/minha-feature
   ```

## 📡 Exemplos de endpoints da API

### Health Check

| Método | Endpoint         | Descrição               |
| ------ | ---------------- | ----------------------- |
| GET    | `/`              | Mensagem de boas-vindas |
| GET    | `/api/health`    | Health check do serviço |

### Usuários

| Método | Endpoint                  | Descrição                |
| ------ | ------------------------- | ------------------------ |
| POST   | `/api/users`              | Criar novo usuário       |
| GET    | `/api/users`              | Listar todos os usuários |
| GET    | `/api/users/{user_id}`    | Buscar usuário por ID    |
| PUT    | `/api/users/{user_id}`    | Atualizar usuário        |
| DELETE | `/api/users/{user_id}`    | Deletar usuário          |

### Roles

| Método | Endpoint                  | Descrição             |
| ------ | ------------------------- | --------------------- |
| POST   | `/api/roles`              | Criar nova role       |
| GET    | `/api/roles`              | Listar todas as roles |
| GET    | `/api/roles/{role_id}`    | Buscar role por ID    |
| PUT    | `/api/roles/{role_id}`    | Atualizar role        |
| DELETE | `/api/roles/{role_id}`    | Deletar role          |

### Dados Complementares

| Método | Endpoint                               | Descrição                  |
| ------ | -------------------------------------- | -------------------------- |
| POST   | `/api/complementary-data`              | Criar dados complementares |
| GET    | `/api/complementary-data/{user_id}`    | Buscar dados por usuário   |
| PUT    | `/api/complementary-data/{data_id}`    | Atualizar dados            |
| DELETE | `/api/complementary-data/{data_id}`    | Deletar dados              |

> 📝 Para documentação detalhada dos schemas e exemplos de request/response, acesse `/docs` após iniciar o servidor.

## 🔐 Segurança

### Autenticação via API Key

Todos os endpoints (exceto `/` e `/health`) requerem autenticação via API Key:

```bash
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "x-api-key: your-api-key"
```

Configure a chave no arquivo `.env`:

```env
API_KEY=your-secure-api-key-here
```

### Swagger UI com API Key

A documentação Swagger está configurada para aceitar a API Key:

1. Acesse http://localhost:8000/docs
2. Clique no botão **"Authorize"** 🔒
3. Insira sua API Key
4. Todos os requests subsequentes incluirão o header automaticamente

### CORS

O CORS está configurado para aceitar todas as origens em desenvolvimento. **Em produção, configure adequadamente!**

```python
# main.py - Atualize para produção
allow_origins=["https://seu-dominio.com"]
```

## 📊 Logging

O projeto utiliza **structlog** para logging estruturado com rastreamento de requisições.

### Recursos de Logging

- **Logs Estruturados**: JSON em produção, colorido em desenvolvimento
- **Correlation ID**: Rastreamento de requisições via `X-Request-ID`
- **Performance Tracking**: Tempo de processamento de cada request
- **Context Binding**: Contexto automaticamente adicionado aos logs

### Exemplo de Log

```json
{
  "event": "Request completed",
  "timestamp": "2024-12-30T19:35:42Z",
  "level": "info",
  "request_id": "abc123",
  "method": "GET",
  "path": "/api/v1/users/123",
  "status_code": 200,
  "duration_ms": 45.2
}
```

### Níveis de Log

Configure o nível de log via variável de ambiente:

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🧪 Testes

### Executar Testes

```bash
# Executar todos os testes
make test
# Ou: pytest tests/ -v

# Com cobertura de código
make test-cov
# Ou: pytest tests/ -v --cov=app --cov-report=html

# Executar teste específico
pytest tests/test_users.py -v

# Com output detalhado
pytest tests/ -vv -s
```

### Estrutura de Testes

```
tests/
├── conftest.py           # Fixtures compartilhadas
├── test_users.py         # Testes de usuários
├── test_roles.py         # Testes de roles
└── test_integration.py   # Testes de integração
```

## 🚀 Deploy

### Deploy no Railway

O projeto está configurado para deploy automático no Railway com suporte a migrations automáticas.

**Arquivos de Deploy:**
- `start.sh`: Script que executa migrations e inicia o servidor
- `Procfile`: Configuração de inicialização para Railway

**Guia Completo:** Consulte [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md) para instruções detalhadas sobre:
- Como configurar o projeto no Railway
- Variáveis de ambiente necessárias
- Configuração do PostgreSQL
- Troubleshooting e verificação

### Deploy em Outros Ambientes

Para outros ambientes (AWS, Google Cloud, Azure, etc.), certifique-se de:

1. Executar as migrations antes de iniciar a aplicação:
   ```bash
   alembic upgrade head
   ```

2. Configurar todas as variáveis de ambiente necessárias (veja `env.example`)

3. Iniciar o servidor com Uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

## 📚 Documentação Adicional

O projeto inclui documentação detalhada na pasta `docs/` e na raiz:

- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)**: Como contribuir para o projeto
- **[DEVELOPMENT_GUIDELINES.md](docs/DEVELOPMENT_GUIDELINES.md)**: Diretrizes detalhadas de desenvolvimento
- **[SETUP_EDITOR.md](docs/SETUP_EDITOR.md)**: Como configurar seu editor (VS Code, PyCharm, etc.)
- **[DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)**: Guia completo de deploy no Railway

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão  | Descrição                    |
| ---------- | ------- | ---------------------------- |
| Python     | 3.12.7  | Linguagem de programação     |
| FastAPI    | 0.120.2 | Framework web assíncrono     |
| PostgreSQL | 16+     | Banco de dados relacional    |
| SQLAlchemy | 2.0.44  | ORM Python                   |
| Alembic    | 1.17.1  | Ferramenta de migrações      |
| Pydantic   | 2.12.3  | Validação de dados           |
| structlog  | 24.4.0  | Logging estruturado          |
| uvicorn    | 0.38.0  | Servidor ASGI                |
| asyncpg    | 0.30.0  | Driver PostgreSQL assíncrono |

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

Consulte [CONTRIBUTING.md](docs/CONTRIBUTING.md) para mais detalhes.

## 📄 Licença

Este projeto é parte do ecossistema Humana e é propriedade da organização.

## 📞 Suporte

Para questões e suporte:

- Abra uma issue no repositório
- Entre em contato com a equipe de desenvolvimento

---

**Desenvolvido com ❤️ pela equipe Humana**
