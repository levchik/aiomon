from typing import (
    Any,
    Callable,
    Optional,
    Union,
    cast,
)

from aiomon.base import (
    ExportableMonitorStorage,
    FormattedMetrics,
    Metric,
    MonitorFormatter,
    MonitorOutput,
    MonitorOutputData,
    MonitorOutputItem,
    MonitorStorage,
    MonitorStorageData,
)
from aiomon.impl.types import UniqueMetricsDict


class MonitorMetric:
    """Basically it is Delegator pattern."""

    def __init__(self, metric: Metric, storage: MonitorStorage) -> None:
        self._metric = metric
        self._storage = storage

    def __getattr__(self, name: str) -> Union[Any, Callable]:
        attr = getattr(self._metric, name)

        if not callable(attr):
            # Restrict access to the Metric's attributes, we only communicate
            # with the metric through methods of the Metric
            msg = f"Attribute {name} is not callable"
            raise AttributeError(msg)

        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await attr(*args, storage=self._storage, **kwargs)

        return wrapper


class Monitor:
    def __init__(
        self,
        name: str,
        output: Optional[MonitorOutput],
        formatter: Optional[MonitorFormatter],
        storage: MonitorStorage | ExportableMonitorStorage,
    ) -> None:
        # Validate arguments
        if output and not formatter:
            msg = "formatter must be specified if output is specified"
            raise ValueError(msg)

        # Set attributes
        self.name = name
        self.__output = output
        self.__formatter = formatter
        self.__storage = storage
        self.__metrics = UniqueMetricsDict()
        self.__is_exportable_storage = isinstance(
            self.__storage, ExportableMonitorStorage
        )

    def add_metric(self, metric: Metric) -> None:
        self.__metrics[metric.name] = metric

    def metric(self, name: str) -> MonitorMetric:
        return MonitorMetric(self.__metrics[name], self.__storage)

    def __output_data_from_storage_data(
        self, storage_data: MonitorStorageData
    ) -> MonitorOutputData:
        return [
            MonitorOutputItem(
                metric=self.__metrics[k],
                value=v,
            )
            for k, v in storage_data.items()
        ]

    async def format_(self) -> FormattedMetrics:
        if not self.__formatter:
            msg = "formatter must be specified if you want to format metrics"
            raise ValueError(msg)
        if not self.__is_exportable_storage:
            msg = (
                "storage must be ExportableMonitorStorage "
                "if you want to format metrics"
            )
            raise ValueError(msg)
        storage: ExportableMonitorStorage = cast(
            ExportableMonitorStorage,
            self.__storage,
        )
        storage_data = await storage.get_data()
        output_data = self.__output_data_from_storage_data(storage_data)
        formatted: FormattedMetrics = self.__formatter.format_(output_data)
        return formatted

    async def output(self) -> None:
        if not self.__output:
            msg = (
                "output and formatter must be specified "
                "if you want to output metrics"
            )
            raise ValueError(msg)
        await self.__output.write(await self.format_())
