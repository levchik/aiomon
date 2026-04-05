import pytest

from aiomon.impl.metrics.gauge import GaugeMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType


@pytest.mark.asyncio
async def test_gauge_with_storage() -> None:
    """Test that gauge stores metadata and uses atomic operations."""
    storage = MemoryMonitorStorage()

    # Create gauge with storage
    gauge = GaugeMetric(
        "temperature",
        storage=storage,
        tags=["location:datacenter"],
        value=20.0,
    )

    # Verify metadata was stored
    metadata = await storage.get_metadata("temperature")
    assert metadata is not None
    assert metadata.name == "temperature"

    # Use gauge
    await gauge.set(storage, 25.0)
    await gauge.inc(storage, by=5.0)

    # Verify value in storage
    data = await storage.get_data()
    assert data["temperature"] == 30.0


@pytest.mark.asyncio
async def test_gauge_set():
    """Test set operation sets gauge to specific value."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="temperature", storage=storage)

    await gauge.set(storage, 25.5)

    data = await storage.get_data()
    assert data["temperature"] == 25.5


@pytest.mark.asyncio
async def test_gauge_increment():
    """Test inc operation increments gauge value."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="connections", storage=storage)

    await gauge.set(storage, 10)
    await gauge.inc(storage)
    await gauge.inc(storage)

    data = await storage.get_data()
    assert data["connections"] == 12


@pytest.mark.asyncio
async def test_gauge_increment_by():
    """Test inc with custom by value."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="connections", storage=storage)

    await gauge.set(storage, 10)
    await gauge.inc(storage, by=5)

    data = await storage.get_data()
    assert data["connections"] == 15


@pytest.mark.asyncio
async def test_gauge_decrement():
    """Test dec operation decrements gauge value."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="connections", storage=storage)

    await gauge.set(storage, 10)
    await gauge.dec(storage)
    await gauge.dec(storage)

    data = await storage.get_data()
    assert data["connections"] == 8


@pytest.mark.asyncio
async def test_gauge_decrement_by():
    """Test dec with custom by value."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="connections", storage=storage)

    await gauge.set(storage, 10)
    await gauge.dec(storage, by=3)

    data = await storage.get_data()
    assert data["connections"] == 7


@pytest.mark.asyncio
async def test_gauge_add_alias():
    """Test add is an alias for inc."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="score", storage=storage)

    await gauge.set(storage, 10)
    await gauge.add(storage, 5)

    data = await storage.get_data()
    assert data["score"] == 15


@pytest.mark.asyncio
async def test_gauge_sub_alias():
    """Test sub is an alias for dec."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="score", storage=storage)

    await gauge.set(storage, 10)
    await gauge.sub(storage, 3)

    data = await storage.get_data()
    assert data["score"] == 7


@pytest.mark.asyncio
async def test_gauge_with_initial_value():
    """Test gauge works with initial value parameter."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="temperature", storage=storage, value=20.0)

    # Initial value is used as fallback when no value in storage
    await gauge.inc(storage)
    data = await storage.get_data()
    assert data["temperature"] == 21.0


@pytest.mark.asyncio
async def test_gauge_with_tags():
    """Test gauge works with tags."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(
        name="cpu_usage",
        storage=storage,
        tags=["host:server-1", "core:0"],
    )

    await gauge.set(storage, 75.5)

    data = await storage.get_data()
    assert data["cpu_usage"] == 75.5
    assert gauge.tags == ["host:server-1", "core:0"]


@pytest.mark.asyncio
async def test_gauge_with_full_metadata():
    """Test gauge works with all metadata fields."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(
        name="memory_usage",
        storage=storage,
        tags=["host:server-1"],
        host="server-1",
        key="custom_key",
        unit="bytes",
        rate=0.5,
        ttl=60,
    )

    await gauge.set(storage, 1024)

    data = await storage.get_data()
    assert data["memory_usage"] == 1024
    assert gauge.host == "server-1"
    assert gauge.key == "custom_key"
    assert gauge.unit == "bytes"
    assert gauge.rate == 0.5
    assert gauge.ttl == 60


@pytest.mark.asyncio
async def test_gauge_type_is_gauge():
    """Test gauge type_ property is MetricType.GAUGE."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="test", storage=storage)
    assert gauge.type_ == MetricType.GAUGE


@pytest.mark.asyncio
async def test_gauge_negative_values():
    """Test gauge can handle negative values."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="balance", storage=storage)

    await gauge.set(storage, 10)
    await gauge.dec(storage, by=15)

    data = await storage.get_data()
    assert data["balance"] == -5


@pytest.mark.asyncio
async def test_gauge_float_operations():
    """Test gauge works with float values."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="temperature", storage=storage)

    await gauge.set(storage, 20.5)
    await gauge.inc(storage, by=0.3)
    await gauge.dec(storage, by=0.1)

    data = await storage.get_data()
    assert data["temperature"] == 20.7


@pytest.mark.asyncio
async def test_gauge_set_raises_without_value():
    """Test that set raises ValueError when value is not provided."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="temperature", storage=storage)

    with pytest.raises(ValueError, match="value is required"):
        await gauge.set(storage, None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_gauge_set_raises_with_storage_but_no_value():
    """Test that set raises ValueError when storage provided but no value."""
    storage = MemoryMonitorStorage()
    gauge = GaugeMetric(name="temperature", storage=storage)

    with pytest.raises(
        ValueError, match="value is required when storage is provided"
    ):
        await gauge.set(storage, None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_gauge_get_storage_raises_without_storage():
    """Test _get_storage raises RuntimeError without storage."""
    gauge = GaugeMetric(name="temperature", storage=MemoryMonitorStorage())

    # Clear bound storage to simulate no storage scenario
    gauge._bound_storage = None  # type: ignore[assignment]

    # Call inc/dec which use _get_storage to trigger RuntimeError
    with pytest.raises(RuntimeError, match="No storage provided"):
        await gauge.inc(None)  # type: ignore[arg-type]
