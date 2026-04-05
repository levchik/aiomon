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

MetricValue_contra = TypeVar("MetricValue_contra", contravariant=True)
FormattedMetrics = TypeVar("FormattedMetrics")
FormattedMetrics_co = TypeVar("FormattedMetrics_co", covariant=True)
FormattedMetrics_contra = TypeVar(
    "FormattedMetrics_contra", contravariant=True
)


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


class MonitorOutputItem(Generic[MetricValue_contra], NamedTuple):
    metric: Metric
    value: MetricValue_contra


MonitorOutputData = List[MonitorOutputItem]
MonitorStorageData = Dict[str, MetricValue_contra]


@runtime_checkable
class MonitorFormatter(Protocol[FormattedMetrics_co]):
    def format_(
        self,
        metrics: MonitorOutputData,
        fields_only: Optional[Set[str]] = None,
    ) -> FormattedMetrics_co:
        ...


@runtime_checkable
class MonitorOutput(Protocol[FormattedMetrics_contra]):
    async def write(self, formatted_metrics: FormattedMetrics_contra) -> None:
        ...


@runtime_checkable
class MonitorStorage(Protocol[MetricValue_contra]):
    async def update(self, name: str, value: MetricValue_contra) -> None:
        ...


@runtime_checkable
class ExportableMonitorStorage(MonitorStorage, Protocol):
    async def get_data(self) -> MonitorStorageData:
        ...
