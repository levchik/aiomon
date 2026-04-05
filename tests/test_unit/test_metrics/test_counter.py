"""Unit tests for CounterMetric class."""

import pytest

from aiomon.impl.metrics.counter import CounterMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType


class TestCounterMetricInitialization:
    """Tests for CounterMetric initialization."""

    def test_init_with_name_only(self) -> None:
        """Test that CounterMetric can be initialized with only name."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(name="requests_total", storage=storage)
        assert counter.name == "requests_total"
        assert counter.type_ == MetricType.COUNTER
        assert counter.tags is None

    def test_init_with_all_metadata_fields(self) -> None:
        """Test CounterMetric can be initialized with all metadata fields."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(
            name="requests_total",
            storage=storage,
            tags=["method:GET", "status:200"],
            host="localhost",
            key="http_requests",
            unit="requests",
            rate=1.0,
            ttl=3600,
        )
        assert counter.name == "requests_total"
        assert counter.type_ == MetricType.COUNTER
        assert counter.tags == ["method:GET", "status:200"]
        assert counter.host == "localhost"
        assert counter.key == "http_requests"
        assert counter.unit == "requests"
        assert counter.rate == 1.0
        assert counter.ttl == 3600


class TestCounterMetricWithStorage:
    """Tests for CounterMetric metadata storage."""

    @pytest.mark.asyncio
    async def test_counter_with_storage(self) -> None:
        """Test that counter stores metadata and uses atomic increment."""
        storage = MemoryMonitorStorage()

        # Create counter with storage
        counter = CounterMetric(
            "requests",
            storage=storage,
            tags=["method:GET"],
        )

        # Verify metadata was stored
        metadata = await storage.get_metadata("requests")
        assert metadata is not None
        assert metadata.name == "requests"
        assert metadata.tags == ["method:GET"]

        # Use counter
        await counter.inc(storage, by=1)
        await counter.inc(storage, by=5)

        # Verify value in storage
        data = await storage.get_data()
        assert data["requests"] == 6


class TestCounterMetricInc:
    """Tests for CounterMetric.inc() method."""

    @pytest.mark.asyncio
    async def test_inc_default_value(self) -> None:
        """Test that inc() increments by 1 by default."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(name="requests_total", storage=storage)

        await counter.inc(storage)
        data = await storage.get_data()
        assert data["requests_total"] == 1

        await counter.inc(storage)
        data = await storage.get_data()
        assert data["requests_total"] == 2

    @pytest.mark.asyncio
    async def test_inc_by_one_explicit(self) -> None:
        """Test that inc(by=1) increments by 1."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(name="requests_total", storage=storage)

        await counter.inc(storage, by=1)
        data = await storage.get_data()
        assert data["requests_total"] == 1

    @pytest.mark.asyncio
    async def test_inc_by_custom_value(self) -> None:
        """Test that inc() increments by custom value."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(name="requests_total", storage=storage)

        await counter.inc(storage, by=5)
        data = await storage.get_data()
        assert data["requests_total"] == 5

        await counter.inc(storage, by=10)
        data = await storage.get_data()
        assert data["requests_total"] == 15

    @pytest.mark.asyncio
    async def test_inc_with_tags(self) -> None:
        """Test that inc() works with tags."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(
            name="requests_total",
            storage=storage,
            tags=["method:POST"],
        )

        await counter.inc(storage)
        data = await storage.get_data()
        assert data["requests_total"] == 1


class TestCounterMetricIncBy:
    """Tests for CounterMetric.inc_by() method."""

    @pytest.mark.asyncio
    async def test_inc_by_basic(self) -> None:
        """Test that inc_by() increments by specified value."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(name="bytes_sent", storage=storage)

        await counter.inc_by(storage, 100)
        data = await storage.get_data()
        assert data["bytes_sent"] == 100

    @pytest.mark.asyncio
    async def test_inc_by_multiple_calls(self) -> None:
        """Test that inc_by() accumulates values."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(name="bytes_sent", storage=storage)

        await counter.inc_by(storage, 100)
        await counter.inc_by(storage, 200)
        await counter.inc_by(storage, 50)
        data = await storage.get_data()
        assert data["bytes_sent"] == 350

    @pytest.mark.asyncio
    async def test_inc_by_with_all_metadata(self) -> None:
        """Test that inc_by() works with all metadata fields."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(
            name="bytes_sent",
            storage=storage,
            tags=["endpoint:/api"],
            host="server1",
            key="network_bytes",
            unit="bytes",
        )

        await counter.inc_by(storage, 1024)
        data = await storage.get_data()
        assert data["bytes_sent"] == 1024


class TestCounterMetricReset:
    """Tests for CounterMetric.reset() method."""

    @pytest.mark.asyncio
    async def test_reset_to_zero(self) -> None:
        """Test that reset() resets counter to zero."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(name="requests_total", storage=storage)

        await counter.inc(storage, by=100)
        data = await storage.get_data()
        assert data["requests_total"] == 100

        await counter.reset(storage)
        data = await storage.get_data()
        assert data["requests_total"] == 0

    @pytest.mark.asyncio
    async def test_reset_then_inc_again(self) -> None:
        """Test that counter can be incremented after reset."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(name="requests_total", storage=storage)

        await counter.inc(storage, by=50)
        await counter.reset(storage)
        await counter.inc(storage, by=10)
        data = await storage.get_data()
        assert data["requests_total"] == 10

    @pytest.mark.asyncio
    async def test_reset_already_zero(self) -> None:
        """Test that reset() works when counter is already zero."""
        storage = MemoryMonitorStorage()
        counter = CounterMetric(name="requests_total", storage=storage)

        await counter.reset(storage)
        data = await storage.get_data()
        assert data["requests_total"] == 0

    @pytest.mark.asyncio
    async def test_counter_get_storage_raises_without_storage(self) -> None:
        """Test _get_storage raises RuntimeError without storage."""
        counter = CounterMetric(
            name="requests_total",
            storage=MemoryMonitorStorage(),
        )

        # Clear the bound storage to simulate no storage scenario
        counter._bound_storage = None  # type: ignore[assignment]

        with pytest.raises(RuntimeError, match="No storage provided"):
            await counter.inc(None)  # type: ignore[arg-type]
