import json
from typing import Any


class FileMonitorOutput:
    # TODO: aiofiles
    def __init__(self, path: str) -> None:
        self.path = path

    async def write(self, formatted_metrics: Any) -> None:
        # Serialize list[dict] to JSON
        if isinstance(formatted_metrics, list):
            content = json.dumps(formatted_metrics)
        elif isinstance(formatted_metrics, bytes):
            with open(self.path, "wb") as f:
                f.write(formatted_metrics)
            return
        elif isinstance(formatted_metrics, str):
            content = formatted_metrics
        else:
            msg = "formatted_metrics must be bytes, str, or list[dict]"
            raise TypeError(msg)

        with open(self.path, "w") as f:
            f.write(content)
