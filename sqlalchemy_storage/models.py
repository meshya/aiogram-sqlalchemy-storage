from typing import Type

from sqlalchemy.orm import declarative_base
from sqlalchemy import String, Column

class FSMData:
    id = Column(String, primary_key=True)
    state = Column(String, nullable=True)
    data = Column(String, nullable=True)


def declare_models(base, tablename)->Type[FSMData]:
    class _FSMData(FSMData, base):
        __tablename__ = tablename
    return _FSMData
