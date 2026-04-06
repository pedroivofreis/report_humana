#!/bin/bash

# Script de inicialização rápida do Institution Service API
# Este script facilita a primeira execução da aplicação

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Institution Service API - Setup${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não está instalado!${NC}"
    echo "Por favor, instale o Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não está instalado!${NC}"
    echo "Por favor, instale o Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker e Docker Compose encontrados${NC}\n"

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado${NC}"
    
    if [ -f env.template ]; then
        echo -e "${YELLOW}📋 Criando arquivo .env a partir do template...${NC}"
        cp env.template .env
        echo -e "${GREEN}✅ Arquivo .env criado com sucesso!${NC}"
        echo -e "${YELLOW}⚠️  IMPORTANTE: Revise o arquivo .env e ajuste as configurações${NC}"
        echo -e "${YELLOW}   Especialmente SECRET_KEY e API_KEY para produção!${NC}\n"
        
        # Perguntar se o usuário quer editar agora
        read -p "Deseja editar o arquivo .env agora? (s/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo -e "${RED}❌ Template env.template não encontrado!${NC}"
        echo "Por favor, crie um arquivo .env manualmente"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Arquivo .env encontrado${NC}\n"
fi

# Perguntar se deve construir as imagens
echo -e "${YELLOW}🔨 Construindo imagens Docker...${NC}"
docker-compose build

# Perguntar se deve iniciar os containers
echo -e "\n${YELLOW}🚀 Iniciando containers...${NC}"
docker-compose up -d

echo -e "\n${YELLOW}⏳ Aguardando inicialização dos serviços...${NC}"
sleep 5

# Verificar se os containers estão rodando
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Containers iniciados com sucesso!${NC}\n"
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}🎉 Aplicação pronta para uso!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    
    echo -e "📍 URLs disponíveis:"
    echo -e "   - API: ${GREEN}http://localhost:8000${NC}"
    echo -e "   - Swagger Docs: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "   - ReDoc: ${GREEN}http://localhost:8000/redoc${NC}"
    echo -e "   - Health Check: ${GREEN}http://localhost:8000/health${NC}\n"
    
    echo -e "📊 Comandos úteis:"
    echo -e "   - Ver logs: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "   - Ver logs da API: ${YELLOW}docker-compose logs -f api${NC}"
    echo -e "   - Parar containers: ${YELLOW}docker-compose stop${NC}"
    echo -e "   - Parar e remover: ${YELLOW}docker-compose down${NC}"
    echo -e "   - Ver status: ${YELLOW}docker-compose ps${NC}\n"
    
    echo -e "🛠️  Comandos Make disponíveis:"
    echo -e "   - Ver todos comandos: ${YELLOW}make help${NC}"
    echo -e "   - Ver logs: ${YELLOW}make docker-logs${NC}"
    echo -e "   - Parar: ${YELLOW}make docker-down${NC}\n"
    
    # Perguntar se deve abrir os logs
    read -p "Deseja visualizar os logs agora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        docker-compose logs -f
    fi
else
    echo -e "${RED}❌ Erro ao iniciar containers${NC}"
    echo -e "Verifique os logs com: ${YELLOW}docker-compose logs${NC}"
    exit 1
fi

