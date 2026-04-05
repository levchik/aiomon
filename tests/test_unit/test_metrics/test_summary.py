import pytest

from aiomon.impl.metrics.summary import SummaryMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType


@pytest.mark.asyncio
async def test_summary_observe_basic():
    """Test basic observe operation records a value."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(name="request_latency", storage=storage)

    await summary.observe(storage, 100.5)

    data = await storage.get_data()
    assert data["request_latency"]["count"] == 1
    assert data["request_latency"]["sum"] == 100.5
    assert 100.5 in data["request_latency"]["values"]


@pytest.mark.asyncio
async def test_summary_observe_multiple_values():
    """Test observe with multiple values updates count and sum."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(name="request_latency", storage=storage)

    await summary.observe(storage, 100.0)
    await summary.observe(storage, 200.0)
    await summary.observe(storage, 300.0)

    data = await storage.get_data()
    assert data["request_latency"]["count"] == 3
    assert data["request_latency"]["sum"] == 600.0
    assert len(data["request_latency"]["values"]) == 3


@pytest.mark.asyncio
async def test_summary_sum_tracking():
    """Test sum is correctly tracked."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(name="response_size", storage=storage)

    await summary.observe(storage, 50.0)
    await summary.observe(storage, 75.0)
    await summary.observe(storage, 25.0)

    data = await storage.get_data()
    assert data["response_size"]["sum"] == 150.0


@pytest.mark.asyncio
async def test_summary_count_tracking():
    """Test count is correctly tracked."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(name="requests", storage=storage)

    for i in range(10):
        await summary.observe(storage, float(i))

    data = await storage.get_data()
    assert data["requests"]["count"] == 10


@pytest.mark.asyncio
async def test_summary_quantile_calculation():
    """Test quantile calculation is correct."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(
        name="latency", storage=storage, quantiles=(0.5, 0.9, 0.99)
    )

    # Add values 1-100
    for i in range(1, 101):
        await summary.observe(storage, float(i))

    data = await storage.get_data()
    quantiles = data["latency"]["quantiles"]

    # For 100 values (1-100), sorted:
    # 0.5 quantile: pos 50 -> index 49 -> value 50
    # 0.9 quantile: pos 90 -> index 89 -> value 90
    # 0.99 quantile: pos 99 -> index 98 -> value 99
    assert quantiles[0.5] == 50.0
    assert quantiles[0.9] == 90.0
    assert quantiles[0.99] == 99.0


@pytest.mark.asyncio
async def test_summary_custom_quantiles():
    """Test custom quantiles work correctly."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(
        name="latency", storage=storage, quantiles=(0.25, 0.75)
    )

    # Add values 1-100
    for i in range(1, 101):
        await summary.observe(storage, float(i))

    data = await storage.get_data()
    quantiles = data["latency"]["quantiles"]

    # 0.25 quantile: position 0.25 * 100 = 25 -> value at index 24 = 25
    # 0.75 quantile: position 0.75 * 100 = 75 -> value at index 74 = 75
    assert quantiles[0.25] == 25.0
    assert quantiles[0.75] == 75.0
    # Default quantiles should not be present
    assert 0.5 not in quantiles
    assert 0.9 not in quantiles
    assert 0.99 not in quantiles


@pytest.mark.asyncio
async def test_summary_default_quantiles():
    """Test default quantiles are used when not specified."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(name="latency", storage=storage)

    # Add values 1-100
    for i in range(1, 101):
        await summary.observe(storage, float(i))

    data = await storage.get_data()
    quantiles = data["latency"]["quantiles"]

    # Should have default quantiles
    assert 0.5 in quantiles
    assert 0.9 in quantiles
    assert 0.99 in quantiles
    assert len(quantiles) == 3


@pytest.mark.asyncio
async def test_summary_quantiles_sorted():
    """Test quantiles are sorted in the data structure."""
    storage = MemoryMonitorStorage()
    # Use unsorted quantiles
    summary = SummaryMetric(
        name="latency", storage=storage, quantiles=(0.99, 0.5, 0.9)
    )

    for i in range(1, 101):
        await summary.observe(storage, float(i))

    data = await storage.get_data()
    quantiles = data["latency"]["quantiles"]

    # Keys should be sorted
    quantile_keys = list(quantiles.keys())
    assert quantile_keys == sorted(quantile_keys)


@pytest.mark.asyncio
async def test_summary_with_tags():
    """Test summary works with tags."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(
        name="api_latency",
        storage=storage,
        tags=["endpoint:/users", "method:GET"],
    )

    await summary.observe(storage, 50.0)

    data = await storage.get_data()
    assert data["api_latency"]["count"] == 1
    assert summary.tags == ["endpoint:/users", "method:GET"]


@pytest.mark.asyncio
async def test_summary_with_full_metadata():
    """Test summary works with all metadata fields."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(
        name="db_query_time",
        storage=storage,
        tags=["db:postgres"],
        host="db-server-1",
        key="custom_key",
        unit="ms",
        rate=0.5,
        ttl=60,
    )

    await summary.observe(storage, 10.0)

    data = await storage.get_data()
    assert data["db_query_time"]["count"] == 1
    assert summary.host == "db-server-1"
    assert summary.key == "custom_key"
    assert summary.unit == "ms"
    assert summary.rate == 0.5
    assert summary.ttl == 60


@pytest.mark.asyncio
async def test_summary_type_is_summary():
    """Test summary type_ property is MetricType.SUMMARY."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(name="test", storage=storage)
    assert summary.type_ == MetricType.SUMMARY


@pytest.mark.asyncio
async def test_summary_empty_quantiles():
    """Test summary works with empty quantiles tuple."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(name="latency", storage=storage, quantiles=())

    await summary.observe(storage, 100.0)

    data = await storage.get_data()
    assert data["latency"]["count"] == 1
    assert data["latency"]["sum"] == 100.0
    assert data["latency"]["quantiles"] == {}


@pytest.mark.asyncio
async def test_summary_quantile_edge_case_single_value():
    """Test quantile calculation with single value."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(
        name="latency", storage=storage, quantiles=(0.5, 0.9, 0.99)
    )

    await summary.observe(storage, 42.0)

    data = await storage.get_data()
    quantiles = data["latency"]["quantiles"]

    # With single value, all quantiles should return that value
    assert quantiles[0.5] == 42.0
    assert quantiles[0.9] == 42.0
    assert quantiles[0.99] == 42.0


@pytest.mark.asyncio
async def test_summary_negative_values():
    """Test summary can handle negative values."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(name="temperature_change", storage=storage)

    await summary.observe(storage, -10.0)
    await summary.observe(storage, 5.0)
    await summary.observe(storage, -3.0)

    data = await storage.get_data()
    assert data["temperature_change"]["count"] == 3
    assert data["temperature_change"]["sum"] == -8.0


@pytest.mark.asyncio
async def test_summary_float_values():
    """Test summary works with float values."""
    storage = MemoryMonitorStorage()
    summary = SummaryMetric(name="latency", storage=storage)

    await summary.observe(storage, 10.5)
    await summary.observe(storage, 20.7)
    await summary.observe(storage, 30.3)

    data = await storage.get_data()
    assert data["latency"]["sum"] == 61.5
    assert data["latency"]["count"] == 3
