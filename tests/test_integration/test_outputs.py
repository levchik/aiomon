"""Integration tests for different monitor output types."""

import json
import os

import pytest

from aiomon import (
    CounterMetric,
    EnumMetric,
    FileMonitorOutput,
    GaugeMetric,
    HistogramMetric,
    InfoMetric,
    JSONMonitorFormatter,
    MemoryMonitorStorage,
    Monitor,
    StderrMonitorOutput,
    StdoutMonitorOutput,
    SummaryMetric,
)


@pytest.fixture
def temp_file_path(tmp_path) -> str:
    """Provide a temporary file path for testing."""
    return str(tmp_path / "test_metrics.json")


class TestFileMonitorOutput:
    """Test FileMonitorOutput with all metric types."""

    @pytest.mark.asyncio
    async def test_file_output_with_all_metrics(
        self, temp_file_path: str
    ) -> None:
        """Test FileMonitorOutput writes all metrics to file."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        output = FileMonitorOutput(path=temp_file_path)

        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
            output=output,
        )

        # Create metrics with storage
        counter = CounterMetric("requests", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)
        histogram = HistogramMetric("latency", storage=storage)
        summary = SummaryMetric("response_time", storage=storage)
        enum_metric = EnumMetric(
            "state", states=["up", "down"], storage=storage
        )
        info = InfoMetric("info", storage=storage)

        # Update values
        await counter.inc(storage)
        await gauge.set(storage, 25.0)
        await histogram.observe(storage, 0.5)
        await summary.observe(storage, 0.3)
        await enum_metric.set(storage, "up")
        await info.set_(storage, {"version": "1.0"})

        # Write output
        await monitor.output()

        # Verify file was created and contains correct data
        assert os.path.exists(temp_file_path)

        with open(temp_file_path) as f:
            content = f.read()
            data = json.loads(content)

        assert len(data) == 6

        # Create a map for easier assertions
        metrics_map = {item["name"]: item for item in data}

        # Verify each metric type
        assert metrics_map["requests"]["type"] == "counter"
        assert metrics_map["requests"]["value"] == 1

        assert metrics_map["temperature"]["type"] == "gauge"
        assert metrics_map["temperature"]["value"] == 25.0

        assert metrics_map["latency"]["type"] == "histogram"

        assert metrics_map["response_time"]["type"] == "summary"

        assert metrics_map["state"]["type"] == "enum"
        assert metrics_map["state"]["value"] == "up"

        assert metrics_map["info"]["type"] == "info"
        assert metrics_map["info"]["value"] == {"version": "1.0"}

        # Cleanup
        os.remove(temp_file_path)

    @pytest.mark.asyncio
    async def test_file_output_with_single_metric(
        self, temp_file_path: str
    ) -> None:
        """Test FileMonitorOutput with a single metric."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        output = FileMonitorOutput(path=temp_file_path)

        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
            output=output,
        )

        counter = CounterMetric("requests", storage=storage)
        await counter.inc(storage)

        await monitor.output()

        with open(temp_file_path) as f:
            content = f.read()
            data = json.loads(content)

        assert len(data) == 1
        assert data[0]["name"] == "requests"
        assert data[0]["value"] == 1

        # Cleanup
        os.remove(temp_file_path)


class TestStdoutMonitorOutput:
    """Test StdoutMonitorOutput with all metric types."""

    @pytest.mark.asyncio
    async def test_stdout_output_with_all_metrics(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test StdoutMonitorOutput writes all metrics to stdout."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        output = StdoutMonitorOutput()

        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
            output=output,
        )

        # Create metrics with storage
        counter = CounterMetric("requests", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)
        histogram = HistogramMetric("latency", storage=storage)
        summary = SummaryMetric("response_time", storage=storage)
        enum_metric = EnumMetric(
            "state", states=["up", "down"], storage=storage
        )
        info = InfoMetric("info", storage=storage)

        # Update values
        await counter.inc(storage)
        await gauge.set(storage, 25.0)
        await histogram.observe(storage, 0.5)
        await summary.observe(storage, 0.3)
        await enum_metric.set(storage, "up")
        await info.set_(storage, {"version": "1.0"})

        # Write output
        await monitor.output()

        # Verify stdout contains correct data
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 6

        # Create a map for easier assertions
        metrics_map = {item["name"]: item for item in data}

        # Verify each metric type
        assert metrics_map["requests"]["type"] == "counter"
        assert metrics_map["requests"]["value"] == 1

        assert metrics_map["temperature"]["type"] == "gauge"
        assert metrics_map["temperature"]["value"] == 25.0

        assert metrics_map["latency"]["type"] == "histogram"

        assert metrics_map["response_time"]["type"] == "summary"

        assert metrics_map["state"]["type"] == "enum"
        assert metrics_map["state"]["value"] == "up"

        assert metrics_map["info"]["type"] == "info"
        assert metrics_map["info"]["value"] == {"version": "1.0"}

    @pytest.mark.asyncio
    async def test_stdout_output_with_single_metric(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test StdoutMonitorOutput with a single metric."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        output = StdoutMonitorOutput()

        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
            output=output,
        )

        counter = CounterMetric("requests", storage=storage)
        await counter.inc(storage)

        await monitor.output()

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 1
        assert data[0]["name"] == "requests"
        assert data[0]["value"] == 1


class TestStderrMonitorOutput:
    """Test StderrMonitorOutput with all metric types."""

    @pytest.mark.asyncio
    async def test_stderr_output_with_all_metrics(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test StderrMonitorOutput writes all metrics to stderr."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        output = StderrMonitorOutput()

        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
            output=output,
        )

        # Create metrics with storage
        counter = CounterMetric("requests", storage=storage)
        gauge = GaugeMetric("temperature", storage=storage)
        histogram = HistogramMetric("latency", storage=storage)
        summary = SummaryMetric("response_time", storage=storage)
        enum_metric = EnumMetric(
            "state", states=["up", "down"], storage=storage
        )
        info = InfoMetric("info", storage=storage)

        # Update values
        await counter.inc(storage)
        await gauge.set(storage, 25.0)
        await histogram.observe(storage, 0.5)
        await summary.observe(storage, 0.3)
        await enum_metric.set(storage, "up")
        await info.set_(storage, {"version": "1.0"})

        # Write output
        await monitor.output()

        # Verify stderr contains correct data
        captured = capsys.readouterr()
        data = json.loads(captured.err)

        assert len(data) == 6

        # Create a map for easier assertions
        metrics_map = {item["name"]: item for item in data}

        # Verify each metric type
        assert metrics_map["requests"]["type"] == "counter"
        assert metrics_map["requests"]["value"] == 1

        assert metrics_map["temperature"]["type"] == "gauge"
        assert metrics_map["temperature"]["value"] == 25.0

        assert metrics_map["latency"]["type"] == "histogram"

        assert metrics_map["response_time"]["type"] == "summary"

        assert metrics_map["state"]["type"] == "enum"
        assert metrics_map["state"]["value"] == "up"

        assert metrics_map["info"]["type"] == "info"
        assert metrics_map["info"]["value"] == {"version": "1.0"}

    @pytest.mark.asyncio
    async def test_stderr_output_with_single_metric(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test StderrMonitorOutput with a single metric."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        output = StderrMonitorOutput()

        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
            output=output,
        )

        counter = CounterMetric("requests", storage=storage)
        await counter.inc(storage)

        await monitor.output()

        captured = capsys.readouterr()
        data = json.loads(captured.err)

        assert len(data) == 1
        assert data[0]["name"] == "requests"
        assert data[0]["value"] == 1


class TestOutputCombinations:
    """Test different output combinations and scenarios."""

    @pytest.mark.asyncio
    async def test_multiple_outputs_same_metrics(
        self, temp_file_path: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test writing same metrics to multiple outputs."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()

        # Create monitor with stdout output
        stdout_output = StdoutMonitorOutput()
        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
            output=stdout_output,
        )

        counter = CounterMetric("requests", storage=storage)
        await counter.inc(storage)

        await monitor.output()

        # Verify stdout
        captured = capsys.readouterr()
        stdout_data = json.loads(captured.out)
        assert len(stdout_data) == 1

        # Create monitor with file output
        storage2: MemoryMonitorStorage = MemoryMonitorStorage()
        file_output = FileMonitorOutput(path=temp_file_path)
        monitor2 = Monitor(
            name="test",
            storage=storage2,
            formatter=formatter,
            output=file_output,
        )

        counter2 = CounterMetric("requests", storage=storage2)
        await counter2.inc(storage2)

        await monitor2.output()

        # Verify file
        with open(temp_file_path) as f:
            file_content = f.read()
            file_data = json.loads(file_content)

        assert len(file_data) == 1

        # Both outputs should have same data
        assert stdout_data[0]["name"] == file_data[0]["name"]
        assert stdout_data[0]["value"] == file_data[0]["value"]

        # Cleanup
        os.remove(temp_file_path)

    @pytest.mark.asyncio
    async def test_output_with_metadata_fields(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test output includes metadata fields when specified."""
        storage: MemoryMonitorStorage = MemoryMonitorStorage()
        formatter = JSONMonitorFormatter()
        output = StdoutMonitorOutput()

        monitor = Monitor(
            name="test",
            storage=storage,
            formatter=formatter,
            output=output,
        )

        # Add metric with metadata
        counter = CounterMetric(
            "requests",
            storage=storage,
            tags=["method:GET"],
            host="localhost",
            unit="requests",
        )
        await counter.inc(storage)

        await monitor.output()

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 1
        assert data[0]["name"] == "requests"
        assert data[0]["tags"] == ["method:GET"]
        assert data[0]["host"] == "localhost"
        assert data[0]["unit"] == "requests"
