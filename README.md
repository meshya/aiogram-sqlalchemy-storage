# SQLAlchemyStorage for aiogram FSM

## Overview
`SQLAlchemyStorage` is a storage module for `aiogram`'s finite state machine (FSM) using SQLAlchemy as the backend. It provides an efficient and flexible way to persist FSM state and data using an asynchronous database session.

## Features
- Asynchronous support with `AsyncSession`
- Customizable table name for storing FSM data
- Pluggable key-building strategy
- JSON serialization customization

## Installation
Ensure you have `aiogram` and `SQLAlchemy` installed in your environment:

```sh
pip install aiogram sqlalchemy
```

## Usage

### Import and Setup
```python
# db.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy_storage import SQLAlchemyStorage

# Create an async engine
engine = create_async_engine("sqlite+aiosqlite:///database.db")
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Initialize the storage
storage = SQLAlchemyStorage(session=SessionLocal)
```

### Parameters
The `SQLAlchemyStorage` constructor accepts the following parameters:

```python
def __init__(
    self,
    session: sessionmaker[AsyncSession],  # Async database session
    base=None,                            # Optional declarative base
    table_name: Optional[str] = 'aiogram_fsm_data',  # Custom table name
    key_builder: Optional[KeyBuilder] = None,       # Custom key-building strategy
    json_dumps: _JsonDumps = json.dumps,            # Custom JSON serialization
    json_loads: _JsonLoads = json.loads,            # Custom JSON deserialization
):
```

### Example Integration with aiogram
```python
# bot.py
from db import storage
from aiogram import Bot, Dispatcher

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(storage=storage)
```

## Database Schema
By default, `SQLAlchemyStorage` creates a table named `aiogram_fsm_data` to store FSM-related data. You can customize this by passing a different table name during initialization.

## Custom Key Builder
If you need a custom key-building strategy, pass an instance of `KeyBuilder` to the `key_builder` parameter.

## Custom JSON Serialization
You can override the default JSON serialization and deserialization methods using the `json_dumps` and `json_loads` parameters.

## License
MIT License

## Contributions
Contributions are welcome! Feel free to submit issues or pull requests on the repository.

---
This module provides an efficient way to manage FSM data storage using SQLAlchemy with aiogram, ensuring scalability and flexibility in bot development.

