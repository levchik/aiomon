"""Histogram metric implementation."""

from aiomon.base import MonitorStorage
from aiomon.impl.metrics.base import BaseMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType


class HistogramMetric(BaseMetric):
    """
    Histogram metric for observing value distributions.

    Histograms track the distribution of values by counting observations
    in configurable buckets. They provide cumulative counts per bucket,
    sum of all values, and total count of observations.
    """

    type_: MetricType = MetricType.HISTOGRAM

    DEFAULT_BUCKETS: tuple[float, ...] = (
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
        float("inf"),
    )

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
        buckets: tuple[float, ...] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            tags=tags,
            host=host,
            key=key,
            unit=unit,
            rate=rate,
            ttl=ttl,
            timestamp=timestamp,
        )
        self._buckets = (
            buckets if buckets is not None else self.DEFAULT_BUCKETS
        )
        storage.store_metadata_sync(self)

    async def observe(self, storage: MonitorStorage, value: float) -> None:
        """
        Record an observation in the histogram.

        Args:
            storage: The storage backend to update.
            value: The value to observe.
        """
        data = await self._get_or_init_data(storage)

        # Update sum and count
        data["sum"] += value
        data["count"] += 1

        # Update cumulative bucket counts
        for bucket in self._buckets:
            if value <= bucket:
                data["buckets"][bucket] += 1

        await storage.update(name=self.name, value=data)

    async def _get_or_init_data(self, storage: MonitorStorage) -> dict:
        """
        Get existing histogram data or initialize new data structure.

        Args:
            storage: The storage backend to read from.

        Returns:
            The histogram data dictionary.
        """
        # Access internal data for reading current value
        if hasattr(storage, "_MemoryMonitorStorage__data"):
            data: dict = storage._MemoryMonitorStorage__data  # type: ignore[attr-defined]
            stored = data.get(self.name)
            if stored is not None:
                # Extract value from (value, expire_at) tuple
                return stored[0] if isinstance(stored, tuple) else stored  # type: ignore[no-any-return]

        # Initialize new data structure
        return {
            "buckets": dict.fromkeys(self._buckets, 0),
            "sum": 0.0,
            "count": 0,
        }
