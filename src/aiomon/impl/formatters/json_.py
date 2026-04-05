from typing import Any

from aiomon.base import MonitorFormatter, MonitorOutputData


class JSONMonitorFormatter(MonitorFormatter[list[dict[str, Any]]]):
    """Format metrics as JSON array."""

    def format_(
        self,
        metrics: MonitorOutputData,
        fields_only: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        if fields_only is None:
            fields_only = set()

        output: list[dict[str, Any]] = []
        for metric in metrics:
            if metric.metric.name not in fields_only:
                item: dict[str, Any] = {
                    "name": metric.metric.name,
                    "type": metric.metric.type_,
                    "value": metric.value,
                    "tags": metric.metric.tags,
                }
                # Add optional metadata fields only if they are not None
                if metric.timestamp is not None:
                    item["timestamp"] = metric.timestamp
                if metric.ttl is not None:
                    item["ttl"] = metric.ttl
                if metric.unit is not None:
                    item["unit"] = metric.unit
                if metric.rate is not None:
                    item["rate"] = metric.rate
                if metric.host is not None:
                    item["host"] = metric.host
                if metric.key is not None:
                    item["key"] = metric.key
                output.append(item)
        return output
