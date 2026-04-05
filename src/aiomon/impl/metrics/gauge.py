"""Gauge metric implementation."""

from typing import cast

from aiomon.impl.metrics.base import BaseMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType

Number = int | float


class GaugeMetric(BaseMetric):
    """
    Gauge metric that can increase or decrease.

    Gauges are metrics that represent a single numerical value that can
    arbitrarily go up and down. They are typically used for measured values
    like temperature, current memory usage, or active connections.
    """

    type_: MetricType = MetricType.GAUGE

    def __init__(
        self,
        name: str,
        storage: MemoryMonitorStorage,
        tags: list[str] | None = None,
        host: str | None = None,
        key: str | None = None,
        unit: str | None = None,
        rate: float | None = None,
        ttl: int | None = None,
        timestamp: float | None = None,
        value: Number | None = 0,
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
        self._initial_value: Number = value if value is not None else 0
        # Store metadata in storage for monitors to use
        storage.store_metadata_sync(self)

    def _get_storage(
        self,
        storage: MemoryMonitorStorage | None = None,
    ) -> MemoryMonitorStorage:
        """Get storage from argument or bound storage."""
        if storage is not None:
            return storage
        if self._bound_storage is not None:
            return cast(MemoryMonitorStorage, self._bound_storage)
        msg = "No storage provided"
        raise RuntimeError(msg)

    async def set(
        self,
        storage_or_value: MemoryMonitorStorage | Number | None = None,
        value: Number | None = None,
    ) -> None:
        """Set gauge to value.

        Usage:
            await gauge.set(25.0)  # Uses bound storage
            await gauge.set(storage, 25.0)

        Args:
            storage_or_value: Value or storage.
            value: Value to set.
        """
        if isinstance(storage_or_value, MemoryMonitorStorage):
            if value is None:
                msg = "value is required when storage is provided"
                raise ValueError(msg)
            store = storage_or_value
            final_value = value
        else:
            if storage_or_value is None:
                msg = "value is required"
                raise ValueError(msg)
            store = self._get_storage(None)
            final_value = storage_or_value

        await store.update(name=self.name, value=final_value)

    async def inc(
        self,
        storage: MemoryMonitorStorage | None = None,
        by: Number = 1,
    ) -> None:
        """Increment gauge.

        Args:
            storage: Storage backend. Uses bound storage if not provided.
            by: Value to increment by (default: 1).
        """
        store = self._get_storage(storage)
        await store.modify(
            name=self.name,
            modifier=lambda v: (v or self._initial_value) + by,
        )

    async def dec(
        self,
        storage: MemoryMonitorStorage | None = None,
        by: Number = 1,
    ) -> None:
        """Decrement gauge.

        Args:
            storage: Storage backend. Uses bound storage if not provided.
            by: Value to decrement by (default: 1).
        """
        store = self._get_storage(storage)
        await store.modify(
            name=self.name,
            modifier=lambda v: (v or self._initial_value) - by,
        )

    async def add(
        self,
        storage: MemoryMonitorStorage | None = None,
        value: Number = 1,
    ) -> None:
        """Alias for inc - add value.

        Args:
            storage: Storage backend. Uses bound storage if not provided.
            value: Value to add.
        """
        await self.inc(storage, by=value)

    async def sub(
        self,
        storage: MemoryMonitorStorage | None = None,
        value: Number = 1,
    ) -> None:
        """Alias for dec - subtract value.

        Args:
            storage: Storage backend. Uses bound storage if not provided.
            value: Value to subtract.
        """
        await self.dec(storage, by=value)
