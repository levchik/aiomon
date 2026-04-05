"""Summary metric implementation."""

from aiomon.base import MonitorStorage
from aiomon.impl.metrics.base import BaseMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType

DEFAULT_QUANTILES: tuple[float, ...] = (0.5, 0.9, 0.99)


class SummaryMetric(BaseMetric):
    """
    Summary metric for calculating quantiles over observed values.

    Summaries track the distribution of values by calculating exact quantiles
    from observed values. They are useful for latency distributions, response
    time percentiles, or any value where you need to know the distribution.

    Unlike Histogram which uses pre-defined buckets, Summary calculates
    exact quantiles from observed values.
    """

    type_: MetricType = MetricType.SUMMARY

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
        quantiles: tuple[float, ...] | None = None,
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
        self._quantiles: tuple[float, ...] = (
            quantiles if quantiles is not None else DEFAULT_QUANTILES
        )
        storage.store_metadata_sync(self)

    async def observe(self, storage: MonitorStorage, value: float) -> None:
        """
        Record an observed value.

        Args:
            storage: The storage backend to update.
            value: The value to observe.
        """
        data = await self._get_or_init_data(storage)
        data["values"].append(value)
        data["sum"] += value
        data["count"] += 1
        data["quantiles"] = self._calculate_quantiles(data["values"])
        await storage.update(name=self.name, value=data)

    async def _get_or_init_data(self, storage: MonitorStorage) -> dict:
        """
        Get existing summary data or initialize new data structure.

        Args:
            storage: The storage backend to read from.

        Returns:
            The summary data dictionary.
        """
        if hasattr(storage, "_MemoryMonitorStorage__data"):
            data: dict = storage._MemoryMonitorStorage__data  # type: ignore[attr-defined]
            if self.name in data:
                stored = data[self.name]
                # Extract value from (value, expire_at) tuple
                return stored[0] if isinstance(stored, tuple) else stored  # type: ignore[no-any-return]

        return {
            "values": [],
            "sum": 0.0,
            "count": 0,
            "quantiles": {},
        }

    def _calculate_quantiles(self, values: list[float]) -> dict[float, float]:
        """
        Calculate quantile values from observed values.

        For quantile q, find value at position q * len(values) in sorted list.
        Quantiles are returned as a dict with sorted keys.

        Args:
            values: The list of observed values.

        Returns:
            A dictionary mapping quantile values to their calculated values.
        """
        if not values or not self._quantiles:
            return {}

        sorted_values = sorted(values)
        n = len(sorted_values)
        quantile_values: dict[float, float] = {}

        for q in sorted(self._quantiles):
            # Position in sorted list (0-indexed)
            # Using int(q * n) - 1 to match expected quantile behavior
            pos = int(q * n) - 1
            # Clamp to valid index range
            pos = max(0, min(pos, n - 1))
            quantile_values[q] = sorted_values[pos]

        return quantile_values
