# 🚀 Checklist de Deployment para Produção

Este documento fornece um guia passo a passo para fazer deploy da aplicação em produção.

## ⚠️ Antes do Deployment

### 1. Segurança

- [ ] **Gerar SECRET_KEY seguro**
  ```bash
  openssl rand -hex 32
  ```

- [ ] **Gerar API_KEY seguro**
  ```bash
  openssl rand -hex 32
  ```

- [ ] **Configurar senha forte do PostgreSQL**
  ```bash
  openssl rand -base64 32
  ```

- [ ] **Atualizar variáveis de ambiente no servidor**
  - SECRET_KEY
  - API_KEY
  - POSTGRES_PASSWORD
  - ENVIRONMENT=production
  - LOG_LEVEL=INFO ou WARNING

- [ ] **Configurar CORS apropriadamente**
  - Remover `allow_origins=["*"]` do código
  - Configurar domínios específicos permitidos

### 2. Infraestrutura

- [ ] **Servidor/VM provisionado**
  - CPU: Mínimo 2 cores
  - RAM: Mínimo 2GB
  - Disco: Mínimo 20GB

- [ ] **Docker e Docker Compose instalados**
  ```bash
  # Verificar versões
  docker --version
  docker-compose --version
  ```

- [ ] **Firewall configurado**
  - Porta 80 (HTTP) aberta
  - Porta 443 (HTTPS) aberta
  - Porta 22 (SSH) aberta apenas para IPs confiáveis
  - Porta 5432 (PostgreSQL) FECHADA externamente

- [ ] **Domínio configurado**
  - DNS apontando para o servidor
  - Certificado SSL obtido (Let's Encrypt recomendado)

### 3. Configuração do Ambiente

- [ ] **Criar arquivo .env de produção**
  ```bash
  cp env.template .env
  # Editar com valores de produção
  ```

- [ ] **Configurar backup automático do banco**
  - Script de backup diário
  - Armazenamento externo (S3, backup remoto, etc.)

- [ ] **Configurar monitoramento**
  - Health checks automáticos
  - Alertas de erro
  - Métricas de performance

## 📦 Processo de Deployment

### Opção 1: Deployment Manual

#### Passo 1: Preparar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker (se necessário)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Passo 2: Clonar o Repositório

```bash
cd /opt
sudo git clone <URL_DO_REPOSITORIO> institution-service-api
cd institution-service-api
```

#### Passo 3: Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
sudo cp env.template .env
sudo nano .env  # ou vim

# Garantir que SECRET_KEY, API_KEY e senhas estão configuradas
```

#### Passo 4: Iniciar a Aplicação

```bash
# Usando docker-compose de produção
sudo docker-compose -f docker-compose.prod.yml up -d --build

# Verificar logs
sudo docker-compose -f docker-compose.prod.yml logs -f
```

#### Passo 5: Configurar Nginx (Opcional mas Recomendado)

```bash
# Se usar o Nginx do docker-compose
sudo cp nginx.conf.example nginx.conf
sudo nano nginx.conf  # Ajustar configurações

# Iniciar com Nginx
sudo docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

### Opção 2: Deployment Automatizado (CI/CD)

#### GitHub Actions Example

Crie `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Copy files via SSH
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          source: "."
          target: "/opt/institution-service-api"
      
      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/institution-service-api
            docker-compose -f docker-compose.prod.yml down
            docker-compose -f docker-compose.prod.yml up -d --build
            docker-compose -f docker-compose.prod.yml logs --tail=50
```

## 🔒 SSL/HTTPS Configuration

### Let's Encrypt com Certbot

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Renovação automática (já configurada pelo certbot)
sudo certbot renew --dry-run
```

### Configurar SSL no Nginx

Descomente a seção HTTPS no `nginx.conf` e ajuste os caminhos dos certificados.

## 📊 Monitoramento e Logs

### 1. Health Checks

```bash
# Configurar healthcheck automático
curl https://seu-dominio.com/health

# Com monitoramento (exemplo: UptimeRobot, Pingdom)
# Configurar para verificar /health a cada 5 minutos
```

### 2. Logs Centralizados

```bash
# Ver logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f api

# Logs do PostgreSQL
docker-compose -f docker-compose.prod.yml logs -f postgres

# Exportar logs para arquivo
docker-compose -f docker-compose.prod.yml logs --no-color > logs.txt
```

### 3. Métricas (Opcional)

Considere adicionar:
- Prometheus para métricas
- Grafana para visualização
- Sentry para tracking de erros

## 🔄 Backup e Recuperação

### Backup do Banco de Dados

#### Script de Backup Manual

```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

mkdir -p $BACKUP_DIR

docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres places_db | gzip > $BACKUP_FILE

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup criado: $BACKUP_FILE"
```

#### Agendar Backup (Cron)

```bash
# Editar crontab
crontab -e

# Adicionar linha para backup diário às 2h da manhã
0 2 * * * /opt/institution-service-api/backup-db.sh >> /var/log/backup.log 2>&1
```

### Restauração

```bash
# Restaurar de backup
gunzip < backup_20240107_020000.sql.gz | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres -d places_db
```

## 🔧 Manutenção

### Atualização da Aplicação

```bash
# Pull das últimas mudanças
cd /opt/institution-service-api
git pull origin main

# Rebuild e restart
docker-compose -f docker-compose.prod.yml up -d --build

# Executar migrações se necessário
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### Limpeza de Recursos

```bash
# Remover imagens antigas
docker image prune -a

# Remover volumes não utilizados (CUIDADO!)
docker volume prune

# Limpar logs do Docker
truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

### Monitorar Recursos

```bash
# Uso de disco
df -h

# Uso de memória e CPU dos containers
docker stats

# Ver processos
docker-compose -f docker-compose.prod.yml ps
```

## 🚨 Troubleshooting em Produção

### Container não inicia

```bash
# Ver logs detalhados
docker-compose -f docker-compose.prod.yml logs api

# Verificar recursos
docker stats
free -h
df -h
```

### Performance lenta

```bash
# Aumentar workers do Uvicorn
# No docker-compose.prod.yml, ajuste:
# --workers 4  (ajuste conforme CPUs disponíveis)

# Verificar queries lentas no PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -d places_db \
  -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker-compose -f docker-compose.prod.yml ps postgres

# Reiniciar PostgreSQL
docker-compose -f docker-compose.prod.yml restart postgres

# Verificar logs
docker-compose -f docker-compose.prod.yml logs postgres
```

## ✅ Checklist Final

Antes de considerar o deployment completo:

- [ ] Aplicação acessível via HTTPS
- [ ] Health check respondendo corretamente
- [ ] Logs sendo gerados corretamente
- [ ] Backup automático configurado e testado
- [ ] Monitoramento/alertas configurados
- [ ] Documentação atualizada
- [ ] Variáveis de ambiente seguras
- [ ] Firewall configurado corretamente
- [ ] SSL válido e renovação automática configurada
- [ ] Processo de rollback testado
- [ ] Equipe treinada em procedimentos de manutenção

## 📞 Contatos e Recursos

- **Documentação da API**: https://seu-dominio.com/docs
- **Status Page**: (configurar uptimerobot ou similar)
- **Repositório**: <URL_DO_GIT>
- **Logs**: `docker-compose -f docker-compose.prod.yml logs -f`

---

**Última atualização**: 2026-01-07

