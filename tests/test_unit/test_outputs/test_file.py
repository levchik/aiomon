"""Tests for FileMonitorOutput."""

import json
import os
import tempfile

import pytest

from aiomon.impl.outputs.file import FileMonitorOutput


class TestFileMonitorOutput:
    """Tests for FileMonitorOutput class."""

    @pytest.mark.asyncio
    async def test_write_string(self) -> None:
        """Test writing string metrics to file."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as f:
            temp_path = f.name

        try:
            output = FileMonitorOutput(temp_path)
            await output.write("test_metric 123")

            with open(temp_path) as f:
                content = f.read()

            assert content == "test_metric 123"
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_write_bytes(self) -> None:
        """Test writing bytes metrics to file."""
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".bin"
        ) as f:
            temp_path = f.name

        try:
            output = FileMonitorOutput(temp_path)
            await output.write(b"test_metric 456")

            with open(temp_path, "rb") as f:
                content = f.read()

            assert content == b"test_metric 456"
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_write_list_of_dicts(self) -> None:
        """Test writing list[dict] metrics to file as JSON."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as f:
            temp_path = f.name

        try:
            output = FileMonitorOutput(temp_path)
            metrics = [
                {"name": "requests", "value": 100},
                {"name": "temperature", "value": 25.5},
            ]
            await output.write(metrics)

            with open(temp_path) as f:
                content = f.read()

            # Should be serialized as JSON
            parsed = json.loads(content)
            assert parsed == metrics
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_write_invalid_type_raises_typeerror(self) -> None:
        """Test writing invalid type raises TypeError."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as f:
            temp_path = f.name

        try:
            output = FileMonitorOutput(temp_path)

            error_match = (
                r"formatted_metrics must be bytes, str, or list\[dict\]"
            )

            with pytest.raises(TypeError, match=error_match):
                await output.write(123)  # type: ignore[arg-type]

            with pytest.raises(TypeError, match=error_match):
                await output.write({"key": "value"})  # type: ignore[arg-type]

            with pytest.raises(TypeError, match=error_match):
                await output.write(None)  # type: ignore[arg-type]
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_write_preserves_file_path(self) -> None:
        """Test FileMonitorOutput preserves file path."""
        output = FileMonitorOutput("/tmp/test_metrics.txt")  # noqa: S108
        assert output.path == "/tmp/test_metrics.txt"  # noqa: S108

    @pytest.mark.asyncio
    async def test_write_overwrites_existing_file(self) -> None:
        """Test write overwrites existing file content."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as f:
            temp_path = f.name
            f.write("original content")

        try:
            output = FileMonitorOutput(temp_path)
            await output.write("new content")

            with open(temp_path) as f:
                content = f.read()

            assert content == "new content"
            assert "original content" not in content
        finally:
            os.unlink(temp_path)
