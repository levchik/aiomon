from typing import AnyStr


class FileMonitorOutput:
    # TODO: aiofiles
    def __init__(self, path: str) -> None:
        self.path = path

    async def write(self, formatted_metrics: AnyStr) -> None:
        if isinstance(formatted_metrics, bytes):
            mode = "wb"
        elif isinstance(formatted_metrics, str):
            mode = "w"
        else:
            msg = "formatted_metrics must be bytes or str"
            raise TypeError(msg)

        with open(self.path, mode) as f:
            f.write(formatted_metrics)
