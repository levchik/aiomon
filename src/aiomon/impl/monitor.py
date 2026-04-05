from typing import Generic, TypeVar

from aiomon.base import (
    ExportableMonitorStorage,
    Metric,
    MonitorFormatter,
    MonitorOutput,
    MonitorOutputData,
    MonitorOutputItem,
)

T_co = TypeVar("T_co", covariant=True)


class Monitor(Generic[T_co]):
    """
    Monitor with exactly one formatter and optional output target.

    Generic over the formatter's output type T_co.

    Monitor reads metric metadata from storage (not from its own registry),
    enabling full decoupling between metrics and monitors.
    """

    def __init__(
        self,
        name: str,
        storage: ExportableMonitorStorage,
        formatter: MonitorFormatter[T_co],
        output: MonitorOutput[T_co] | None = None,
    ) -> None:
        self.name = name
        self._storage = storage
        self._formatter = formatter
        self._output = output

    async def add_metric(self, metric: Metric) -> None:
        """Explicitly store metric metadata.

        Note: Metrics automatically store themselves on creation.
        This is for backward compat and explicit registration.
        """
        await self._storage.store_metadata(metric)

    async def format_(self) -> T_co:
        """Pull formatted data.

        Reads all metrics from storage with metadata,
        formats using the configured formatter.

        Returns type T_co from formatter.
        """
        # Get all metric values from storage
        storage_data = await self._storage.get_data()

        # Build output data with metadata from storage
        output_data: MonitorOutputData = []
        for name, value in storage_data.items():
            # Get metric metadata from storage
            metric = await self._storage.get_metadata(name)
            if metric is not None:
                output_data.append(
                    MonitorOutputItem(
                        metric=metric,
                        value=value,
                        timestamp=metric.timestamp,
                        ttl=metric.ttl,
                        unit=metric.unit,
                        rate=metric.rate,
                        host=metric.host,
                        key=metric.key,
                    )
                )

        return self._formatter.format_(output_data)

    async def output(self) -> None:
        """Push to output target."""
        if self._output is None:
            msg = "No output configured"
            raise ValueError(msg)
        await self._output.write(await self.format_())
