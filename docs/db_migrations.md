# Database Migrations

This guide explains how to handle database migrations when using `aiogram-sqlalchemy-storage`, including using the storage's metadata and integrating with Alembic.

## Table of Contents
- [Overview](#overview)
- [Using Storage Metadata](#using-storage-metadata)
- [Alembic Integration](#alembic-integration)
- [Migration Strategies](#migration-strategies)
- [Best Practices](#best-practices)

## Overview

When using `SQLAlchemyStorage`, the FSM table is automatically added to your metadata. This means you need to consider the storage table when setting up migrations for your application.

## Using Storage Metadata

The `SQLAlchemyStorage` modifies the metadata you pass to it by adding the FSM table definition. You should use the storage's metadata for creating tables and migrations.

### Basic Migration Setup

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy_storage import SQLAlchemyStorage

# Setup database
engine = create_async_engine("sqlite+aiosqlite:///database.db")
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Your application models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)

# Initialize storage (this adds FSM table to metadata)
storage = SQLAlchemyStorage(sessionmaker=SessionLocal, metadata=Base.metadata)

# Create all tables including FSM storage
async def init_db():
    async with engine.begin() as conn:
        # This will create both your models AND the FSM storage table
        await conn.run_sync(Base.metadata.create_all)
```

### Manual Table Creation

If you prefer more control over table creation:

```python
async def create_tables():
    async with engine.begin() as conn:
        # Create only specific tables
        await conn.run_sync(Base.metadata.tables['users'].create, checkfirst=True)
        await conn.run_sync(Base.metadata.tables['aiogram_fsm_data'].create, checkfirst=True)
```

## Alembic Integration

Alembic is the recommended migration tool for SQLAlchemy applications. Here's how to integrate it with `aiogram-sqlalchemy-storage`.

### Initial Setup

1. **Install Alembic:**
```bash
pip install alembic
```

2. **Initialize Alembic in your project:**
```bash
alembic init alembic
```

3. **Configure Alembic (`alembic.ini`):**
```ini
# Database URL
sqlalchemy.url = sqlite+aiosqlite:///database.db

# For async databases, you might need:
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

### Configure env.py

Update your `alembic/env.py` to include the storage metadata:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# Import your models and storage
from your_app.models import Base  # Your declarative base
from your_app.storage import storage  # Your configured storage instance

# This is the Alembic Config object
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata - IMPORTANT: use the storage's metadata
# This ensures FSM table is included in migrations
target_metadata = storage.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    import asyncio
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Alternative env.py for Sync Databases

If you're using synchronous database connections:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your configured storage
from your_app.storage import storage

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use storage metadata that includes FSM table
target_metadata = storage.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Generate Initial Migration

Create your first migration that includes the FSM table:

```bash
alembic revision --autogenerate -m "Initial migration with FSM storage"
```

### Apply Migrations

```bash
# Apply migrations
alembic upgrade head

# Check current revision
alembic current

# Show migration history
alembic history
```

## Migration Strategies

### Strategy 1: Include FSM Table in App Migrations

**Pros:**
- Single migration system
- FSM table versioned with your app
- Consistent database state

**Cons:**
- FSM table changes might interfere with app migrations

```python
# Configure storage before creating migrations
storage = SQLAlchemyStorage(sessionmaker=SessionLocal, metadata=Base.metadata)
# Now Base.metadata includes FSM table
```

### Strategy 2: Separate FSM Migrations

**Pros:**
- FSM changes isolated from app changes
- More control over FSM table evolution

**Cons:**
- Two migration systems to manage
- Potential for inconsistency

```python
# Create separate metadata for FSM
fsm_metadata = MetaData()
storage = SQLAlchemyStorage(sessionmaker=SessionLocal, metadata=fsm_metadata)

# Separate Alembic configuration for FSM
# alembic init fsm_migrations
```

### Strategy 3: Manual FSM Table Management

**Pros:**
- Full control over FSM table
- No migration complexity

**Cons:**
- Manual work required
- Risk of forgetting updates

```python
# Create FSM table manually before initializing storage
async def ensure_fsm_table():
    async with engine.begin() as conn:
        # Check if table exists, create if not
        await conn.run_sync(storage.metadata.create_all)
```

## Best Practices

### 1. Initialize Storage Early
Always initialize your storage before generating migrations:

```python
# config.py or models.py
storage = SQLAlchemyStorage(sessionmaker=SessionLocal, metadata=Base.metadata)
```

### 2. Version Control Migrations
Always commit your migration files to version control:

```bash
git add alembic/versions/
git commit -m "Add migration for FSM storage"
```

### 3. Test Migrations
Test your migrations on a copy of production data:

```bash
# Create database backup
# Run migration on copy
alembic upgrade head
```

### 4. Custom Table Names
When using custom table names, ensure consistency:

```python
# Use the same table name across environments
storage = SQLAlchemyStorage(
    sessionmaker=SessionLocal,
    metadata=Base.metadata,
    table_name=os.getenv('FSM_TABLE_NAME', 'aiogram_fsm_data')
)
```

### 5. Environment-Specific Configurations

```python
# development.py
storage = SQLAlchemyStorage(
    sessionmaker=DevSessionLocal,
    metadata=Base.metadata,
    table_name='dev_aiogram_fsm_data'
)

# production.py
storage = SQLAlchemyStorage(
    sessionmaker=ProdSessionLocal,
    metadata=Base.metadata,
    table_name='aiogram_fsm_data'
)
```

## Troubleshooting

### Common Issues

1. **FSM table not included in migrations:**
   - Ensure you're using `storage.metadata` as target_metadata
   - Initialize storage before generating migrations

2. **Migration conflicts:**
   - Use `alembic merge` to resolve conflicts
   - Consider separate migration branches for major changes

3. **Table already exists errors:**
   - Use `checkfirst=True` when creating tables manually
   - Ensure migrations are properly tracked

### Migration Rollback

```bash
# Rollback to previous revision
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

This migration guide ensures your FSM storage integrates smoothly with your application's database evolution strategy.
