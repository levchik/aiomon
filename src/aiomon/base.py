from typing import Generic, NamedTuple, Protocol, TypeVar, runtime_checkable

from aiomon.types import MetricType

T_co = TypeVar("T_co", covariant=True)
MetricValue_contra = TypeVar("MetricValue_contra", contravariant=True)
FormattedMetrics = TypeVar("FormattedMetrics")
FormattedMetrics_co = TypeVar("FormattedMetrics_co", covariant=True)
FormattedMetrics_contra = TypeVar(
    "FormattedMetrics_contra", contravariant=True
)


@runtime_checkable
class Metric(Protocol):
    @property
    def type_(self) -> MetricType: ...

    @property
    def name(self) -> str: ...

    @property
    def tags(self) -> list[str] | None: ...

    @property
    def timestamp(self) -> float | None: ...

    @property
    def ttl(self) -> int | None: ...

    @property
    def unit(self) -> str | None: ...

    @property
    def rate(self) -> float | None: ...

    @property
    def host(self) -> str | None: ...

    @property
    def key(self) -> str | None: ...


class MonitorOutputItem(Generic[MetricValue_contra], NamedTuple):
    metric: Metric
    value: MetricValue_contra
    timestamp: float | None = None
    ttl: int | None = None
    unit: str | None = None
    rate: float | None = None
    host: str | None = None
    key: str | None = None


MonitorOutputData = list[MonitorOutputItem]
MonitorStorageData = dict[str, MetricValue_contra]


@runtime_checkable
class MonitorFormatter(Protocol[T_co]):
    """Format metrics into output type T_co."""

    def format_(
        self,
        metrics: MonitorOutputData,
        fields_only: set[str] | None = None,
    ) -> T_co: ...


@runtime_checkable
class MonitorOutput(Protocol[FormattedMetrics_contra]):
    async def write(
        self, formatted_metrics: FormattedMetrics_contra
    ) -> None: ...


@runtime_checkable
class MonitorStorage(Protocol[MetricValue_contra]):
    async def update(self, name: str, value: MetricValue_contra) -> None: ...


@runtime_checkable
class ExportableMonitorStorage(MonitorStorage, Protocol):
    async def get_data(self) -> MonitorStorageData: ...
    async def get_metadata(self, name: str) -> Metric | None: ...
    async def store_metadata(self, metric: Metric) -> None: ...
