"""Unit tests for MemoryMonitorStorage TTL functionality."""

import asyncio

import pytest

from aiomon.impl.metrics.counter import CounterMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage


@pytest.mark.asyncio
async def test_update_with_ttl_stores_value():
    """Test that setting value with TTL works."""
    storage: MemoryMonitorStorage = MemoryMonitorStorage()
    await storage.update("test_key", "test_value", ttl=10.0)

    data = await storage.get_data()
    assert data["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_value_exists_before_expiration():
    """Test that value exists before TTL expiration."""
    storage: MemoryMonitorStorage = MemoryMonitorStorage()
    await storage.update("test_key", "test_value", ttl=1.0)

    # Get data immediately - should exist
    data = await storage.get_data()
    assert "test_key" in data
    assert data["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_value_is_gone_after_expiration():
    """Test that value is filtered out after TTL expiration."""
    storage: MemoryMonitorStorage = MemoryMonitorStorage()

    # Set value with very short TTL (0.1 seconds)
    await storage.update("test_key", "test_value", ttl=0.1)

    # Verify it exists initially
    data = await storage.get_data()
    assert "test_key" in data

    # Wait for expiration
    await asyncio.sleep(0.15)

    # Verify it's gone
    data = await storage.get_data()
    assert "test_key" not in data


@pytest.mark.asyncio
async def test_values_without_ttl_dont_expire():
    """Test that values without TTL don't expire."""
    storage: MemoryMonitorStorage = MemoryMonitorStorage()

    # Set value without TTL
    await storage.update("test_key", "test_value")

    # Wait a bit
    await asyncio.sleep(0.1)

    # Value should still exist
    data = await storage.get_data()
    assert "test_key" in data
    assert data["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_cleanup_expired_removes_expired_entries():
    """Test that cleanup_expired removes expired entries."""
    storage: MemoryMonitorStorage = MemoryMonitorStorage()

    # Set one value with short TTL and one without
    await storage.update("expired_key", "expired_value", ttl=0.1)
    await storage.update("persistent_key", "persistent_value")

    # Wait for expiration
    await asyncio.sleep(0.15)

    # Call cleanup
    await storage.cleanup_expired()

    # Get data - expired should be gone, persistent should remain
    data = await storage.get_data()
    assert "expired_key" not in data
    assert "persistent_key" in data
    assert data["persistent_key"] == "persistent_value"


@pytest.mark.asyncio
async def test_update_without_ttl_parameter():
    """Test backward compatibility - update without ttl parameter."""
    storage: MemoryMonitorStorage = MemoryMonitorStorage()

    # Old-style call without ttl should still work
    await storage.update("test_key", "test_value")

    data = await storage.get_data()
    assert data["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_multiple_values_with_different_ttls():
    """Test multiple values with different TTLs expire correctly."""
    storage: MemoryMonitorStorage = MemoryMonitorStorage()

    # Set values with different TTLs
    await storage.update("short_ttl", "short_value", ttl=0.1)
    await storage.update("long_ttl", "long_value", ttl=10.0)
    await storage.update("no_ttl", "no_ttl_value")

    # All should exist initially
    data = await storage.get_data()
    assert len(data) == 3
    assert data["short_ttl"] == "short_value"
    assert data["long_ttl"] == "long_value"
    assert data["no_ttl"] == "no_ttl_value"

    # Wait for short TTL to expire
    await asyncio.sleep(0.15)

    # Only short_ttl should be gone
    data = await storage.get_data()
    assert "short_ttl" not in data
    assert data["long_ttl"] == "long_value"
    assert data["no_ttl"] == "no_ttl_value"


@pytest.mark.asyncio
async def test_modify_atomic_increment() -> None:
    """Test that modify performs atomic read-modify-write."""
    storage: MemoryMonitorStorage = MemoryMonitorStorage()

    # Initial increment
    result1 = await storage.modify(
        name="counter",
        modifier=lambda v: (v or 0) + 1,
    )
    assert result1 == 1

    # Second increment
    result2 = await storage.modify(
        name="counter",
        modifier=lambda v: (v or 0) + 1,
    )
    assert result2 == 2

    # Verify final value in storage
    data = await storage.get_data()
    assert data["counter"] == 2


@pytest.mark.asyncio
async def test_store_and_get_metadata() -> None:
    """Test that storage can store and retrieve metric metadata."""
    storage: MemoryMonitorStorage = MemoryMonitorStorage()

    # Create metric (auto-stores metadata)
    CounterMetric("requests", storage=storage, tags=["method:GET"])

    # Retrieve metadata
    metadata = await storage.get_metadata("requests")

    assert metadata is not None
    assert metadata.name == "requests"
    assert metadata.tags == ["method:GET"]
    assert metadata.type_ == "counter"
