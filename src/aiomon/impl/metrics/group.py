"""MetricGroup base class for declarative metric definitions."""

from typing import Any

from aiomon.base import MonitorStorage
from aiomon.impl.metrics.base import BaseMetric


class MetricGroup:
    """
    Base class for defining metrics as class attributes.

    Subclasses define metrics as class attributes for type-safe access.
    Each metric stores its own metadata in storage via __init__.

    Example:
        class AppMetrics(MetricGroup, storage=storage):
            requests_total = CounterMetric("requests_total", storage=storage)
            temperature = GaugeMetric("temperature", storage=storage)

        # Usage - fully type-safe:
        await AppMetrics.requests_total.inc()
        await AppMetrics.temperature.set(25.0)
    """

    _storage: MonitorStorage

    def __init_subclass__(
        cls,
        storage: MonitorStorage,
        **kwargs: Any,
    ) -> None:
        """Store storage on class and bind to metrics."""
        super().__init_subclass__(**kwargs)
        cls._storage = storage

        # Bind storage to all BaseMetric instances defined as class attributes
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, BaseMetric):
                attr._bind_storage(storage)
