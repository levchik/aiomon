"""Tests for JSONMonitorFormatter."""

from aiomon import (
    CounterMetric,
    GaugeMetric,
    JSONMonitorFormatter,
    MemoryMonitorStorage,
    MonitorOutputData,
    MonitorOutputItem,
)


class TestJSONMonitorFormatter:
    """Tests for JSONMonitorFormatter class."""

    def test_format_basic_counter(self) -> None:
        """Test formatting basic counter metric."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        counter = CounterMetric("requests_total", storage=storage)

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=counter,
                value=100,
            )
        ]

        result = formatter.format_(metrics)

        assert len(result) == 1
        assert result[0]["name"] == "requests_total"
        assert result[0]["type"] == "counter"
        assert result[0]["value"] == 100
        # tags can be None or empty list depending on implementation
        assert result[0]["tags"] is None or result[0]["tags"] == []

    def test_format_basic_gauge(self) -> None:
        """Test formatting basic gauge metric."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        gauge = GaugeMetric("temperature", storage=storage)

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=gauge,
                value=25.5,
            )
        ]

        result = formatter.format_(metrics)

        assert len(result) == 1
        assert result[0]["name"] == "temperature"
        assert result[0]["type"] == "gauge"
        assert result[0]["value"] == 25.5

    def test_format_with_tags(self) -> None:
        """Test formatting metric with tags."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        gauge = GaugeMetric(
            "cpu_usage", storage=storage, tags=["host:server1", "core:0"]
        )

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=gauge,
                value=75.0,
            )
        ]

        result = formatter.format_(metrics)

        assert result[0]["tags"] == ["host:server1", "core:0"]

    def test_format_with_fields_only_filtering(self) -> None:
        """Test fields_only filters metrics by name."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        counter = CounterMetric("requests_total", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=counter,
                value=100,
            ),
            MonitorOutputItem(
                metric=gauge,
                value=25.5,
            ),
        ]

        # fields_only excludes metrics in the set
        result = formatter.format_(metrics, fields_only={"temperature"})

        assert len(result) == 1
        assert result[0]["name"] == "requests_total"

    def test_format_with_fields_only_empty_set(self) -> None:
        """Test that empty fields_only returns all metrics."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        counter = CounterMetric("requests_total", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=counter,
                value=100,
            ),
            MonitorOutputItem(
                metric=gauge,
                value=25.5,
            ),
        ]

        result = formatter.format_(metrics, fields_only=set())

        assert len(result) == 2

    def test_format_with_timestamp(self) -> None:
        """Test formatting metric with timestamp."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        gauge = GaugeMetric(
            "temperature", storage=storage, timestamp=1234567890.0
        )

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=gauge,
                value=25.5,
                timestamp=1234567890.0,
            )
        ]

        result = formatter.format_(metrics)

        assert result[0]["timestamp"] == 1234567890.0

    def test_format_with_ttl(self) -> None:
        """Test formatting metric with ttl."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        gauge = GaugeMetric("temperature", storage=storage, ttl=3600)

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=gauge,
                value=25.5,
                ttl=3600,
            )
        ]

        result = formatter.format_(metrics)

        assert result[0]["ttl"] == 3600

    def test_format_with_unit(self) -> None:
        """Test formatting metric with unit."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        gauge = GaugeMetric("memory_usage", storage=storage, unit="bytes")

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=gauge,
                value=1024,
                unit="bytes",
            )
        ]

        result = formatter.format_(metrics)

        assert result[0]["unit"] == "bytes"

    def test_format_with_rate(self) -> None:
        """Test formatting metric with rate."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        counter = CounterMetric("requests", storage=storage, rate=1.5)

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=counter,
                value=100,
                rate=1.5,
            )
        ]

        result = formatter.format_(metrics)

        assert result[0]["rate"] == 1.5

    def test_format_with_host(self) -> None:
        """Test formatting metric with host."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        gauge = GaugeMetric("cpu_usage", storage=storage, host="server1")

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=gauge,
                value=75.0,
                host="server1",
            )
        ]

        result = formatter.format_(metrics)

        assert result[0]["host"] == "server1"

    def test_format_with_key(self) -> None:
        """Test formatting metric with key."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        gauge = GaugeMetric("memory", storage=storage, key="custom_key")

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=gauge,
                value=1024,
                key="custom_key",
            )
        ]

        result = formatter.format_(metrics)

        assert result[0]["key"] == "custom_key"

    def test_format_with_all_optional_metadata(self) -> None:
        """Test formatting metric with all optional metadata fields."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        gauge = GaugeMetric(
            "memory_usage",
            storage=storage,
            tags=["host:server1"],
            host="server1",
            key="custom_key",
            unit="bytes",
            rate=0.5,
            ttl=3600,
            timestamp=1234567890.0,
        )

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=gauge,
                value=1024,
                timestamp=1234567890.0,
                ttl=3600,
                unit="bytes",
                rate=0.5,
                host="server1",
                key="custom_key",
            )
        ]

        result = formatter.format_(metrics)

        assert result[0]["timestamp"] == 1234567890.0
        assert result[0]["ttl"] == 3600
        assert result[0]["unit"] == "bytes"
        assert result[0]["rate"] == 0.5
        assert result[0]["host"] == "server1"
        assert result[0]["key"] == "custom_key"

    def test_format_without_optional_metadata(self) -> None:
        """Test that optional metadata fields are not included when None."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        gauge = GaugeMetric("temperature", storage=storage)

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=gauge,
                value=25.5,
                timestamp=None,
                ttl=None,
                unit=None,
                rate=None,
                host=None,
                key=None,
            )
        ]

        result = formatter.format_(metrics)

        # Optional fields should not be present when None
        assert "timestamp" not in result[0]
        assert "ttl" not in result[0]
        assert "unit" not in result[0]
        assert "rate" not in result[0]
        assert "host" not in result[0]
        assert "key" not in result[0]

    def test_format_multiple_metrics(self) -> None:
        """Test formatting multiple metrics."""
        formatter = JSONMonitorFormatter()
        storage = MemoryMonitorStorage()

        counter = CounterMetric("requests", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=counter,
                value=100,
            ),
            MonitorOutputItem(
                metric=gauge,
                value=25.5,
            ),
        ]

        result = formatter.format_(metrics)

        assert len(result) == 2
        names = [m["name"] for m in result]
        assert "requests" in names
        assert "temperature" in names
