import os

from aiomon.impl.formatters.json_ import JSONMonitorFormatter
from aiomon.impl.metrics import InfoMetric
from aiomon.impl.monitor import Monitor
from aiomon.impl.outputs.file import FileMonitorOutput
from aiomon.impl.storages.memory import MemoryMonitorStorage


async def test_kv_monitor_data_methods_work():
    storage = MemoryMonitorStorage()
    monitor = Monitor(
        name="test-monitor",
        storage=storage,
        formatter=JSONMonitorFormatter(),
        output=FileMonitorOutput(path="tests/test.json"),
    )
    info = InfoMetric("health", storage=storage)
    await info.set_(storage, {"healthy": False})
    result = await monitor.format_()
    assert len(result) == 1
    item = result[0]
    assert item["name"] == "health"
    assert item["type"] == "info"
    assert item["value"] == {"healthy": False}
    assert item["tags"] is None
    assert "timestamp" in item
    await monitor.output()
    os.remove("tests/test.json")
