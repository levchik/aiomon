"""Integration tests for all metric types with Monitor class."""

import pytest

from aiomon import (
    CounterMetric,
    EnumMetric,
    GaugeMetric,
    HistogramMetric,
    InfoMetric,
    JSONMonitorFormatter,
    MemoryMonitorStorage,
    Monitor,
    SummaryMetric,
)


class TestAllMetricsWithMonitor:
    """Test all metric types working together with Monitor."""

    @pytest.mark.asyncio
    async def test_create_monitor_with_all_metric_types(self) -> None:
        """Test creating a Monitor with all metric types."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        # Create metrics with storage (they auto-register metadata)
        counter = CounterMetric("requests", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)
        histogram = HistogramMetric("latency", storage=storage)
        summary = SummaryMetric("response_time", storage=storage)
        enum = EnumMetric("state", states=["up", "down"], storage=storage)
        info = InfoMetric("info", storage=storage)

        # Explicitly add to monitor (optional, for backward compat)
        await monitor.add_metric(counter)
        await monitor.add_metric(gauge)
        await monitor.add_metric(histogram)
        await monitor.add_metric(summary)
        await monitor.add_metric(enum)
        await monitor.add_metric(info)

        # Update values
        await counter.inc(storage)
        await gauge.set(storage, 25.0)
        await histogram.observe(storage, 0.5)
        await summary.observe(storage, 0.3)
        await enum.set(storage, "up")
        await info.set_(storage, {"version": "1.0"})

        # Format and verify all metrics are present
        data = await monitor.format_()
        assert len(data) == 6
        names = {item["name"] for item in data}
        expected = {
            "requests",
            "temperature",
            "latency",
            "response_time",
            "state",
            "info",
        }
        assert names == expected

    @pytest.mark.asyncio
    async def test_update_all_metric_types(self) -> None:
        """Test updating each metric type."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()

        # Create metrics with storage
        counter = CounterMetric("requests", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)
        histogram = HistogramMetric("latency", storage=storage)
        summary = SummaryMetric("response_time", storage=storage)
        enum = EnumMetric("state", states=["up", "down"], storage=storage)
        info = InfoMetric("info", storage=storage)

        # Update values
        await counter.inc(storage)
        await gauge.set(storage, 25.0)
        await histogram.observe(storage, 0.5)
        await summary.observe(storage, 0.3)
        await enum.set(storage, "up")
        await info.set_(storage, {"version": "1.0"})

        # Verify storage has all values
        data = await storage.get_data()
        assert len(data) == 6
        assert data["requests"] == 1
        assert data["temperature"] == 25.0
        assert "latency" in data
        assert "response_time" in data
        assert data["state"] == "up"
        assert data["info"] == {"version": "1.0"}

    @pytest.mark.asyncio
    async def test_format_all_metrics_with_json(self) -> None:
        """Test formatting output with JSON for all metric types."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        # Create metrics with storage
        counter = CounterMetric("requests", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)
        histogram = HistogramMetric("latency", storage=storage)
        summary = SummaryMetric("response_time", storage=storage)
        enum = EnumMetric("state", states=["up", "down"], storage=storage)
        info = InfoMetric("info", storage=storage)

        # Update values
        await counter.inc(storage)
        await gauge.set(storage, 25.0)
        await histogram.observe(storage, 0.5)
        await summary.observe(storage, 0.3)
        await enum.set(storage, "up")
        await info.set_(storage, {"version": "1.0"})

        # Format and verify
        data = await monitor.format_()
        assert len(data) == 6

        # Create a map for easier assertions
        metrics_map = {item["name"]: item for item in data}

        # Verify CounterMetric
        assert metrics_map["requests"]["type"] == "counter"
        assert metrics_map["requests"]["value"] == 1

        # Verify GaugeMetric
        assert metrics_map["temperature"]["type"] == "gauge"
        assert metrics_map["temperature"]["value"] == 25.0

        # Verify HistogramMetric
        assert metrics_map["latency"]["type"] == "histogram"
        assert "buckets" in metrics_map["latency"]["value"]

        # Verify SummaryMetric
        assert metrics_map["response_time"]["type"] == "summary"
        assert "count" in metrics_map["response_time"]["value"]
        assert "sum" in metrics_map["response_time"]["value"]
        assert "quantiles" in metrics_map["response_time"]["value"]

        # Verify EnumMetric
        assert metrics_map["state"]["type"] == "enum"
        assert metrics_map["state"]["value"] == "up"

        # Verify InfoMetric
        assert metrics_map["info"]["type"] == "info"
        assert metrics_map["info"]["value"] == {"version": "1.0"}

    @pytest.mark.asyncio
    async def test_all_metrics_have_required_fields(self) -> None:
        """Test that all metrics have required fields in output."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        # Create metrics with storage
        counter = CounterMetric("requests", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)
        histogram = HistogramMetric("latency", storage=storage)
        summary = SummaryMetric("response_time", storage=storage)
        enum = EnumMetric("state", states=["up", "down"], storage=storage)
        info = InfoMetric("info", storage=storage)

        # Update values
        await counter.inc(storage)
        await gauge.set(storage, 25.0)
        await histogram.observe(storage, 0.5)
        await summary.observe(storage, 0.3)
        await enum.set(storage, "up")
        await info.set_(storage, {"version": "1.0"})

        # Format and verify
        data = await monitor.format_()

        # Each metric should have name, type, value, tags, timestamp
        for item in data:
            assert "name" in item
            assert "type" in item
            assert "value" in item
            assert "tags" in item
            assert "timestamp" in item

    @pytest.mark.asyncio
    async def test_multiple_updates_same_metric(self) -> None:
        """Test multiple updates to the same metric."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        # Create metrics with storage
        counter = CounterMetric("requests", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)

        # Multiple updates
        await counter.inc(storage)
        await counter.inc(storage)
        await counter.inc(storage)

        await gauge.set(storage, 20.0)
        await gauge.set(storage, 25.0)
        await gauge.set(storage, 30.0)

        # Format and verify
        data = await monitor.format_()
        metrics_map = {item["name"]: item for item in data}
        assert metrics_map["requests"]["value"] == 3
        assert metrics_map["temperature"]["value"] == 30.0


class TestMetricTypesCorrectness:
    """Test that metric types are correctly identified in output."""

    @pytest.mark.asyncio
    async def test_counter_type_in_output(self) -> None:
        """Test CounterMetric type appears correctly in output."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        counter = CounterMetric("requests", storage=storage)
        await counter.inc(storage)

        data = await monitor.format_()
        assert data[0]["type"] == "counter"

    @pytest.mark.asyncio
    async def test_gauge_type_in_output(self) -> None:
        """Test GaugeMetric type appears correctly in output."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        gauge = GaugeMetric("temperature", storage=storage)
        await gauge.set(storage, 25.0)

        data = await monitor.format_()
        assert data[0]["type"] == "gauge"

    @pytest.mark.asyncio
    async def test_histogram_type_in_output(self) -> None:
        """Test HistogramMetric type appears correctly in output."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        histogram = HistogramMetric("latency", storage=storage)
        await histogram.observe(storage, 0.5)

        data = await monitor.format_()
        assert data[0]["type"] == "histogram"

    @pytest.mark.asyncio
    async def test_summary_type_in_output(self) -> None:
        """Test SummaryMetric type appears correctly in output."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        summary = SummaryMetric("response_time", storage=storage)
        await summary.observe(storage, 0.3)

        data = await monitor.format_()
        assert data[0]["type"] == "summary"

    @pytest.mark.asyncio
    async def test_enum_type_in_output(self) -> None:
        """Test EnumMetric type appears correctly in output."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        enum = EnumMetric("state", states=["up", "down"], storage=storage)
        await enum.set(storage, "up")

        data = await monitor.format_()
        assert data[0]["type"] == "enum"

    @pytest.mark.asyncio
    async def test_info_type_in_output(self) -> None:
        """Test InfoMetric type appears correctly in output."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
        )

        info = InfoMetric("info", storage=storage)
        await info.set_(storage, {"version": "1.0"})

        data = await monitor.format_()
        assert data[0]["type"] == "info"
