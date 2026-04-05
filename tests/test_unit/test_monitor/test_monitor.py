"""Unit tests for Monitor class."""

import pytest

from aiomon.impl.formatters.json_ import JSONMonitorFormatter
from aiomon.impl.metrics.counter import CounterMetric
from aiomon.impl.metrics.gauge import GaugeMetric
from aiomon.impl.monitor import Monitor
from aiomon.impl.storages.memory import MemoryMonitorStorage


@pytest.mark.asyncio
async def test_monitor_reads_metadata_from_storage() -> None:
    """Test that monitor reads metric metadata from storage."""
    storage = MemoryMonitorStorage()

    # Create metrics (they store metadata in storage)
    counter = CounterMetric("requests", storage=storage, tags=["method:GET"])
    gauge = GaugeMetric("temperature", storage=storage, tags=["location:dc"])

    # Create monitor (no need to add metrics!)
    monitor = Monitor(
        name="test",
        storage=storage,
        formatter=JSONMonitorFormatter(),
    )

    # Update metric values
    await counter.inc(storage, by=10)
    await gauge.set(storage, 25.0)

    # Format - should read metadata from storage
    data = await monitor.format_()

    # Verify all metrics are formatted with their metadata
    assert len(data) == 2
    metrics_map = {m["name"]: m for m in data}

    assert metrics_map["requests"]["value"] == 10
    assert metrics_map["requests"]["tags"] == ["method:GET"]

    assert metrics_map["temperature"]["value"] == 25.0
    assert metrics_map["temperature"]["tags"] == ["location:dc"]


@pytest.mark.asyncio
async def test_monitor_add_metric_backward_compat() -> None:
    """Test that add_metric() still works for backward compatibility."""
    storage = MemoryMonitorStorage()

    monitor = Monitor(
        name="test",
        storage=storage,
        formatter=JSONMonitorFormatter(),
    )

    # Create metric and explicitly add to monitor
    counter = CounterMetric("requests", storage=storage, tags=["method:POST"])
    await monitor.add_metric(counter)

    # Update value using the same counter instance
    await counter.inc(storage, by=5)

    # Format - should include the metric
    data = await monitor.format_()

    assert len(data) == 1
    assert data[0]["value"] == 5
    assert data[0]["tags"] == ["method:POST"]


@pytest.mark.asyncio
async def test_monitor_output_raises_when_no_output_configured() -> None:
    """Test that output() raises ValueError when no output is configured."""
    storage = MemoryMonitorStorage()

    monitor = Monitor(
        name="test",
        storage=storage,
        formatter=JSONMonitorFormatter(),
        output=None,
    )

    with pytest.raises(ValueError, match="No output configured"):
        await monitor.output()
