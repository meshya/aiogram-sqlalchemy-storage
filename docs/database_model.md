# Database Model Documentation

This document contains the database schema for different versions of `aiogram-sqlalchemy-storage`.

## Table of Contents
- [Current Version (0.2.x)](#current-version-02x)
- [Version History](#version-history)
- [Migration Notes](#migration-notes)

## Current Version (0.2.x)

### FSM Storage Table

The current version creates a single table to store FSM state and data.

#### Table Structure

```sql
CREATE TABLE aiogram_fsm_data (
    id VARCHAR PRIMARY KEY,
    state VARCHAR NULL,
    data VARCHAR NULL
);
```

#### SQLAlchemy Model Definition

```python
from sqlalchemy import String, Column

class FSMData:
    id = Column(String, primary_key=True)
    state = Column(String, nullable=True)
    data = Column(String, nullable=True)
```

#### Field Descriptions

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | VARCHAR | No | Primary key built from bot_id, chat_id, and user_id using the key builder |
| `state` | VARCHAR | Yes | Current FSM state as string (e.g., "MyState:waiting_for_input") |
| `data` | VARCHAR | Yes | JSON-serialized user data dictionary |

#### Key Building Strategy

The primary key is built using the following format (with DefaultKeyBuilder):
```
{bot_id}:{chat_id}:{user_id}
```

For example: `123456789:987654321:555444333`

#### Data Storage Format

- **State**: Stored as plain string representing the current FSM state
- **Data**: Stored as JSON string containing user session data

Example data content:
```json
{
    "user_name": "John",
    "step": 2,
    "selected_items": ["item1", "item2"]
}
```

### Table Creation

The table is dynamically created using SQLAlchemy's declarative approach:

```python
def declare_models(base, tablename) -> Type[FSMData]:
    new_cls = type('StorageModel', (base,), 
                    {
                        '__tablename__': tablename,
                        'id': Column(String, primary_key=True),
                        'state': Column(String, nullable=True),
                        'data': Column(String, nullable=True)
                    })
    return new_cls
```

### Indexes

- **Primary Key Index**: Automatically created on `id` column
- **No additional indexes**: For performance optimization, consider adding indexes based on your usage patterns

### Storage Behavior

#### Record Lifecycle

1. **Creation**: Record is created when either state or data is first set
2. **Updates**: Record is updated when state or data changes
3. **Deletion**: Record is deleted when both state and data become empty/null

#### Null Handling

- If `state` is None and `data` is empty, the entire record is deleted
- Individual fields can be null without affecting the other field
- Empty data dictionary is stored as empty string `""`

## Version History

### Version 0.2.x (Current)
- **Release Date**: August 28, 2025
- **Database Schema**: Single table with id, state, data columns
- **Features**: 
  - Improved ORM integration
  - Better metadata handling
  - Bug fixes from 0.1.x

### Version 0.1.x (Deprecated)
- **Release Date**: January 30, 2025
- **Status**: Does not work, deprecated
- **Issues**: Multiple compatibility and functionality problems

## Migration Notes

### From 0.1.x to 0.2.x

Since version 0.1.x was non-functional, no migration path is provided. Users should:

1. Remove any 0.1.x installation
2. Install 0.2.x fresh
3. Initialize database schema from scratch

### Future Migrations

For future versions, migration scripts will be provided.

### Customization Options

#### Custom Table Names

```python
storage = SQLAlchemyStorage(
    sessionmaker=SessionLocal,
    metadata=Base.metadata,
    table_name="custom_fsm_storage"  # Custom table name
)
```

#### Custom Key Builders

```python
class CustomKeyBuilder(KeyBuilder):
    def build(self, key: StorageKey) -> str:
        return f"bot{key.bot_id}_chat{key.chat_id}_user{key.user_id}"

storage = SQLAlchemyStorage(
    sessionmaker=SessionLocal,
    metadata=Base.metadata,
    key_builder=CustomKeyBuilder()
)
```

## Performance Considerations

### Current Schema Performance

- **Primary Key Lookups**: O(1) performance due to primary key index
- **Full Table Scans**: Not optimized - avoid queries without WHERE clause on id
- **Storage Overhead**: Minimal - only stores active FSM sessions

### Recommended Optimizations

For high-traffic applications, consider:

1. **Connection Pooling**:
```python
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```


This model documentation will be updated with each major version release to track schema evolution.
