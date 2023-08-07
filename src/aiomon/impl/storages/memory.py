from aiomon.base import MetricValue_contra, MonitorStorageData
from aiomon.impl.storages._sync import RWMutex


class MemoryMonitorStorage:
    def __init__(self) -> None:
        self.__data: MonitorStorageData = {}
        self.__mutex = RWMutex(self.__data)

    async def update(self, name: str, value: MetricValue_contra) -> None:
        async with self.__mutex.writer_lock() as data:
            data[name] = value

    async def get_data(self) -> MonitorStorageData:
        async with self.__mutex.reader_lock() as data:
            return data
