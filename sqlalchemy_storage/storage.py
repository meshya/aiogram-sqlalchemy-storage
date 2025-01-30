from typing import Any, Optional, Dict, cast, Callable

from aiogram.fsm.storage.base import (
    BaseStorage, 
    DefaultKeyBuilder, 
    KeyBuilder, 
    StorageKey,
    StateType,
)
from aiogram.fsm.state import State
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Select, Update, Delete
from sqlalchemy.ext.asyncio import AsyncSession
import json

from .models import declare_models

_JsonLoads = Callable[..., Any]
_JsonDumps = Callable[..., str]


class SQLAlchemyStorage(BaseStorage):
    def __init__(
            self,
            session: sessionmaker[AsyncSession],
            base: Any,
            table_name: Optional[str] = 'aiogram_fsm_data',
            key_builder: Optional[KeyBuilder] = None,
            json_dumps: _JsonDumps = json.dumps,
            json_loads: _JsonLoads = json.loads,
            ):
        if not base:
            base = declarative_base()
        if not key_builder:
            key_builder = DefaultKeyBuilder()
        self._model = declare_models(base, table_name)
        self._async_session_maker = session
        self._key_builder = key_builder
        self._json_loads = json_loads
        self._json_dumps = json_dumps

    async def get_state(self, key:StorageKey) -> Optional[str]:
        pk = self._key_builder.build(key)
        async with self._async_session_maker() as session:
            db_result = await session.execute(
                Select(self._model.state).where(
                    self._model.id == pk
                )
            )
            result = db_result.scalar_one_or_none()
        return result

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        pk = self._key_builder.build(key)
        dump_state = state.state if isinstance(state, State) else state
        async with self._async_session_maker() as session:
            await session.execute(
                Update(self._model).where(
                    self._model.id == pk
                ).values(
                    state=dump_state
                )
            )
            if state is None:
                data = await self.get_data()
                if not data:
                    await session.execute(
                        Delete(self._model).where(
                            self._model.id == pk
                        )
                    )

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        pk = self._key_builder.build(key)
        async with self._async_session_maker() as session:
            db_result = await session.execute(
                Select(self._model.data).where(
                    self._model.id == pk
                )
            )
            result = db_result.scalar_one_or_none()
        if result:
            result = self._json_loads(result)
        else:
            result = {}
        return cast(Dict[str, Any], result)
    
    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        pk = self._key_builder.build(key)
        if data:
            data = self._json_dumps(data)
        else:
            data = ""
        async with self._async_session_maker() as session:
            await session.execute(
                Update(self._model).where(
                    self._model.id == pk
                ).values(
                    data = data
                )
            )
            if not data:
                if not await self.get_state():
                    await session.execute(
                        Delete(self._model).where(
                            self._model.id == pk
                        )
                    )
