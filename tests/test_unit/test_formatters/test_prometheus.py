"""Tests for PrometheusFormatter."""

from aiomon import (
    CounterMetric,
    EnumMetric,
    GaugeMetric,
    HistogramMetric,
    InfoMetric,
    MemoryMonitorStorage,
    MonitorOutputData,
    MonitorOutputItem,
    PrometheusFormatter,
    SummaryMetric,
)


class TestPrometheusFormatter:
    def test_format_counter(self) -> None:
        """Test formatting counter metric."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=CounterMetric("requests_total", storage=storage),
                value=100,
            )
        ]

        result = formatter.format_(metrics)

        assert "# HELP requests_total requests_total metric" in result
        assert "# TYPE requests_total counter" in result
        assert "requests_total 100" in result

    def test_format_gauge(self) -> None:
        """Test formatting gauge metric."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=GaugeMetric("temperature", storage=storage),
                value=25.5,
            )
        ]

        result = formatter.format_(metrics)

        assert "# HELP temperature temperature metric" in result
        assert "# TYPE temperature gauge" in result
        assert "temperature 25.5" in result

    def test_format_gauge_with_labels(self) -> None:
        """Test formatting gauge metric with labels."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=GaugeMetric(
                    "temperature",
                    storage=storage,
                    tags=["location:datacenter"],
                ),
                value=25.5,
            )
        ]

        result = formatter.format_(metrics)

        assert 'temperature{location="datacenter"} 25.5' in result

    def test_format_gauge_with_host_label(self) -> None:
        """Test formatting gauge metric with host label."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=GaugeMetric(
                    "cpu_usage", storage=storage, host="server1"
                ),
                value=75.0,
            )
        ]

        result = formatter.format_(metrics)

        assert 'cpu_usage{host="server1"} 75.0' in result

    def test_format_gauge_with_multiple_labels(self) -> None:
        """Test formatting gauge metric with multiple labels."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=GaugeMetric(
                    "memory_usage",
                    storage=storage,
                    tags=["env:production", "region:us-east"],
                    host="server1",
                ),
                value=8192.0,
            )
        ]

        result = formatter.format_(metrics)

        assert "memory_usage{" in result
        assert 'env="production"' in result
        assert 'region="us-east"' in result
        assert 'host="server1"' in result

    def test_format_histogram(self) -> None:
        """Test formatting histogram metric."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        histogram = HistogramMetric("request_duration", storage=storage)
        histogram_data = {
            "buckets": {0.1: 5, 0.5: 10, 1.0: 15, float("inf"): 20},
            "sum": 12.5,
            "count": 20,
        }

        metrics: MonitorOutputData = [
            MonitorOutputItem(metric=histogram, value=histogram_data)
        ]

        result = formatter.format_(metrics)

        assert "# TYPE request_duration histogram" in result
        assert 'request_duration_bucket{le="0.1"} 5' in result
        assert 'request_duration_bucket{le="0.5"} 10' in result
        assert 'request_duration_bucket{le="1.0"} 15' in result
        assert 'request_duration_bucket{le="inf"} 20' in result
        assert "request_duration_sum 12.5" in result
        assert "request_duration_count 20" in result

    def test_format_summary(self) -> None:
        """Test formatting summary metric."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        summary = SummaryMetric("response_time", storage=storage)
        summary_data = {
            "quantiles": {0.5: 100.0, 0.9: 200.0, 0.99: 500.0},
            "sum": 1500.0,
            "count": 10,
        }

        metrics: MonitorOutputData = [
            MonitorOutputItem(metric=summary, value=summary_data)
        ]

        result = formatter.format_(metrics)

        assert "# TYPE response_time summary" in result
        assert 'response_time{quantile="0.5"} 100.0' in result
        assert 'response_time{quantile="0.9"} 200.0' in result
        assert 'response_time{quantile="0.99"} 500.0' in result
        assert "response_time_sum 1500.0" in result
        assert "response_time_count 10" in result

    def test_format_multiple_metrics(self) -> None:
        """Test formatting multiple metrics."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=CounterMetric("requests_total", storage=storage),
                value=100,
            ),
            MonitorOutputItem(
                metric=GaugeMetric("temperature", storage=storage),
                value=25.5,
            ),
        ]

        result = formatter.format_(metrics)

        # Check counter
        assert "# HELP requests_total requests_total metric" in result
        assert "# TYPE requests_total counter" in result
        assert "requests_total 100" in result

        # Check gauge
        assert "# HELP temperature temperature metric" in result
        assert "# TYPE temperature gauge" in result
        assert "temperature 25.5" in result

    def test_format_info_metric(self) -> None:
        """Test formatting info metric (mapped to gauge)."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=InfoMetric("app_info", storage=storage),
                value=1,
            )
        ]

        result = formatter.format_(metrics)

        assert "# TYPE app_info gauge" in result
        assert "app_info 1" in result

    def test_format_enum_metric(self) -> None:
        """Test formatting enum metric (mapped to gauge)."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=EnumMetric(
                    "state", storage=storage, states=["running", "stopped"]
                ),
                value=0,
            )
        ]

        result = formatter.format_(metrics)

        assert "# TYPE state gauge" in result
        assert "state 0" in result

    def test_format_output_ends_with_newline(self) -> None:
        """Test that formatted output ends with a newline."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        metrics: MonitorOutputData = [
            MonitorOutputItem(
                metric=CounterMetric("requests_total", storage=storage),
                value=100,
            )
        ]

        result = formatter.format_(metrics)

        assert result.endswith("\n")

    def test_format_histogram_with_empty_buckets(self) -> None:
        """Test formatting histogram with empty buckets dict."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        histogram = HistogramMetric("request_duration", storage=storage)
        histogram_data = {
            "buckets": {},
            "sum": 0,
            "count": 0,
        }

        metrics: MonitorOutputData = [
            MonitorOutputItem(metric=histogram, value=histogram_data)
        ]

        result = formatter.format_(metrics)

        assert "# TYPE request_duration histogram" in result
        assert "request_duration_sum 0" in result
        assert "request_duration_count 0" in result

    def test_format_summary_with_empty_quantiles(self) -> None:
        """Test formatting summary with empty quantiles dict."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        summary = SummaryMetric("response_time", storage=storage)
        summary_data = {
            "quantiles": {},
            "sum": 0,
            "count": 0,
        }

        metrics: MonitorOutputData = [
            MonitorOutputItem(metric=summary, value=summary_data)
        ]

        result = formatter.format_(metrics)

        assert "# TYPE response_time summary" in result
        assert "response_time_sum 0" in result
        assert "response_time_count 0" in result

    def test_format_histogram_without_value_dict(self) -> None:
        """Test formatting histogram when value is not a dict."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        histogram = HistogramMetric("request_duration", storage=storage)

        metrics: MonitorOutputData = [
            MonitorOutputItem(metric=histogram, value=100)  # type: ignore[assignment]
        ]

        result = formatter.format_(metrics)

        # Should fall back to default formatting
        assert "# TYPE request_duration histogram" in result

    def test_format_summary_without_value_dict(self) -> None:
        """Test formatting summary when value is not a dict."""
        formatter = PrometheusFormatter()
        storage = MemoryMonitorStorage()

        summary = SummaryMetric("response_time", storage=storage)

        metrics: MonitorOutputData = [
            MonitorOutputItem(metric=summary, value=100)  # type: ignore[assignment]
        ]

        result = formatter.format_(metrics)

        # Should fall back to default formatting
        assert "# TYPE response_time summary" in result
