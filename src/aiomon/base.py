import sys
from typing import (
    Dict,
    Generic,
    List,
    NamedTuple,
    Optional,
    Set,
    TypeVar,
)

from aiomon.types import MetricType

if sys.version_info >= (3, 8):  # pragma: py-lt-38
    from typing import Protocol, runtime_checkable
else:  # pragma: py-gte-38
    from typing_extensions import Protocol, runtime_checkable

MetricValue = TypeVar("MetricValue", contravariant=True)
FormattedMetrics = TypeVar("FormattedMetrics")
FormattedMetrics_co = TypeVar("FormattedMetrics_co", covariant=True)
FormattedMetrics_con = TypeVar("FormattedMetrics_con", contravariant=True)


@runtime_checkable
class Metric(Protocol):
    @property
    def type_(self) -> MetricType:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def tags(self) -> Optional[List[str]]:
        ...


class MonitorOutputItem(Generic[MetricValue], NamedTuple):
    metric: Metric
    value: MetricValue


MonitorOutputData = List[MonitorOutputItem]
MonitorStorageData = Dict[str, MetricValue]


@runtime_checkable
class MonitorFormatter(Protocol[FormattedMetrics_co]):
    def format_(
        self,
        metrics: MonitorOutputData,
        fields_only: Optional[Set[str]] = None,
    ) -> FormattedMetrics_co:
        ...


@runtime_checkable
class MonitorOutput(Protocol[FormattedMetrics_con]):
    async def write(self, formatted_metrics: FormattedMetrics_con) -> None:
        ...


@runtime_checkable
class MonitorStorage(Protocol[MetricValue]):
    async def update(self, name: str, value: MetricValue) -> None:
        ...


@runtime_checkable
class ExportableMonitorStorage(MonitorStorage, Protocol):
    async def get_data(self) -> MonitorStorageData:
        ...
