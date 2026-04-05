"""Tests for UniqueMetricsDict."""

import pytest

from aiomon.impl.metrics.counter import CounterMetric
from aiomon.impl.metrics.gauge import GaugeMetric
from aiomon.impl.storages.memory import MemoryMonitorStorage
from aiomon.impl.types import UniqueMetricsDict


class TestUniqueMetricsDict:
    """Tests for UniqueMetricsDict class."""

    def test_setitem_adds_new_key(self) -> None:
        """Test that setitem adds a new key successfully."""
        metrics_dict = UniqueMetricsDict()
        storage = MemoryMonitorStorage()
        metric = GaugeMetric(name="test_metric", storage=storage)

        metrics_dict["test_metric"] = metric

        assert "test_metric" in metrics_dict
        assert metrics_dict["test_metric"] == metric

    def test_setitem_raises_on_duplicate_key(self) -> None:
        """Test that setitem raises KeyError when key already exists."""
        metrics_dict = UniqueMetricsDict()
        storage = MemoryMonitorStorage()
        metric1 = GaugeMetric(name="test_metric", storage=storage)
        metric2 = CounterMetric(name="test_metric", storage=storage)

        metrics_dict["test_metric"] = metric1

        with pytest.raises(KeyError, match="Key test_metric already exists"):
            metrics_dict["test_metric"] = metric2

    def test_setitem_multiple_unique_keys(self) -> None:
        """Test that setitem works with multiple unique keys."""
        metrics_dict = UniqueMetricsDict()
        storage = MemoryMonitorStorage()
        metric1 = CounterMetric(name="requests", storage=storage)
        metric2 = GaugeMetric(name="temperature", storage=storage)
        metric3 = GaugeMetric(name="latency", storage=storage)

        metrics_dict["requests"] = metric1
        metrics_dict["temperature"] = metric2
        metrics_dict["latency"] = metric3

        assert len(metrics_dict) == 3
        assert metrics_dict["requests"].name == "requests"
        assert metrics_dict["temperature"].name == "temperature"
        assert metrics_dict["latency"].name == "latency"

    def test_inherits_from_dict(self) -> None:
        """Test that UniqueMetricsDict inherits from dict."""
        metrics_dict = UniqueMetricsDict()
        storage = MemoryMonitorStorage()
        metric = GaugeMetric(name="test", storage=storage)

        metrics_dict["test"] = metric

        # Test dict methods work
        assert "test" in metrics_dict
        assert len(metrics_dict) == 1
        assert list(metrics_dict.keys()) == ["test"]
        assert list(metrics_dict.values()) == [metric]
        assert list(metrics_dict.items()) == [("test", metric)]

    def test_getitem_returns_value(self) -> None:
        """Test that getitem returns the stored metric."""
        metrics_dict = UniqueMetricsDict()
        storage = MemoryMonitorStorage()
        metric = GaugeMetric(name="test_metric", storage=storage)

        metrics_dict["test_metric"] = metric

        assert metrics_dict["test_metric"] is metric

    def test_getitem_raises_on_missing_key(self) -> None:
        """Test that getitem raises KeyError for missing key."""
        metrics_dict = UniqueMetricsDict()

        with pytest.raises(KeyError):
            _ = metrics_dict["nonexistent"]
