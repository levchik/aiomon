"""Unit tests for EnumMetric class."""

import pytest

from aiomon.impl.metrics.enum import EnumMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.types import MetricType


class TestEnumMetricInitialization:
    """Tests for EnumMetric initialization."""

    def test_init_with_name_and_states(self) -> None:
        """Test that EnumMetric can be initialized with name and states."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            storage=storage,
        )
        assert enum_metric.name == "service_status"
        assert enum_metric.type_ == MetricType.ENUM
        assert enum_metric._states == ["running", "stopped", "paused"]

    def test_init_with_default_state(self) -> None:
        """Test EnumMetric can be initialized with a default state."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            default="stopped",
            storage=storage,
        )
        assert enum_metric.name == "service_status"
        assert enum_metric._default == "stopped"

    def test_init_default_is_first_state(self) -> None:
        """Test that default state is first state if not specified."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            storage=storage,
        )
        assert enum_metric._default == "running"

    def test_init_with_all_metadata_fields(self) -> None:
        """Test EnumMetric can be initialized with all metadata fields."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            storage=storage,
            tags=["service:api"],
            host="localhost",
            key="service_state",
            unit="state",
            rate=1.0,
            ttl=3600,
        )
        assert enum_metric.name == "service_status"
        assert enum_metric.type_ == MetricType.ENUM
        assert enum_metric.tags == ["service:api"]
        assert enum_metric.host == "localhost"
        assert enum_metric.key == "service_state"
        assert enum_metric.unit == "state"
        assert enum_metric.rate == 1.0
        assert enum_metric.ttl == 3600


class TestEnumMetricSet:
    """Tests for EnumMetric.set() method."""

    @pytest.mark.asyncio
    async def test_set_valid_state(self) -> None:
        """Test that set() updates state for valid state."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            storage=storage,
        )

        await enum_metric.set(storage, "running")
        data = await storage.get_data()
        assert data["service_status"] == "running"

        await enum_metric.set(storage, "stopped")
        data = await storage.get_data()
        assert data["service_status"] == "stopped"

    @pytest.mark.asyncio
    async def test_set_multiple_states(self) -> None:
        """Test that set() can update state multiple times."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            storage=storage,
        )

        await enum_metric.set(storage, "running")
        await enum_metric.set(storage, "paused")
        await enum_metric.set(storage, "stopped")

        data = await storage.get_data()
        assert data["service_status"] == "stopped"

    @pytest.mark.asyncio
    async def test_set_invalid_state_raises_value_error(self) -> None:
        """Test that set() raises ValueError for invalid state."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            storage=storage,
        )

        with pytest.raises(ValueError, match="Invalid state"):
            await enum_metric.set(storage, "invalid_state")

    @pytest.mark.asyncio
    async def test_set_with_tags(self) -> None:
        """Test that set() works with tags."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            storage=storage,
            tags=["service:api"],
        )

        await enum_metric.set(storage, "running")
        data = await storage.get_data()
        assert data["service_status"] == "running"


class TestEnumMetricReset:
    """Tests for EnumMetric.reset() method."""

    @pytest.mark.asyncio
    async def test_reset_to_default_state(self) -> None:
        """Test that reset() resets to default state."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            default="paused",
            storage=storage,
        )

        await enum_metric.set(storage, "running")
        await enum_metric.reset(storage=storage)

        data = await storage.get_data()
        assert data["service_status"] == "paused"

    @pytest.mark.asyncio
    async def test_reset_to_first_state_when_no_default(self) -> None:
        """Test that reset() resets to first state when no default."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            storage=storage,
        )

        await enum_metric.set(storage, "stopped")
        await enum_metric.reset(storage=storage)

        data = await storage.get_data()
        assert data["service_status"] == "running"

    @pytest.mark.asyncio
    async def test_reset_then_set_again(self) -> None:
        """Test that enum can be set after reset."""
        storage = MemoryMonitorStorage()
        enum_metric = EnumMetric(
            name="service_status",
            states=["running", "stopped", "paused"],
            storage=storage,
        )

        await enum_metric.set(storage, "running")
        await enum_metric.reset(storage=storage)
        await enum_metric.set(storage, "paused")

        data = await storage.get_data()
        assert data["service_status"] == "paused"
