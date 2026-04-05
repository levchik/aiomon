import abc
from typing import Dict, List, Optional

from aiomon.base import MonitorStorage
from aiomon.types import MetricType


class BaseMetric(metaclass=abc.ABCMeta):
    type_: MetricType
    name: str
    tags: Optional[List[str]]

    def __init__(self, name: str, tags: Optional[List[str]] = None) -> None:
        self.name = name
        self.tags = tags


class InfoMetric(BaseMetric):
    type_: MetricType = MetricType.INFO

    async def set_(self, value: Dict, storage: MonitorStorage) -> None:
        await storage.update(name=self.name, value=value)
