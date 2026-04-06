# Guia de Contribuição

## Padrões de Código

Este projeto segue padrões rigorosos de qualidade de código. Antes de submeter qualquer alteração, certifique-se de seguir as diretrizes abaixo.

## Configuração do Ambiente de Desenvolvimento

1. Clone o repositório e entre no diretório:
```bash
cd api
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências de desenvolvimento:
```bash
make install-dev
# ou
pip install -r requirements-dev.txt
```

4. (Opcional) Instale os hooks de pre-commit:
```bash
pip install pre-commit
pre-commit install
```

## Padrões de Código

### Formatação

- **Indentação**: 4 espaços (nunca tabs)
- **Comprimento de linha**: Máximo 100 caracteres
- **Formatador**: Black
- **Organização de imports**: isort

### Convenções de Nomenclatura

- **Variáveis e funções**: `snake_case`
- **Classes**: `PascalCase`
- **Constantes**: `UPPER_CASE`
- **Arquivos**: `snake_case.py`
- **Módulos privados**: `_private_module.py`

### Estrutura de Imports

```python
# 1. Imports da biblioteca padrão
import os
import sys
from datetime import datetime

# 2. Imports de terceiros
from fastapi import FastAPI, HTTPException
from sqlalchemy import Column, Integer

# 3. Imports locais
from app.core.config import settings
from app.api.models.user import User
```

### Docstrings

Use docstrings no formato Google Style:

```python
def funcao_exemplo(param1: str, param2: int) -> bool:
    """Descrição breve da função.

    Descrição mais detalhada se necessário.

    Args:
        param1: Descrição do parâmetro 1
        param2: Descrição do parâmetro 2

    Returns:
        Descrição do retorno

    Raises:
        ValueError: Quando param2 é negativo
    """
    if param2 < 0:
        raise ValueError("param2 não pode ser negativo")
    return True
```

## Workflow de Desenvolvimento

### 1. Antes de Começar

```bash
# Certifique-se de estar na branch main atualizada
git checkout main
git pull origin main

# Crie uma nova branch para sua feature
git checkout -b feature/nome-da-feature
```

### 2. Durante o Desenvolvimento

```bash
# Formate o código frequentemente
make format

# Execute os linters
make lint

# Verifique os tipos
make type-check

# Ou execute tudo de uma vez
make check
```

### 3. Antes de Commitar

```bash
# Execute todos os testes
make test

# Verifique a cobertura de testes
make test-cov

# Execute a verificação completa
make check
```

### 4. Commitando

Siga o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Formato: <tipo>(<escopo>): <descrição>

# Tipos:
# - feat: Nova funcionalidade
# - fix: Correção de bug
# - docs: Alteração em documentação
# - style: Formatação, ponto e vírgula, etc
# - refactor: Refatoração de código
# - test: Adição ou correção de testes
# - chore: Atualização de dependências, etc

# Exemplos:
git commit -m "feat(hospital): add hospital CRUD endpoints"
git commit -m "fix(sector): correct validation in sector creation"
git commit -m "docs(readme): update installation instructions"
```

### 5. Antes de Abrir um Pull Request

```bash
# Execute a suite completa
make all

# Push da branch
git push origin feature/nome-da-feature
```

## Testes

### Escrevendo Testes

- Coloque os testes em `tests/`
- Nomeie arquivos de teste como `test_*.py`
- Use fixtures do pytest quando apropriado
- Teste casos de sucesso e falha
- Mantenha cobertura acima de 80%

```python
# tests/test_example.py
import pytest
from app.api.services.example import example_function

def test_example_function_success():
    """Testa o caso de sucesso."""
    result = example_function("input")
    assert result == "expected"

def test_example_function_error():
    """Testa o caso de erro."""
    with pytest.raises(ValueError):
        example_function("invalid")
```

### Executando Testes

```bash
# Todos os testes
make test

# Com cobertura
make test-cov

# Teste específico
pytest tests/test_example.py -v

# Teste específico com função
pytest tests/test_example.py::test_example_function_success -v
```

## Migrações de Banco de Dados

### Criando Migrações

```bash
# Após modificar os modelos, crie uma migração
make migrate-create NAME="descricao_da_mudanca"
```

### Aplicando Migrações

```bash
make migrate
```

### Revertendo Migrações

```bash
make migrate-rollback
```

## Checklist antes do Pull Request

- [ ] Código está formatado (`make format`)
- [ ] Sem erros de linting (`make lint`)
- [ ] Tipos verificados (`make type-check`)
- [ ] Todos os testes passam (`make test`)
- [ ] Cobertura de testes adequada
- [ ] Documentação atualizada
- [ ] Commits seguem Conventional Commits
- [ ] Branch atualizada com main

## Dúvidas?

Se tiver dúvidas sobre os padrões ou processo, abra uma issue ou entre em contato com a equipe.
