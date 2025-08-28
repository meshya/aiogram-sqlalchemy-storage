# Quick Setup

This guide will help you quickly set up `aiogram-sqlalchemy-storage` for your project.

## Installation

```sh
pip install aiogram-sqlalchemy-storage
```

## Basic Usage

1. **Create SQLAlchemy engine and session:**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy_storage import SQLAlchemyStorage

engine = create_async_engine("sqlite+aiosqlite:///database.db")
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
```

2. **Initialize storage for aiogram FSM:**

```python
storage = SQLAlchemyStorage(sessionmaker=SessionLocal, metadata=Base.metadata)
```

3. **Integrate with aiogram FSM:**

```python
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(storage=storage)
```


4. **Create tables in the database:**

Before using the storage, make sure to create the required tables:

```python
async def init_db():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

# Run this once at startup
import asyncio
asyncio.run(init_db())
```

Now your FSM state and data will be stored in the database using SQLAlchemy.

---

- [Storage Documentation](./storage.md)
