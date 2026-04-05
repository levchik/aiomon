"""Enum metric for tracking state from a set of possible values."""

from aiomon.base import MonitorStorage
from aiomon.impl.metrics.base import BaseMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType


class EnumMetric(BaseMetric):
    """
    Enum metric for tracking state from a set of possible values.

    Enum metrics represent a state that can be one of a predefined set
    of values. They are useful for tracking things like service status,
    application state, or any categorical value with a fixed set of options.
    """

    type_: MetricType = MetricType.ENUM

    def __init__(
        self,
        name: str,
        states: list[str],
        storage: MemoryMonitorStorage,
        default: str | None = None,
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
            tags=tags,
            host=host,
            key=key,
            unit=unit,
            rate=rate,
            ttl=ttl,
            timestamp=timestamp,
        )
        self._states = states
        self._default = default if default is not None else states[0]
        storage.store_metadata_sync(self)

    async def set(self, storage: MonitorStorage, state: str) -> None:
        """
        Set the enum state.

        Args:
            storage: The storage backend to update.
            state: The state to set. Must be one of the allowed states.

        Raises:
            ValueError: If the state is not in the allowed states list.
        """
        if state not in self._states:
            msg = (
                f"Invalid state '{state}'. "
                f"Allowed states are: {', '.join(self._states)}"
            )
            raise ValueError(msg)
        await storage.update(name=self.name, value=state)

    async def reset(self, storage: MonitorStorage) -> None:
        """
        Reset to the default state.

        Args:
            storage: The storage backend to update.
        """
        await storage.update(name=self.name, value=self._default)
