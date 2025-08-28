from typing import Type

from sqlalchemy import String, Column

class FSMData:
    id = Column(String, primary_key=True)
    state = Column(String, nullable=True)
    data = Column(String, nullable=True)


def declare_models(base, tablename)->Type[FSMData]:
    new_cls = type('StorageModel', (base,), 
                    {
                        '__tablename__': tablename,
                        'id': Column(String, primary_key=True),
                        'state': Column(String, nullable=True),
                        'data': Column(String, nullable=True)
                    })
    return new_cls
