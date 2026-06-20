# FastAPI Async Boilerplate

A production-ready FastAPI boilerplate with async SQLAlchemy, generic BaseRepository pattern, JWT authentication, and Docker Compose.

## Architecture

```
Router  →  Service  →  Repository  →  Database
  ↓          ↓           ↓
Schema    Business    BaseRepository
(Pydantic) Logic     (Generic CRUD)
```

## Structure

```
src/
├── main.py                          # Application entry point
├── core/                            # Shared infrastructure
│   ├── config.py                    # Settings (env vars)
│   ├── logging.py                   # Structured logging
│   ├── exceptions.py                # Custom exceptions
│   ├── database/
│   │   └── session.py               # Async session management
│   ├── models/
│   │   └── base.py                  # Base model (UUID + Timestamps + SoftDelete)
│   ├── repositories/
│   │   └── base_repository.py       # Generic CRUD repository
│   ├── utils/
│   │   └── pagination.py            # Page[T] + PaginationParams
│   └── middleware/
│       ├── exceptions.py            # Global exception handler
│       └── auth/
│           ├── exceptions.py        # Global exception handler
│           ├── permission_list.py   # Permission definitions
│           └── role_list.py         # Role → Permission mappings
├── app/
│   ├── routes.py                    # Main router (includes all feature routers)
│   └── items/                       # ✅ Example feature (complete CRUD)
│       ├── model.py                 # SQLAlchemy model
│       ├── schema.py                # Pydantic schemas (Create/Update/Filter/Response)
│       ├── repository.py            # Extends BaseRepository
│       ├── service.py               # Business logic
│       └── router.py                # API endpoints
└── scripts/
    └── seed.py                      # Example seed script
```

## Quick Start

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env with your values
```

### 2. Start everything

```bash
make up
```

This will:
- Create Docker network
- Start PostgreSQL + FastAPI backend
- Run database migrations

### 3. Access the API

- **API Docs**: http://localhost:8005/docs
- **Health Check**: http://localhost:8005/health
- **Items API**: http://localhost:8005/api/items

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all containers + migrate |
| `make down` | Stop containers |
| `make fclean` | Stop + remove volumes |
| `make rebuild` | Rebuild + restart |
| `make migrate` | Run Alembic migrations |
| `make migration msg="your message"` | Create a new migration |
| `make seed` | Seed example data |
| `make logs` | Tail backend logs |
| `make status` | Show container status |
| `make shell` | Open shell in backend |
| `make test` | Run tests |
| `make check` | Health check |
| `make help` | Show all commands |

## BaseRepository

The `BaseRepository` provides a complete set of CRUD operations out of the box:

### Available Methods

| Method | Description |
|--------|-------------|
| `create(obj_in)` | Create a single record |
| `create_many(objs_in)` | Bulk create records |
| `get_by_id(obj_id)` | Get by primary key |
| `get_by_id_or_raise(obj_id)` | Get by PK or raise ValueError |
| `get_first(filters)` | Get first matching record |
| `list(params, filters, order_by)` | **Paginated** list |
| `list_raw(skip, limit, filters)` | Raw list (no pagination wrapper) |
| `count(filters)` | Count matching records |
| `exists(filters)` | Check if any record matches |
| `update(obj, obj_in)` | Update from Pydantic schema |
| `update_from_dict(obj, data)` | Update from dictionary |
| `update_many(ids, data)` | Bulk update by IDs |
| `update_with_filter(filters, data)` | Update matching records |
| `delete(obj_id)` | Soft-delete |
| `delete(obj_id, hard=True)` | Hard-delete |
| `delete_many(ids)` | Bulk soft-delete |
| `delete_with_filter(filters)` | Delete matching records |
| `restore(obj_id)` | Restore soft-deleted |
| `restore_many(ids)` | Bulk restore |

### Key Features

- **Soft Delete**: All deletes are soft by default (`deleted_on` timestamp)
- **Pagination**: Built-in `Page[T]` response with metadata
- **Filtering**: Abstract `build_filter_conditions()` for custom filters
- **Ordering**: `ORDER_BY_MAP` for safe, configurable sorting
- **Relationships**: Eager loading via `default_relationships()`
- **Type Safety**: Full generics `Repository[Model, Create, Update, Filter]`

## Creating a New Feature

### 1. Create the module

```bash
mkdir -p src/app/products
touch src/app/products/__init__.py
```

### 2. Define the model (`model.py`)

```python
from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from core.models.base import Base

class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
```

### 3. Define schemas (`schema.py`)

```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    price: float = Field(..., gt=0)
    description: str | None = None

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(None, gt=0)
    description: str | None = None

class ProductFilter(BaseModel):
    name: str | None = None

class ProductResponse(BaseModel):
    id: UUID
    name: str
    price: float
    description: str | None
    created_on: datetime
    updated_on: datetime
    model_config = {"from_attributes": True}
```

### 4. Create repository (`repository.py`)

```python
from typing import Annotated, List, Sequence
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import ColumnElement

from app.products.model import Product
from app.products.schema import ProductCreate, ProductUpdate, ProductFilter
from core.database.session import get_db_session
from core.repositories.base_repository import Repository

class ProductRepository(Repository[Product, ProductCreate, ProductUpdate, ProductFilter]):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db_session)]):
        super().__init__(Product, session=session)

    ORDER_BY_MAP = {
        "name": Product.name.asc(),
        "-name": Product.name.desc(),
        "created_on": Product.created_on.asc(),
        "-created_on": Product.created_on.desc(),
    }

    def default_relationships(self) -> Sequence[_AbstractLoad]:
        return []

    def build_filter_conditions(self, filters: ProductFilter | None) -> List[ColumnElement[bool]]:
        if not filters:
            return []
        conditions = []
        if filters.name:
            conditions.append(self.model.name.ilike(f"%{filters.name}%"))
        return conditions
```

### 5. Create service & router (follow the Items example)

### 6. Register the router

```python
# src/app/routes.py
from app.products.router import router as products_router
api_router.include_router(products_router)
```

### 7. Import model in alembic/env.py

```python
from src.app.products.model import Product  # noqa: F401
```

### 8. Create migration

```bash
make migration msg="add products table"
make migrate
```

## Development Tools

- **black** — Code formatting
- **isort** — Import sorting
- **flake8** — Linting
- **mypy** — Type checking
- **pytest** — Testing
- **bandit** — Security scanning
- **pre-commit** — Git hooks
- **gitleaks** — Secret detection

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL |
| Migrations | Alembic |
| Auth | JWT (PyJWT + bcrypt) |
| Validation | Pydantic v2 |
| Container | Docker + Docker Compose |
| Package Manager | Poetry |
| Python | 3.10 - 3.13 |
# fastapi-boilerplate# storage-manager-backend
# storage-manager-backend
