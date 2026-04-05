"""Integration tests for multiple monitors sharing storage."""

import pytest

from aiomon import (
    CounterMetric,
    GaugeMetric,
    JSONMonitorFormatter,
    MemoryMonitorStorage,
    MetricGroup,
    Monitor,
    PrometheusFormatter,
)


class TestMultipleMonitorsShareStorage:
    """Test that multiple monitors can share the same storage."""

    @pytest.mark.asyncio
    async def test_multiple_monitors_share_storage(self) -> None:
        """Test multiple monitors see same data from shared storage."""
        storage = MemoryMonitorStorage()

        # Create metrics
        class AppMetrics(MetricGroup, storage=storage):
            requests = CounterMetric("requests", storage=storage)
            temp = GaugeMetric("temp", storage=storage)

        # Create multiple monitors with different formatters
        prom_monitor = Monitor(
            name="prometheus",
            storage=storage,
            formatter=PrometheusFormatter(),
        )

        json_monitor = Monitor(
            name="json",
            storage=storage,
            formatter=JSONMonitorFormatter(),
        )

        # Update metrics
        await AppMetrics.requests.inc()
        await AppMetrics.temp.set(25.0)

        # Both monitors should see the same data
        prom_data = await prom_monitor.format_()
        json_data = await json_monitor.format_()

        # Prometheus format
        assert "requests 1" in prom_data
        assert "temp 25.0" in prom_data

        # JSON format
        assert len(json_data) == 2
        metrics_map = {m["name"]: m["value"] for m in json_data}
        assert metrics_map["requests"] == 1
        assert metrics_map["temp"] == 25.0
