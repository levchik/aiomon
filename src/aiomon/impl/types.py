from aiomon.base import Metric


class UniqueMetricsDict(dict):
    def __setitem__(self, key: str, value: Metric) -> None:
        if key in self:
            msg = f"Key {key} already exists"
            raise KeyError(msg)
        super().__setitem__(key, value)
