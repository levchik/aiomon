import time
from collections.abc import Callable
from typing import Generic

from aiomon.base import Metric, MetricValue_contra, MonitorStorageData
from aiomon.impl.metrics.base import BaseMetric
from aiomon.impl.storages._sync import RWMutex


class MemoryMonitorStorage(Generic[MetricValue_contra]):
    def __init__(self) -> None:
        self.__data: dict[str, tuple[MetricValue_contra, float | None]] = {}
        self.__metadata: dict[str, BaseMetric] = {}
        self.__mutex = RWMutex(self.__data)
        self.__metadata_mutex = RWMutex(self.__metadata)

    async def update(
        self,
        name: str,
        value: MetricValue_contra,
        ttl: float | None = None,
    ) -> None:
        async with self.__mutex.writer_lock() as data:
            expire_at = time.time() + ttl if ttl else None
            data[name] = (value, expire_at)

    async def modify(
        self,
        name: str,
        modifier: Callable[[MetricValue_contra | None], MetricValue_contra],
        ttl: float | None = None,
    ) -> MetricValue_contra:
        """Atomically read-modify-write a value."""
        async with self.__mutex.writer_lock() as data:
            current = data.get(name)
            if current is not None:
                current_value = current[0]  # Extract from (value, expire_at)
            else:
                current_value = None
            new_value = modifier(current_value)
            expire_at = time.time() + ttl if ttl else None
            data[name] = (new_value, expire_at)
            return new_value

    async def store_metadata(self, metric: Metric) -> None:
        """Store metric metadata (called once when metric is created)."""
        async with self.__metadata_mutex.writer_lock() as metadata:
            if isinstance(metric, BaseMetric):
                metadata[metric.name] = metric

    def store_metadata_sync(self, metric: BaseMetric) -> None:
        """Store metric metadata synchronously (for use in constructors)."""
        self.__metadata[metric.name] = metric

    async def get_metadata(self, name: str) -> Metric | None:
        """Get metric metadata by name."""
        async with self.__metadata_mutex.reader_lock() as metadata:
            return metadata.get(name)

    async def get_data(self) -> MonitorStorageData:
        async with self.__mutex.reader_lock() as data:
            now = time.time()
            result = {}
            for key, (value, expire_at) in data.items():
                if expire_at is None or expire_at > now:
                    result[key] = value
            return result

    async def cleanup_expired(self) -> None:
        """Remove all expired entries."""
        async with self.__mutex.writer_lock() as data:
            now = time.time()
            expired = [
                k
                for k, (_, expire_at) in data.items()
                if expire_at is not None and expire_at <= now
            ]
            for key in expired:
                del data[key]
