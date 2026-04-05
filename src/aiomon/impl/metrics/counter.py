"""Counter metric implementation."""

from typing import cast

from aiomon.impl.metrics.base import BaseMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType


class CounterMetric(BaseMetric):
    """
    Counter metric that only increases or resets to zero.

    Counters are cumulative metrics that represent a single monotonically
    increasing counter value. They are typically used for counting events
    like requests served, tasks completed, or errors occurred.
    """

    type_: MetricType = MetricType.COUNTER

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

    async def inc(
        self,
        storage: MemoryMonitorStorage | None = None,
        by: int = 1,
    ) -> None:
        """Increment the counter.

        Args:
            storage: Storage backend. Uses bound storage if not provided.
            by: Value to increment by (default: 1).
        """
        store = self._get_storage(storage)
        await store.modify(
            name=self.name,
            modifier=lambda v: (v or 0) + by,
        )

    async def inc_by(
        self,
        storage: MemoryMonitorStorage | None = None,
        value: int = 1,
    ) -> None:
        """Increment counter by specific value.

        Args:
            storage: Storage backend. Uses bound storage if not provided.
            value: Value to increment by.
        """
        await self.inc(storage, by=value)

    async def reset(
        self,
        storage: MemoryMonitorStorage | None = None,
    ) -> None:
        """Reset counter to zero.

        Args:
            storage: Storage backend. Uses bound storage if not provided.
        """
        store = self._get_storage(storage)
        await store.update(name=self.name, value=0)
