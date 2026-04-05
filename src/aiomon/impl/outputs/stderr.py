import json
import sys
from typing import Any


class StderrMonitorOutput:
    """Output metrics to stderr."""

    async def write(self, formatted_metrics: Any) -> None:
        # Serialize list[dict] to JSON
        if isinstance(formatted_metrics, list):
            content = json.dumps(formatted_metrics)
            sys.stderr.write(content)
        elif isinstance(formatted_metrics, bytes):
            sys.stderr.buffer.write(formatted_metrics)
        elif isinstance(formatted_metrics, str):
            sys.stderr.write(formatted_metrics)
        else:
            msg = "formatted_metrics must be bytes, str, or list[dict]"
            raise TypeError(msg)
        sys.stderr.write("\n")
        sys.stderr.flush()
