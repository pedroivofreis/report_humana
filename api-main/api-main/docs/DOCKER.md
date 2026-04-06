# Guia Docker - Institution Service API

Este documento fornece instruções para executar a aplicação usando Docker e Docker Compose.

## Pré-requisitos

- Docker instalado (versão 20.10+)
- Docker Compose instalado (versão 2.0+)

## Estrutura de Arquivos Docker

- `Dockerfile`: Define a imagem da aplicação FastAPI
- `docker-compose.yml`: Orquestra a aplicação e o banco de dados PostgreSQL
- `.dockerignore`: Otimiza o build excluindo arquivos desnecessários

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=places_db

# Application Configuration
PROJECT_NAME=Humana API
API_STR=/api
API_PORT=8000

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here-change-in-production
API_KEY=your-api-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# Logging Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
SQLALCHEMY_ECHO=false
```

**⚠️ IMPORTANTE:** Altere as chaves `SECRET_KEY` e `API_KEY` em produção!

## Como Usar

### 1. Iniciar os Serviços

```bash
# Construir e iniciar todos os serviços
docker-compose up --build

# Ou em modo detached (background)
docker-compose up -d --build
```

### 2. Verificar Status dos Serviços

```bash
# Ver status dos containers
docker-compose ps

# Ver logs da aplicação
docker-compose logs -f api

# Ver logs do banco de dados
docker-compose logs -f postgres
```

### 3. Acessar a Aplicação

- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 4. Executar Migrações Manualmente

```bash
# Acessar o container da aplicação
docker-compose exec api bash

# Executar migrações
alembic upgrade head

# Criar nova migração
alembic revision --autogenerate -m "descrição da migração"
```

### 5. Parar os Serviços

```bash
# Parar os serviços
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar, remover containers e volumes (CUIDADO: apaga o banco de dados!)
docker-compose down -v
```

## Comandos Úteis

### Reconstruir a Aplicação

```bash
# Reconstruir apenas a aplicação (sem cache)
docker-compose build --no-cache api

# Reconstruir e reiniciar
docker-compose up -d --build api
```

### Acessar o Banco de Dados

```bash
# Via docker-compose
docker-compose exec postgres psql -U postgres -d places_db

# Via host (se a porta estiver exposta)
psql -h localhost -U postgres -d places_db
```

### Ver Logs em Tempo Real

```bash
# Logs de todos os serviços
docker-compose logs -f

# Logs apenas da API
docker-compose logs -f api

# Últimas 100 linhas
docker-compose logs --tail=100 api
```

### Executar Comandos na Aplicação

```bash
# Acessar shell do container
docker-compose exec api bash

# Executar comando Python
docker-compose exec api python -c "print('Hello from container!')"

# Executar testes (se configurado)
docker-compose exec api pytest
```

## Troubleshooting

### Problema: Container não inicia

```bash
# Ver logs detalhados
docker-compose logs api

# Verificar se a porta está em uso
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### Problema: Erro de conexão com banco de dados

1. Verifique se o container do PostgreSQL está rodando:
```bash
docker-compose ps postgres
```

2. Verifique os logs do PostgreSQL:
```bash
docker-compose logs postgres
```

3. Certifique-se de que as variáveis de ambiente estão corretas

### Problema: Migrações não são executadas

```bash
# Executar manualmente
docker-compose exec api alembic upgrade head

# Verificar status das migrações
docker-compose exec api alembic current
```

### Limpar Tudo e Começar de Novo

```bash
# Parar e remover tudo
docker-compose down -v

# Remover imagens
docker-compose down --rmi all

# Reconstruir do zero
docker-compose up --build
```

## Desenvolvimento Local

Para desenvolvimento com hot-reload, o `docker-compose.yml` já está configurado com volumes que montam:
- `./app` → `/app/app`
- `./main.py` → `/app/main.py`
- `./alembic` → `/app/alembic`

Isso significa que mudanças no código serão refletidas automaticamente sem precisar reconstruir a imagem.

## Produção

Para produção, considere:

1. **Usar variáveis de ambiente seguras**
   - Gerar SECRET_KEY e API_KEY fortes
   - Usar secrets management (Docker Secrets, Kubernetes Secrets, etc.)

2. **Remover hot-reload**
   - Alterar o comando para: `uvicorn main:app --host 0.0.0.0 --port 8000` (sem `--reload`)

3. **Usar proxy reverso**
   - Adicionar Nginx ou Traefik na frente da aplicação

4. **Backup do banco de dados**
   - Configurar backups regulares do volume PostgreSQL

5. **Monitoramento**
   - Adicionar Prometheus, Grafana, ou serviços de APM

6. **Configurar HTTPS**
   - Usar Let's Encrypt ou certificados da organização

## Estrutura de Rede

Os serviços usam uma rede bridge customizada chamada `institution-network`, que permite:
- Comunicação entre containers por nome (ex: `postgres`)
- Isolamento de outros containers
- DNS interno automático

## Volumes Persistentes

- `postgres_data`: Armazena dados do PostgreSQL de forma persistente

Para fazer backup do volume:
```bash
docker run --rm -v institution-service-api_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

Para restaurar:
```bash
docker run --rm -v institution-service-api_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

