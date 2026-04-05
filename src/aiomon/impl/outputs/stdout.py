"""Standard output implementations for monitor metrics."""

import json
import sys
from typing import Any


class StdoutMonitorOutput:
    """Monitor output that writes to standard output."""

    async def write(self, formatted_metrics: Any) -> None:
        """Write formatted metrics to stdout.

        Args:
            formatted_metrics: Formatted metrics (str, bytes, or list[dict]).
        """
        # Serialize list[dict] to JSON
        if isinstance(formatted_metrics, list):
            content = json.dumps(formatted_metrics)
            sys.stdout.write(content)
            sys.stdout.write("\n")
            sys.stdout.flush()
        elif isinstance(formatted_metrics, bytes):
            sys.stdout.buffer.write(formatted_metrics)
            sys.stdout.buffer.write(b"\n")
            sys.stdout.buffer.flush()
        elif isinstance(formatted_metrics, str):
            sys.stdout.write(formatted_metrics)
            sys.stdout.write("\n")
            sys.stdout.flush()
        else:
            msg = "formatted_metrics must be bytes, str, or list[dict]"
            raise TypeError(msg)


class StderrMonitorOutput:
    """Monitor output that writes to standard error."""

    async def write(self, formatted_metrics: Any) -> None:
        """
        Write formatted metrics to stderr.

        Args:
            formatted_metrics: Formatted metrics (str, bytes, or list[dict]).
        """
        # Serialize list[dict] to JSON
        if isinstance(formatted_metrics, list):
            content = json.dumps(formatted_metrics)
            sys.stderr.write(content)
            sys.stderr.write("\n")
            sys.stderr.flush()
        elif isinstance(formatted_metrics, bytes):
            sys.stderr.buffer.write(formatted_metrics)
            sys.stderr.buffer.write(b"\n")
            sys.stderr.buffer.flush()
        elif isinstance(formatted_metrics, str):
            sys.stderr.write(formatted_metrics)
            sys.stderr.write("\n")
            sys.stderr.flush()
        else:
            msg = "formatted_metrics must be bytes, str, or list[dict]"
            raise TypeError(msg)
