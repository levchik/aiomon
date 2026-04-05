import io
import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from aiomon.impl.outputs.stderr import StderrMonitorOutput


class TestStderrMonitorOutput:
    """Tests for StderrMonitorOutput."""

    @pytest.mark.asyncio
    async def test_write_string(self) -> None:
        """Test writing string formatted metrics."""
        output = StderrMonitorOutput()
        captured = io.StringIO()

        with patch.object(sys, "stderr", captured):
            await output.write('metric_value{label="test"} 42')

        assert captured.getvalue() == 'metric_value{label="test"} 42\n'

    @pytest.mark.asyncio
    async def test_write_bytes(self) -> None:
        """Test writing bytes formatted metrics."""
        output = StderrMonitorOutput()
        captured = io.BytesIO()
        mock_stderr = MagicMock()
        mock_stderr.buffer = captured

        # Track write calls to capture the newline
        newline_captured = io.BytesIO()

        def write_side_effect(data: str | bytes) -> None:
            if isinstance(data, str):
                newline_captured.write(data.encode())
            else:
                newline_captured.write(data)

        mock_stderr.write = write_side_effect  # type: ignore[method-assign]

        with patch.object(sys, "stderr", mock_stderr):
            await output.write(b'metric_value{label="test"} 42')

        # Combine buffer writes and stderr writes
        result = captured.getvalue() + newline_captured.getvalue()
        assert result == b'metric_value{label="test"} 42\n'

    @pytest.mark.asyncio
    async def test_write_appends_newline(self) -> None:
        """Test that newline is appended to output."""
        output = StderrMonitorOutput()
        captured = io.StringIO()

        with patch.object(sys, "stderr", captured):
            await output.write("test_metric 123")

        assert captured.getvalue().endswith("\n")

    @pytest.mark.asyncio
    async def test_write_flushes_stream(self) -> None:
        """Test that stderr is flushed after writing."""
        output = StderrMonitorOutput()
        mock_stderr = MagicMock()

        with patch.object(sys, "stderr", mock_stderr):
            await output.write("test_metric 123")

        mock_stderr.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_list_of_dicts(self) -> None:
        """Test writing list[dict] formatted metrics as JSON."""
        output = StderrMonitorOutput()
        captured = io.StringIO()
        metrics = [
            {"name": "requests", "value": 100},
            {"name": "temperature", "value": 25.5},
        ]

        with patch.object(sys, "stderr", captured):
            await output.write(metrics)

        result = captured.getvalue()
        parsed = json.loads(result.strip())
        assert parsed == metrics

    @pytest.mark.asyncio
    async def test_write_invalid_type_raises_typeerror(self) -> None:
        """Test that writing invalid type raises TypeError."""
        output = StderrMonitorOutput()

        error_match = r"formatted_metrics must be bytes, str, or list\[dict\]"

        with pytest.raises(TypeError, match=error_match):
            await output.write(123)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match=error_match):
            await output.write({"key": "value"})  # type: ignore[arg-type]

        with pytest.raises(TypeError, match=error_match):
            await output.write(None)  # type: ignore[arg-type]
