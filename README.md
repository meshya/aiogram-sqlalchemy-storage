# SQLAlchemyStorage for aiogram FSM

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/meshya/aiogram-sqlalchemy-storage/publish.yaml)

![PyPI - License](https://img.shields.io/pypi/l/aiogram-sqlalchemy-storage)

![PyPI - Version](https://img.shields.io/pypi/v/aiogram-sqlalchemy-storage)

![PyPI - Wheel](https://img.shields.io/pypi/wheel/aiogram-sqlalchemy-storage)

## Overview
`SQLAlchemyStorage` is a storage backend for `aiogram`'s finite state machine (FSM) using SQLAlchemy. It provides an efficient and flexible way to persist FSM state and data using an asynchronous database session.

## Installation
Use `pip` to install in your environment:

```sh
pip install aiogram-sqlalchemy-storage
```

## Quick Start

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy_storage import SQLAlchemyStorage
from aiogram import Bot, Dispatcher

# Setup database
engine = create_async_engine("sqlite+aiosqlite:///database.db")
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Initialize storage
storage = SQLAlchemyStorage(sessionmaker=SessionLocal, metadata=Base.metadata)

# Setup bot
bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(storage=storage)
```
## Features
- Asynchronous support with `AsyncSession`
- Customizable table name for storing FSM data
- Pluggable key-building strategy
- JSON serialization customization

## Documentation

For detailed documentation, configuration options, and advanced usage, see:

- [Quick Setup Guide](docs/quick_setup.md)
- [Storage Documentation](docs/storage.md)
- [Manage DB Migrations](docs/db_migrations.md)
- [Database model](docs/database_model.md)

## Change Log
- [Change Log](./CHANGELOG.md)

## License
MIT License

## Contributions
Contributions are welcome! Feel free to submit issues or pull requests on the repository.

