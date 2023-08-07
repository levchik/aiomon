import json
from typing import Optional, Set

from aiomon.base import MonitorOutputData


class JSONMonitorFormatter:
    def format_(
        self,
        metrics: MonitorOutputData,
        fields_only: Optional[Set[str]] = None,
    ) -> str:
        if fields_only is None:
            fields_only = set()

        output = []
        for metric in metrics:
            if metric.metric.name not in fields_only:
                output.append(
                    {
                        "name": metric.metric.name,
                        "type": metric.metric.type_,
                        "value": metric.value,
                        "tags": metric.metric.tags,
                    }
                )
        return json.dumps(output)
