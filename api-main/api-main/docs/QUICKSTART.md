# 🚀 Guia de Início Rápido

Este guia ajudará você a colocar a aplicação no ar em menos de 5 minutos.

## Pré-requisitos

- ✅ Docker instalado
- ✅ Docker Compose instalado

## Opção 1: Script Automático (Mais Fácil)

```bash
# Execute o script de inicialização
cd scripts
./start.sh
```

O script irá:
1. Verificar se Docker está instalado
2. Criar arquivo `.env` se não existir
3. Construir as imagens Docker
4. Iniciar todos os serviços
5. Mostrar URLs e comandos úteis

## Opção 2: Comandos Manuais

### Passo 1: Configurar Variáveis de Ambiente

```bash
cp env.template .env
```

Edite o arquivo `.env` e ajuste as configurações (especialmente SECRET_KEY e API_KEY para produção).

### Passo 2: Iniciar a Aplicação

```bash
# Usando Make (recomendado)
make docker-dev

# Ou usando docker-compose diretamente
docker-compose up -d --build
```

### Passo 3: Verificar Status

```bash
# Ver status dos containers
make docker-ps

# Ver logs
make docker-logs
```

## 🌐 Acessar a Aplicação

Após iniciar, acesse:

- **API**: http://localhost:8000
- **Documentação Interativa (Swagger)**: http://localhost:8000/docs
- **Documentação Alternativa (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📋 Comandos Mais Usados

```bash
# Ver todos os comandos disponíveis
make help

# Ver logs em tempo real
make docker-logs

# Ver logs apenas da API
make docker-logs-api

# Parar os containers
make docker-down

# Reiniciar apenas a API
make docker-restart-api

# Acessar shell do container
make docker-exec-api

# Executar migrações
make docker-migrate

# Criar nova migração
make docker-migrate-create NAME="nome_da_migracao"
```

## 🔍 Testando a API

### Via Browser
Acesse http://localhost:8000/docs e teste os endpoints pela interface Swagger.

### Via cURL

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Listar instituições (exemplo)
curl http://localhost:8000/api/institutions
```

### Via HTTPie (se instalado)

```bash
http :8000/health
http :8000/api/institutions
```

## 🛑 Parar a Aplicação

```bash
# Parar sem remover containers
make docker-stop

# Parar e remover containers
make docker-down

# Parar, remover containers E volumes (apaga dados!)
make docker-down-volumes
```

## 🐛 Resolução de Problemas

### Porta 8000 já está em uso

```bash
# Descobrir o que está usando a porta
sudo lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Ou altere a porta no arquivo .env
# API_PORT=8001
```

### Erro ao conectar no banco de dados

```bash
# Verificar logs do PostgreSQL
make docker-logs-db

# Reiniciar o banco de dados
docker-compose restart postgres
```

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs api

# Reconstruir sem cache
docker-compose build --no-cache api
docker-compose up -d
```

### Limpar tudo e começar do zero

```bash
# Remove tudo (containers, imagens, volumes)
make docker-clean

# Inicie novamente
make docker-dev
```

## 📚 Documentação Adicional

- **Guia Docker Completo**: [DOCKER.md](DOCKER.md)
- **README Principal**: [README.md](README.md)
- **Guia de Contribuição**: [CONTRIBUTING.md](CONTRIBUTING.md)

## ❓ Precisa de Ajuda?

1. Verifique os logs: `make docker-logs`
2. Consulte o [DOCKER.md](DOCKER.md) para troubleshooting detalhado
3. Verifique se todas as variáveis de ambiente estão corretas no `.env`

## 🎉 Pronto!

Sua aplicação está rodando! Agora você pode:
- Acessar a documentação interativa
- Testar os endpoints
- Desenvolver novas funcionalidades
- Consultar os logs em tempo real

**Dica**: Mantenha um terminal aberto com `make docker-logs-api` para acompanhar as requisições em tempo real.

