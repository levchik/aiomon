"""Tests for MetricGroup class."""

import pytest

from aiomon import (
    CounterMetric,
    GaugeMetric,
    MemoryMonitorStorage,
    MetricGroup,
)


class TestMetricGroup:
    @pytest.mark.asyncio
    async def test_metric_group_type_safe_access(self) -> None:
        """Test that metrics are accessible with full type safety."""
        storage = MemoryMonitorStorage()

        class AppMetrics(MetricGroup, storage=storage):
            requests_total = CounterMetric("requests_total", storage=storage)
            temperature = GaugeMetric("temperature", storage=storage)

        # Type-safe access
        await AppMetrics.requests_total.inc()
        await AppMetrics.temperature.set(25.0)

        # Verify values in storage
        data = await storage.get_data()
        assert data["requests_total"] == 1
        assert data["temperature"] == 25.0
