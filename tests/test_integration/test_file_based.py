import json
import os

from aiomon.impl.formatters.json_ import JSONMonitorFormatter
from aiomon.impl.metrics import InfoMetric
from aiomon.impl.monitor import Monitor
from aiomon.impl.outputs.file import FileMonitorOutput
from aiomon.impl.storages.memory import MemoryMonitorStorage


async def test_kv_monitor_data_methods_work():
    monitor = Monitor(
        name="test-monitor",
        output=FileMonitorOutput(path="tests/test.json"),
        formatter=JSONMonitorFormatter(),
        storage=MemoryMonitorStorage(),
    )
    monitor.add_metric(InfoMetric("health"))
    await monitor.metric("health").set_(value={"healthy": False})
    expected_format = json.dumps(
        [
            {
                "name": "health",
                "type": "info",
                "value": {"healthy": False},
                "tags": None,
            }
        ]
    )
    assert await monitor.format_() == expected_format
    await monitor.output()
    os.remove("tests/test.json")
