"""Unit tests for HistogramMetric class."""

import pytest

from aiomon.impl.metrics.histogram import HistogramMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType


class TestHistogramMetricInitialization:
    """Tests for HistogramMetric initialization."""

    def test_init_with_name_only(self) -> None:
        """Test that HistogramMetric can be initialized with only name."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(name="request_duration", storage=storage)
        assert histogram.name == "request_duration"
        assert histogram.type_ == MetricType.HISTOGRAM
        assert histogram.tags is None

    def test_init_with_all_metadata_fields(self) -> None:
        """Test HistogramMetric can be initialized with all metadata fields."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(
            name="request_duration",
            storage=storage,
            tags=["endpoint:/api"],
            host="localhost",
            key="http_duration",
            unit="seconds",
            rate=1.0,
            ttl=3600,
        )
        assert histogram.name == "request_duration"
        assert histogram.type_ == MetricType.HISTOGRAM
        assert histogram.tags == ["endpoint:/api"]
        assert histogram.host == "localhost"
        assert histogram.key == "http_duration"
        assert histogram.unit == "seconds"
        assert histogram.rate == 1.0
        assert histogram.ttl == 3600

    def test_init_with_custom_buckets(self) -> None:
        """Test HistogramMetric can be initialized with custom buckets."""
        storage = MemoryMonitorStorage()
        custom_buckets = (0.1, 0.5, 1.0, 5.0, float("inf"))
        histogram = HistogramMetric(
            name="request_duration",
            storage=storage,
            buckets=custom_buckets,
        )
        assert histogram._buckets == custom_buckets

    def test_init_default_buckets(self) -> None:
        """Test HistogramMetric uses default buckets when not specified."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(name="request_duration", storage=storage)
        assert histogram._buckets == HistogramMetric.DEFAULT_BUCKETS


class TestHistogramMetricObserve:
    """Tests for HistogramMetric.observe() method."""

    @pytest.mark.asyncio
    async def test_observe_single_value(self) -> None:
        """Test that observe() records a single value."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(name="request_duration", storage=storage)

        await histogram.observe(storage, 0.05)
        data = await storage.get_data()

        assert data["request_duration"]["count"] == 1
        assert data["request_duration"]["sum"] == 0.05

    @pytest.mark.asyncio
    async def test_observe_multiple_values(self) -> None:
        """Test that observe() accumulates values."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(name="request_duration", storage=storage)

        await histogram.observe(storage, 0.1)
        await histogram.observe(storage, 0.2)
        await histogram.observe(storage, 0.3)
        data = await storage.get_data()

        assert data["request_duration"]["count"] == 3
        assert abs(data["request_duration"]["sum"] - 0.6) < 0.0001

    @pytest.mark.asyncio
    async def test_observe_bucket_counts_cumulative(self) -> None:
        """Test that bucket counts are cumulative."""
        storage = MemoryMonitorStorage()
        # Use simple buckets for easier testing
        histogram = HistogramMetric(
            name="request_duration",
            storage=storage,
            buckets=(0.1, 0.5, 1.0, float("inf")),
        )

        # Value 0.05 should be in bucket 0.1 and all higher buckets
        await histogram.observe(storage, 0.05)
        data = await storage.get_data()
        buckets = data["request_duration"]["buckets"]

        assert buckets[0.1] == 1
        assert buckets[0.5] == 1
        assert buckets[1.0] == 1
        assert buckets[float("inf")] == 1

        # Value 0.3 should be in bucket 0.5 and higher, but not 0.1
        await histogram.observe(storage, 0.3)
        data = await storage.get_data()
        buckets = data["request_duration"]["buckets"]

        assert buckets[0.1] == 1  # Only first value
        assert buckets[0.5] == 2  # Both values
        assert buckets[1.0] == 2  # Both values
        assert buckets[float("inf")] == 2  # Both values

    @pytest.mark.asyncio
    async def test_observe_value_exactly_on_bucket_boundary(self) -> None:
        """Test value on bucket boundary is counted in that bucket."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(
            name="request_duration",
            storage=storage,
            buckets=(0.1, 0.5, 1.0, float("inf")),
        )

        # Value exactly at 0.1 boundary
        await histogram.observe(storage, 0.1)
        data = await storage.get_data()
        buckets = data["request_duration"]["buckets"]

        assert buckets[0.1] == 1  # Value <= 0.1, so counted
        assert buckets[0.5] == 1
        assert buckets[1.0] == 1
        assert buckets[float("inf")] == 1

    @pytest.mark.asyncio
    async def test_observe_with_custom_buckets(self) -> None:
        """Test observe() works with custom buckets."""
        storage = MemoryMonitorStorage()
        custom_buckets = (10.0, 50.0, 100.0, float("inf"))
        histogram = HistogramMetric(
            name="response_size",
            storage=storage,
            buckets=custom_buckets,
        )

        await histogram.observe(storage, 25.0)
        data = await storage.get_data()

        assert data["response_size"]["count"] == 1
        assert data["response_size"]["sum"] == 25.0
        assert data["response_size"]["buckets"][10.0] == 0
        assert data["response_size"]["buckets"][50.0] == 1
        assert data["response_size"]["buckets"][100.0] == 1
        assert data["response_size"]["buckets"][float("inf")] == 1

    @pytest.mark.asyncio
    async def test_observe_with_default_buckets(self) -> None:
        """Test observe() works with default buckets."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(name="request_duration", storage=storage)

        await histogram.observe(storage, 0.03)
        data = await storage.get_data()

        assert data["request_duration"]["count"] == 1
        assert data["request_duration"]["sum"] == 0.03
        # Check that default buckets are initialized
        assert 0.05 in data["request_duration"]["buckets"]
        assert 1.0 in data["request_duration"]["buckets"]
        assert float("inf") in data["request_duration"]["buckets"]

    @pytest.mark.asyncio
    async def test_observe_with_tags(self) -> None:
        """Test that observe() works with tags."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(
            name="request_duration",
            storage=storage,
            tags=["method:GET"],
        )

        await histogram.observe(storage, 0.1)
        data = await storage.get_data()

        assert data["request_duration"]["count"] == 1
        assert data["request_duration"]["sum"] == 0.1

    @pytest.mark.asyncio
    async def test_observe_zero_value(self) -> None:
        """Test that observe() handles zero value."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(name="request_duration", storage=storage)

        await histogram.observe(storage, 0.0)
        data = await storage.get_data()

        assert data["request_duration"]["count"] == 1
        assert data["request_duration"]["sum"] == 0.0

    @pytest.mark.asyncio
    async def test_observe_large_value(self) -> None:
        """Test that observe() handles large values."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(name="request_duration", storage=storage)

        await histogram.observe(storage, 1000000.0)
        data = await storage.get_data()

        assert data["request_duration"]["count"] == 1
        assert data["request_duration"]["sum"] == 1000000.0
        # Only the inf bucket should have count 1 for a very large value
        assert data["request_duration"]["buckets"][float("inf")] == 1
        # All finite buckets should have count 0
        for bucket, count in data["request_duration"]["buckets"].items():
            if bucket != float("inf"):
                assert count == 0

    @pytest.mark.asyncio
    async def test_observe_multiple_values_bucket_accumulation(self) -> None:
        """Test bucket counts accumulate over multiple observations."""
        storage = MemoryMonitorStorage()
        histogram = HistogramMetric(
            name="request_duration",
            storage=storage,
            buckets=(0.1, 0.5, 1.0, float("inf")),
        )

        # Add values in different ranges
        await histogram.observe(storage, 0.05)  # In all buckets
        await histogram.observe(storage, 0.25)  # In 0.5, 1.0, inf
        await histogram.observe(storage, 0.75)  # In 1.0, inf
        await histogram.observe(storage, 2.0)  # Only in inf

        data = await storage.get_data()
        buckets = data["request_duration"]["buckets"]

        assert buckets[0.1] == 1  # Only 0.05
        assert buckets[0.5] == 2  # 0.05, 0.25
        assert buckets[1.0] == 3  # 0.05, 0.25, 0.75
        assert buckets[float("inf")] == 4  # All values

        assert data["request_duration"]["count"] == 4
        # 0.05 + 0.25 + 0.75 + 2.0 = 3.05
        assert data["request_duration"]["sum"] == 3.05
