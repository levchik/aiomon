import sys
from typing import (
    Generic,
    Optional,
    Type,
    TypeVar,
)

if sys.version_info >= (3, 8):  # pragma: py-lt-38
    from typing import Protocol, runtime_checkable
else:  # pragma: py-gte-38
    from typing_extensions import Protocol, runtime_checkable

from aiomon._sync import RWMutex

MonitorKey = TypeVar("MonitorKey", contravariant=True)
MonitorValue = TypeVar("MonitorValue")


@runtime_checkable
class MonitorData(Protocol[MonitorKey, MonitorValue]):
    async def get_value(self, key: MonitorKey) -> Optional[MonitorValue]:
        ...

    async def set_value(self, key: MonitorKey, value: MonitorValue) -> None:
        ...

    async def delete_value(self, key: MonitorKey) -> None:
        ...

    # TODO: maybe incr and decr, count, other prom metrics stuff?


MonitorDataT = TypeVar("MonitorDataT", bound=MonitorData, contravariant=True)


@runtime_checkable
class MonitorOutput(Protocol[MonitorDataT]):
    async def write(self, data: MonitorDataT) -> None:
        ...


class Monitor(Generic[MonitorKey, MonitorValue]):
    def __init__(
        self,
        name: str,
        cls_data: Type[MonitorData],
        cls_output: Type[MonitorOutput],
    ) -> None:
        self.name = name
        self.__output = cls_output()
        self.__data = cls_data()
        self.__mutex = RWMutex(self.__data)

    async def get_value(self, key: MonitorKey) -> Optional[MonitorValue]:
        async with self.__mutex.reader_lock() as data:
            return await data.get_value(key)

    async def set_value(self, key: MonitorKey, value: MonitorValue) -> None:
        async with self.__mutex.writer_lock() as data:
            await data.set_value(key=key, value=value)
            await self.__output.write(data=data)

    async def delete_value(self, key: MonitorKey) -> None:
        async with self.__mutex.writer_lock() as data:
            await data.delete_value(key=key)
            await self.__output.write(data=data)
