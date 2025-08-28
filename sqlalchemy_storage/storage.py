from typing import Any, Optional, Dict, cast, Callable, Union
import warnings

from aiogram.fsm.storage.base import (
    BaseStorage, 
    DefaultKeyBuilder, 
    KeyBuilder, 
    StorageKey,
    StateType,
)
from aiogram.fsm.state import State
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Select, Update, Delete, MetaData
from sqlalchemy.ext.asyncio import AsyncSession
import json

from .models import declare_models

_JsonLoads = Callable[..., Any]
_JsonDumps = Callable[..., Union[str, bytes]]


class SQLAlchemyStorage(BaseStorage):
    def __init__(
            self,
            sessionmaker: sessionmaker[AsyncSession],
            metadata: MetaData = MetaData(),
            table_name: Optional[str] = 'aiogram_fsm_data',
            key_builder: Optional[KeyBuilder] = None,
            json_dumps: _JsonDumps = json.dumps,
            json_loads: _JsonLoads = json.loads,
            ):
        if not isinstance(metadata, MetaData):
            if hasattr(metadata, 'metadata'):
                warnings.warn(
                    "Passing Base is deprecated. \n"
                    "Please pass an instance of MetaData instead. \n"
                    "For example: SQLAlchemyStorage(metadata=Base.metadata) \n",
                    UserWarning,
                )
                metadata = metadata.metadata
            if not isinstance(metadata, MetaData):
                raise TypeError("Expected metadata to be an instance of MetaData")
        base = declarative_base(metadata=metadata)
        if not key_builder:
            key_builder = DefaultKeyBuilder()
        self.metadata = metadata
        self._base = base
        self._model = declare_models(base, table_name)
        self._async_session_maker = sessionmaker
        self._key_builder = key_builder
        self._passed_json_loads = json_loads
        self._passed_json_dumps = json_dumps

    def _json_dumps(self, json):
        res = self._passed_json_dumps(json)
        if isinstance(res, bytes):
            res = res.decode()
        return res

    def _json_loads(self, json: Union[str, bytes]) -> Any:
        try:
            return self._passed_json_loads(json)
        except (TypeError, ValueError) as e:
            if isinstance(json, str):
                json = json.encode()
                return self._passed_json_loads(json)
            else:
                raise e


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
            if await self._exists(session, pk):
                await session.execute(
                    Update(self._model).where(
                        self._model.id == pk
                    ).values(
                        state=dump_state
                    )
                )
            else:
                if dump_state:
                    new_row = self._model(id=pk, state=dump_state, data=None)
                    session.add(new_row)
            if dump_state is None:
                data = await self.get_data(key)
                if not data:
                    await session.execute(
                        Delete(self._model).where(
                            self._model.id == pk
                        )
                    )
            await session.commit()

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
            if await self._exists(session, pk):
                await session.execute(
                    Update(self._model).where(
                        self._model.id == pk
                    ).values(
                        data = data
                    )
                )
            else:
                if data:
                    new_row = self._model(id=pk, data=data, state=None)
                    session.add(new_row)
            if not data:
                if not await self.get_state(key):
                    await session.execute(
                        Delete(self._model).where(
                            self._model.id == pk
                        )
                    )
            await session.commit()
    async def _exists(self, session:AsyncSession, pk: str) -> bool:
        db_result = await session.execute(
            Select(self._model.id).where(
                self._model.id == pk
            )
        )
        result = db_result.scalar_one_or_none()
        return result is not None
    async def close(self) -> None:
        pass
