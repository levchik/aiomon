"""Base metric classes for the aiomon library."""

import abc
import time
from typing import TYPE_CHECKING

from aiomon.base import MonitorStorage
from aiomon.types import MetricType

if TYPE_CHECKING:
    from aiomon.impl.storages.memory import MemoryMonitorStorage


class BaseMetric(metaclass=abc.ABCMeta):
    """
    Base class for all metric types.

    Provides common metadata fields for all metrics including name, tags,
    host, key, unit, rate, ttl, and timestamp.
    """

    type_: MetricType
    name: str
    tags: list[str] | None
    host: str | None
    key: str | None
    unit: str | None
    rate: float | None
    ttl: int | None
    timestamp: float | None
    _bound_storage: MonitorStorage | None

    def __init__(
        self,
        name: str,
        storage: "MemoryMonitorStorage | None" = None,
        tags: list[str] | None = None,
        host: str | None = None,
        key: str | None = None,
        unit: str | None = None,
        rate: float | None = None,
        ttl: int | None = None,
        timestamp: float | None = None,
    ) -> None:
        self.name = name
        self.tags = tags
        self.host = host
        self.key = key
        self.unit = unit
        self.rate = rate
        self.ttl = ttl
        self.timestamp = timestamp if timestamp is not None else time.time()
        self._bound_storage = storage

    def _bind_storage(self, storage: MonitorStorage) -> None:
        """Bind a storage reference to this metric."""
        self._bound_storage = storage


class InfoMetric(BaseMetric):
    """
    Info metric for storing arbitrary dictionary data.

    Info metrics are used to store static or slowly changing information
    such as configuration data, version information, or health status.
    """

    type_: MetricType = MetricType.INFO

    def __init__(
        self,
        name: str,
        storage: "MemoryMonitorStorage",
        tags: list[str] | None = None,
        host: str | None = None,
        key: str | None = None,
        unit: str | None = None,
        rate: float | None = None,
        ttl: int | None = None,
        timestamp: float | None = None,
    ) -> None:
        super().__init__(
            name=name,
            storage=storage,
            tags=tags,
            host=host,
            key=key,
            unit=unit,
            rate=rate,
            ttl=ttl,
            timestamp=timestamp,
        )
        storage.store_metadata_sync(self)

    async def set_(self, storage: MonitorStorage, value: dict) -> None:
        """
        Set the info value.

        Args:
            storage: The storage backend to update.
            value: The dictionary value to store.
        """
        await storage.update(name=self.name, value=value)
