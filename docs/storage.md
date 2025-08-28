# SQLAlchemy Storage for aiogram FSM

This document provides detailed information about the `SQLAlchemyStorage` class and its usage with aiogram FSM.

## Table of Contents
- [Overview](#overview)
- [Class Reference](#class-reference)
- [Configuration](#configuration)
- [Database Model](#database-model)
- [Methods](#methods)
- [Advanced Usage](#advanced-usage)
- [Migration Guide](#migration-guide)

## Overview

`SQLAlchemyStorage` is a storage backend for aiogram's Finite State Machine (FSM) that persists state and data using SQLAlchemy. It provides asynchronous database operations and full compatibility with aiogram's storage interface.

## Class Reference

### Constructor

```python
SQLAlchemyStorage(
    sessionmaker: sessionmaker[AsyncSession],
    metadata: MetaData = MetaData(),
    table_name: Optional[str] = 'aiogram_fsm_data',
    key_builder: Optional[KeyBuilder] = None,
    json_dumps: _JsonDumps = json.dumps,
    json_loads: _JsonLoads = json.loads,
)
```

#### Parameters

- **`sessionmaker`** (required): SQLAlchemy async sessionmaker instance
- **`metadata`**: SQLAlchemy MetaData instance for table creation
- **`table_name`**: Name of the database table (default: `'aiogram_fsm_data'`)
- **`key_builder`**: Custom key builder for storage keys (default: `DefaultKeyBuilder`)
- **`json_dumps`**: JSON serialization function (default: `json.dumps`)
- **`json_loads`**: JSON deserialization function (default: `json.loads`)

## Configuration

### Basic Setup

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy_storage import SQLAlchemyStorage

# Create engine and sessionmaker
engine = create_async_engine("sqlite+aiosqlite:///database.db")
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Initialize storage
storage = SQLAlchemyStorage(
    sessionmaker=SessionLocal,
    metadata=Base.metadata,  # Recommended: avoid passing empty metadata
    table_name="custom_fsm_table"  # Optional: custom table name
)
```

### Custom JSON Serialization

```python
import orjson

storage = SQLAlchemyStorage(
    sessionmaker=SessionLocal,
    metadata=Base.metadata,
    json_dumps=orjson.dumps,
    json_loads=orjson.loads
)
```

### Custom Key Builder

```python
from aiogram.fsm.storage.base import KeyBuilder

class CustomKeyBuilder(KeyBuilder):
    def build(self, key: StorageKey) -> str:
        return f"custom_{key.bot_id}_{key.chat_id}_{key.user_id}"

storage = SQLAlchemyStorage(
    sessionmaker=SessionLocal,
    metadata=Base.metadata,
    key_builder=CustomKeyBuilder()
)
```

## Database Model

The storage automatically creates a table with the following structure:

```sql
CREATE TABLE aiogram_fsm_data (
    id VARCHAR PRIMARY KEY,
    state VARCHAR NULL,
    data VARCHAR NULL
);
```

### Fields

- **`id`**: Primary key built from bot_id, chat_id, and user_id
- **`state`**: Current FSM state as string
- **`data`**: JSON-serialized user data

### Database Initialization

The `SQLAlchemyStorage` modifies the metadata passed to it by adding the FSM table definition. If no metadata is provided, it creates a new one. You can access the metadata through `SQLAlchemyStorage.metadata` to create all tables including the FSM storage table.

```python
async def init_database():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Run once at application startup
import asyncio
asyncio.run(init_database())
```

### Connection Pool Configuration

```python
from sqlalchemy.pool import StaticPool

engine = create_async_engine(
    "sqlite+aiosqlite:///database.db",
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=True  # Enable SQL logging for debugging
)
```

## Migration Guide

### From Base Parameter (Deprecated)

**Old way (deprecated):**
```python
Base = declarative_base()
storage = SQLAlchemyStorage(sessionmaker=SessionLocal, metadata=Base)
```

**New way:**
```python
Base = declarative_base()
storage = SQLAlchemyStorage(sessionmaker=SessionLocal, metadata=Base.metadata)
```

### Session Factory Changes

The storage expects a `sessionmaker[AsyncSession]` instance. Make sure your sessionmaker is configured for async operations:

```python
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # Recommended for FSM usage
)
```

## Best Practices

1. **Connection Management**: Use connection pooling for production deployments
2. **Table Names**: Use descriptive table names when running multiple bots
3. **JSON Serialization**: Consider using faster JSON libraries like `orjson` for better performance
4. **Database Cleanup**: Implement periodic cleanup of old FSM records

---

- [Quick Setup Guide](./quick_setup.md)
