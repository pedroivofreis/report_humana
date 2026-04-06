# Guia de Desenvolvimento - User Service API

## Estrutura de Exceptions

### Exceptions Customizadas

O projeto utiliza exceptions customizadas localizadas em `app/core/exceptions.py`. **NUNCA** utilize `HTTPException` do FastAPI diretamente nos serviços.

#### Exceptions Disponíveis

1. **NotFoundException** - Para recursos não encontrados (404)
   ```python
   from app.core.exceptions import NotFoundException

   if not user:
       raise NotFoundException("Usuário não encontrado")
   ```

2. **BadRequestException** - Para requisições inválidas (400)
   ```python
   from app.core.exceptions import BadRequestException

   if email_already_exists:
       raise BadRequestException("Email já cadastrado")
   ```

3. **ResourceNotFoundException** - Para recursos específicos não encontrados (404)
   ```python
   from app.core.exceptions import ResourceNotFoundException

   raise ResourceNotFoundException("User", user_id)
   ```

4. **ResourceAlreadyExistsException** - Para recursos duplicados (409)
   ```python
   from app.core.exceptions import ResourceAlreadyExistsException

   raise ResourceAlreadyExistsException("User")
   ```

5. **ValidationException** - Para erros de validação (400)
   ```python
   from app.core.exceptions import ValidationException

   raise ValidationException("Dados inválidos")
   ```

### Exception Handlers

Os handlers estão registrados em `app/api/middlewares/exception_handler.py` e configurados no `main.py`.

#### Como Adicionar Novas Exceptions

1. **Criar a exception** em `app/core/exceptions.py`:
   ```python
   class MinhaNovaException(DomainException):
       """Descrição da exception."""

       def __init__(self, message: str):
           self.message = message
           super().__init__(message)
   ```

2. **Criar o handler** em `app/api/middlewares/exception_handler.py`:
   ```python
   async def minha_nova_exception_handler(request: Request, exc: Exception) -> JSONResponse:
       """Handle MinhaNovaException."""
       assert isinstance(exc, MinhaNovaException)
       logger.warning("minha_nova_exception", message=exc.message, path=request.url.path)
       return JSONResponse(
           status_code=status.HTTP_XXX_STATUS_CODE,
           content={"detail": exc.message}
       )
   ```

3. **Registrar no main.py**:
   ```python
   from app.core.exceptions import MinhaNovaException
   from app.api.middlewares.exception_handler import minha_nova_exception_handler

   app.add_exception_handler(MinhaNovaException, minha_nova_exception_handler)
   ```

## Padrão de Arquitetura

### Camadas da Aplicação

```
Router (Apresentação)
    ↓
Service (Lógica de Negócio)
    ↓
Repository (Acesso a Dados)
    ↓
Model (Banco de Dados)
```

### 1. Models (app/api/models/)

Define as tabelas do banco de dados usando SQLAlchemy.

```python
"""Nome do model module."""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class MinhaTabela(Base):
    """Descrição do model."""

    __tablename__ = "minha_tabela"

    id = Column(String(length=36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    campo1 = Column(String(255), nullable=False)
    campo2 = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    relacionamento = relationship("OutraTabela", back_populates="campo")
```

### 2. Schemas (app/api/schemas/)

Define os contratos de entrada/saída da API usando Pydantic.

```python
"""Nome do schema module."""

from datetime import datetime
import pydantic


class MinhaEntidadeResponse(pydantic.BaseModel):
    """Response schema."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: str
    campo1: str
    campo2: bool
    created_at: datetime
    updated_at: datetime | None = None


class MinhaEntidadeCreateRequest(pydantic.BaseModel):
    """Create request schema."""

    campo1: str
    campo2: bool = True


class MinhaEntidadeUpdateRequest(pydantic.BaseModel):
    """Update request schema."""

    campo1: str | None = None
    campo2: bool | None = None
```

### 3. Repositories (app/api/repositories/)

Gerencia o acesso direto ao banco de dados. **Sempre use AsyncSession**.

```python
"""Nome do repository module."""

import logging
from fastapi import Depends
from sqlalchemy import select
from app.api.models.minha_tabela import MinhaTabela
from app.api.schemas.minha_entidade import (
    MinhaEntidadeCreateRequest,
    MinhaEntidadeUpdateRequest,
)
from app.db.session import AsyncSession, get_db_session

logger = logging.getLogger(__name__)


class MinhaEntidadeRepository:
    """Descrição do repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        """Initialize repository."""
        logger.info("Initializing MinhaEntidadeRepository")
        self.db = db

    async def get_by_id(self, entity_id: UUID) -> MinhaTabela | None:
        """Get entity by id."""
        logger.info(f"Getting entity by id: {entity_id}")
        result = await self.db.execute(
            select(MinhaTabela).filter(MinhaTabela.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def create(self, entity: MinhaEntidadeCreateRequest) -> MinhaTabela:
        """Create entity."""
        logger.info("Creating entity")
        db_entity = MinhaTabela(**entity.model_dump(exclude_unset=True))
        self.db.add(db_entity)
        await self.db.commit()
        await self.db.refresh(db_entity)
        return db_entity

    async def update(
        self, entity_id: UUID, entity_update: MinhaEntidadeUpdateRequest
    ) -> MinhaTabela | None:
        """Update entity."""
        logger.info(f"Updating entity: {entity_id}")
        db_entity = await self.get_by_id(entity_id)
        if not db_entity:
            return None

        update_data = entity_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_entity, field, value)

        await self.db.commit()
        await self.db.refresh(db_entity)
        return db_entity

    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity."""
        logger.info(f"Deleting entity: {entity_id}")
        db_entity = await self.get_by_id(entity_id)
        if not db_entity:
            return False

        await self.db.delete(db_entity)
        await self.db.commit()
        return True
```

### 4. Services (app/api/services/)

Contém a lógica de negócio. **Use Depends para injetar repositories**.

```python
"""Nome do service module."""

import logging
from fastapi import Depends
from app.api.models.minha_tabela import MinhaTabela
from app.api.repositories.minha_entidade import MinhaEntidadeRepository
from app.api.schemas.minha_entidade import (
    MinhaEntidadeCreateRequest,
    MinhaEntidadeUpdateRequest,
)
from app.core.exceptions import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)


class MinhaEntidadeService:
    """Descrição do service."""

    def __init__(
        self,
        repository: MinhaEntidadeRepository = Depends(MinhaEntidadeRepository),
    ):
        """Initialize service."""
        logger.info("Initializing MinhaEntidadeService")
        self.repository = repository

    async def get_by_id(self, entity_id: UUID) -> MinhaTabela:
        """Get entity by id."""
        logger.info(f"Getting entity by id: {entity_id}")

        entity = await self.repository.get_by_id(entity_id)
        if not entity:
            raise NotFoundException("Entidade não encontrada")

        return entity

    async def create(self, entity: MinhaEntidadeCreateRequest) -> MinhaTabela:
        """Create entity."""
        logger.info("Creating entity")

        # Validações de negócio aqui
        if not entity.campo1:
            raise BadRequestException("Campo1 é obrigatório")

        return await self.repository.create(entity)

    async def update(
        self, entity_id: UUID, entity: MinhaEntidadeUpdateRequest
    ) -> MinhaTabela:
        """Update entity."""
        logger.info(f"Updating entity: {entity_id}")

        # Verificar se existe
        existing = await self.repository.get_by_id(entity_id)
        if not existing:
            raise NotFoundException("Entidade não encontrada")

        # Validações de negócio aqui

        updated = await self.repository.update(entity_id, entity)
        if not updated:
            raise NotFoundException("Entidade não encontrada")

        return updated

    async def delete(self, entity_id: UUID) -> None:
        """Delete entity."""
        logger.info(f"Deleting entity: {entity_id}")

        deleted = await self.repository.delete(entity_id)
        if not deleted:
            raise NotFoundException("Entidade não encontrada")
```

### 5. Routers (app/api/routers/)

Define os endpoints da API. **Sempre use async e Depends para injetar services**.

```python
"""Nome do router module."""

import structlog
from fastapi import APIRouter, Depends, status
from app.api.schemas.minha_entidade import (
    MinhaEntidadeCreateRequest,
    MinhaEntidadeResponse,
    MinhaEntidadeUpdateRequest,
)
from app.api.services.minha_entidade import MinhaEntidadeService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/minha-entidade", tags=["minha-entidade"])


@router.get(
    "/{entity_id}",
    response_model=MinhaEntidadeResponse,
    status_code=status.HTTP_200_OK,
    description="Endpoint description.",
)
async def get_entity(
    entity_id: UUID,
    service: MinhaEntidadeService = Depends(MinhaEntidadeService),
) -> MinhaEntidadeResponse:
    """
    Get entity by id.

    Args:
        entity_id: Entity id.
        service: Service dependency.

    Returns:
        MinhaEntidadeResponse: Entity.
    """
    logger.info("Getting entity by id")
    logger.info(f"Entity id: {entity_id}")
    entity = await service.get_by_id(entity_id)
    return MinhaEntidadeResponse.model_validate(entity)


@router.post(
    "",
    response_model=MinhaEntidadeResponse,
    status_code=status.HTTP_201_CREATED,
    description="Endpoint description.",
)
async def create_entity(
    entity: MinhaEntidadeCreateRequest,
    service: MinhaEntidadeService = Depends(MinhaEntidadeService),
) -> MinhaEntidadeResponse:
    """
    Create entity.

    Args:
        entity: Entity data.
        service: Service dependency.

    Returns:
        MinhaEntidadeResponse: Entity.
    """
    logger.info("Creating entity")
    created = await service.create(entity)
    return MinhaEntidadeResponse.model_validate(created)


@router.patch(
    "/{entity_id}",
    response_model=MinhaEntidadeResponse,
    status_code=status.HTTP_200_OK,
    description="Endpoint description.",
)
async def update_entity(
    entity_id: UUID,
    entity: MinhaEntidadeUpdateRequest,
    service: MinhaEntidadeService = Depends(MinhaEntidadeService),
) -> MinhaEntidadeResponse:
    """
    Update entity.

    Args:
        entity_id: Entity id.
        entity: Entity data.
        service: Service dependency.

    Returns:
        MinhaEntidadeResponse: Entity.
    """
    logger.info("Updating entity")
    logger.info(f"Entity id: {entity_id}")
    updated = await service.update(entity_id, entity)
    return MinhaEntidadeResponse.model_validate(updated)


@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Endpoint description.",
)
async def delete_entity(
    entity_id: UUID,
    service: MinhaEntidadeService = Depends(MinhaEntidadeService),
) -> None:
    """
    Delete entity.

    Args:
        entity_id: Entity id.
        service: Service dependency.

    Returns:
        None.
    """
    logger.info("Deleting entity")
    logger.info(f"Entity id: {entity_id}")
    await service.delete(entity_id)
```

## Migrations com Alembic

### Criar uma nova migration

```bash
# Definir PYTHONPATH e ativar venv
export PYTHONPATH=/caminho/para/projeto:$PYTHONPATH
source venv/bin/activate

# Criar migration
alembic revision -m "descricao_da_migration"

# Editar o arquivo gerado em alembic/versions/

# Aplicar migration
alembic upgrade head
```

### Padrão de Migration

```python
"""descricao_da_migration

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2025-12-28 XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from app.api.schemas.meus_enums import MeuEnum

# revision identifiers, used by Alembic.
revision = "xxxxx"
down_revision = "yyyyy"
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela
    op.create_table(
        "minha_tabela",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("campo1", sa.String(length=255), nullable=False),
        sa.Column("campo_enum", sa.Enum(MeuEnum, name="meuenum"), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["foreign_id"], ["outra_tabela.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_minha_tabela_id"), "minha_tabela", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_minha_tabela_id"), table_name="minha_tabela")
    op.drop_table("minha_tabela")
```

## Logging

Use `structlog` nos routers e `logging` nos services/repositories:

```python
import structlog
logger = structlog.get_logger(__name__)

# Nos routers
logger.info("Operação realizada", campo1="valor1", campo2="valor2")
```

```python
import logging
logger = logging.getLogger(__name__)

# Nos services/repositories
logger.info(f"Operação realizada: {detalhes}")
```

## Boas Práticas

1. ✅ **SEMPRE** use exceptions customizadas do projeto
2. ✅ **SEMPRE** use `async/await` para operações de banco
3. ✅ **SEMPRE** use `Depends()` para injeção de dependências
4. ✅ **SEMPRE** documente classes e métodos em inglês
5. ✅ **SEMPRE** adicione logs informativos
6. ✅ **SEMPRE** valide dados de entrada nos services
7. ✅ **SEMPRE** use type hints
8. ✅ **SEMPRE** registre migrations no `app/db/base.py`
9. ✅ **SEMPRE** use nomes de campos, classes, variáveis e enums em inglês
10. ✅ **SEMPRE** use snake_case para nomes de colunas do banco
11. ✅ **SEMPRE** use PascalCase para nomes de classes e enums

12. ❌ **NUNCA** use `HTTPException` do FastAPI diretamente
13. ❌ **NUNCA** use operações síncronas de banco (`.query()`, `.commit()` sem `await`)
14. ❌ **NUNCA** coloque lógica de negócio nos routers
15. ❌ **NUNCA** acesse o banco diretamente dos services (use repositories)
16. ❌ **NUNCA** esqueça de adicionar o model em `app/db/base.py`
17. ❌ **NUNCA** use português para nomes de variáveis, campos ou classes

## Checklist de Nova Feature

- [ ] Model criado em `app/api/models/`
- [ ] Model adicionado em `app/db/base.py`
- [ ] Schemas criados em `app/api/schemas/`
- [ ] Repository criado em `app/api/repositories/`
- [ ] Service criado em `app/api/services/`
- [ ] Router criado em `app/api/routers/`
- [ ] Router registrado em `app/api/api.py`
- [ ] Migration criada e aplicada
- [ ] Exceptions customizadas utilizadas
- [ ] Testes criados (se aplicável)
- [ ] Documentação atualizada

## Exemplo Completo

Veja os módulos de `user` e `complementary_data` como referência completa de implementação.
