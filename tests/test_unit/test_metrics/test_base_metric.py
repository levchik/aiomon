"""Unit tests for BaseMetric class."""

import time
from typing import cast

from aiomon.impl.metrics import BaseMetric


class ConcreteMetric(BaseMetric):
    """Concrete implementation of BaseMetric for testing purposes."""

    type_ = None  # type: ignore

    def __init__(
        self,
        name: str,
        tags: list[str] | None = None,
        host: str | None = None,
        key: str | None = None,
        unit: str | None = None,
        rate: float | None = None,
        ttl: int | None = None,
        timestamp: float | None = None,
    ) -> None:
        super().__init__(
            name=name,
            tags=tags,
            host=host,
            key=key,
            unit=unit,
            rate=rate,
            ttl=ttl,
            timestamp=timestamp,
        )


class TestBaseMetricMinimalInitialization:
    """Tests for minimal initialization with only name parameter."""

    def test_minimal_init_name_only(self) -> None:
        """Test that BaseMetric can be initialized with only name."""
        metric = ConcreteMetric(name="test_metric")
        assert metric.name == "test_metric"

    def test_minimal_init_tags_default_none(self) -> None:
        """Test that tags defaults to None when not provided."""
        metric = ConcreteMetric(name="test_metric")
        assert metric.tags is None

    def test_minimal_init_host_default_none(self) -> None:
        """Test that host defaults to None when not provided."""
        metric = ConcreteMetric(name="test_metric")
        assert metric.host is None

    def test_minimal_init_key_default_none(self) -> None:
        """Test that key defaults to None when not provided."""
        metric = ConcreteMetric(name="test_metric")
        assert metric.key is None

    def test_minimal_init_unit_default_none(self) -> None:
        """Test that unit defaults to None when not provided."""
        metric = ConcreteMetric(name="test_metric")
        assert metric.unit is None

    def test_minimal_init_rate_default_none(self) -> None:
        """Test that rate defaults to None when not provided."""
        metric = ConcreteMetric(name="test_metric")
        assert metric.rate is None

    def test_minimal_init_ttl_default_none(self) -> None:
        """Test that ttl defaults to None when not provided."""
        metric = ConcreteMetric(name="test_metric")
        assert metric.ttl is None

    def test_minimal_init_timestamp_auto_generated(self) -> None:
        """Test that timestamp is auto-generated when not provided."""
        before = time.time()
        metric = ConcreteMetric(name="test_metric")
        after = time.time()

        assert metric.timestamp is not None
        assert before <= cast(float, metric.timestamp) <= after


class TestBaseMetricFullInitialization:
    """Tests for full initialization with all metadata fields."""

    def test_full_init_all_fields(self) -> None:
        """Test that BaseMetric can be initialized with all fields."""
        timestamp = time.time()
        metric = ConcreteMetric(
            name="test_metric",
            tags=["tag1", "tag2"],
            host="localhost",
            key="metric_key",
            unit="seconds",
            rate=1.5,
            ttl=3600,
            timestamp=timestamp,
        )
        assert metric.name == "test_metric"
        assert metric.tags == ["tag1", "tag2"]
        assert metric.host == "localhost"
        assert metric.key == "metric_key"
        assert metric.unit == "seconds"
        assert metric.rate == 1.5
        assert metric.ttl == 3600
        assert metric.timestamp == timestamp

    def test_full_init_with_tags_only(self) -> None:
        """Test initialization with name and tags only."""
        before = time.time()
        metric = ConcreteMetric(
            name="test_metric",
            tags=["env:prod"],
        )
        after = time.time()
        assert metric.name == "test_metric"
        assert metric.tags == ["env:prod"]
        assert metric.host is None
        assert metric.key is None
        assert metric.unit is None
        assert metric.rate is None
        assert metric.ttl is None
        assert metric.timestamp is not None
        assert before <= cast(float, metric.timestamp) <= after

    def test_full_init_with_host_only(self) -> None:
        """Test initialization with name and host only."""
        metric = ConcreteMetric(
            name="test_metric",
            host="server1.example.com",
        )
        assert metric.name == "test_metric"
        assert metric.host == "server1.example.com"
        assert metric.tags is None
        assert metric.key is None

    def test_full_init_with_key_only(self) -> None:
        """Test initialization with name and key only."""
        metric = ConcreteMetric(
            name="test_metric",
            key="custom_key",
        )
        assert metric.name == "test_metric"
        assert metric.key == "custom_key"
        assert metric.host is None

    def test_full_init_with_unit_only(self) -> None:
        """Test initialization with name and unit only."""
        metric = ConcreteMetric(
            name="test_metric",
            unit="bytes",
        )
        assert metric.name == "test_metric"
        assert metric.unit == "bytes"
        assert metric.host is None
        assert metric.key is None

    def test_full_init_with_rate_only(self) -> None:
        """Test initialization with name and rate only."""
        metric = ConcreteMetric(
            name="test_metric",
            rate=0.5,
        )
        assert metric.name == "test_metric"
        assert metric.rate == 0.5
        assert metric.host is None
        assert metric.key is None

    def test_full_init_with_ttl_only(self) -> None:
        """Test initialization with name and ttl only."""
        metric = ConcreteMetric(
            name="test_metric",
            ttl=7200,
        )
        assert metric.name == "test_metric"
        assert metric.ttl == 7200
        assert metric.host is None
        assert metric.key is None

    def test_full_init_with_timestamp_only(self) -> None:
        """Test initialization with name and timestamp only."""
        timestamp = 1234567890.0
        metric = ConcreteMetric(
            name="test_metric",
            timestamp=timestamp,
        )
        assert metric.name == "test_metric"
        assert metric.timestamp == timestamp
        assert metric.host is None
        assert metric.key is None


class TestBaseMetricTimestampAutoGeneration:
    """Tests for automatic timestamp generation."""

    def test_timestamp_auto_generated_when_not_provided(self) -> None:
        """Test that timestamp is auto-generated when not provided."""
        before = time.time()
        metric = ConcreteMetric(name="test_metric")
        after = time.time()

        assert metric.timestamp is not None
        assert before <= cast(float, metric.timestamp) <= after

    def test_timestamp_not_overwritten_when_provided(self) -> None:
        """Test that provided timestamp is not overwritten."""
        custom_timestamp = 1234567890.0
        metric = ConcreteMetric(
            name="test_metric",
            timestamp=custom_timestamp,
        )
        assert metric.timestamp == custom_timestamp

    def test_timestamp_auto_generation_is_close_to_current_time(self) -> None:
        """Test that auto-generated timestamp is close to current time."""
        before = time.time()
        metric = ConcreteMetric(name="test_metric")
        after = time.time()

        assert metric.timestamp is not None
        # Allow some tolerance for test execution time
        assert abs(cast(float, metric.timestamp) - before) < 1.0
        assert abs(cast(float, metric.timestamp) - after) < 1.0
