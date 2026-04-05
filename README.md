# aiomon

[![PyPI - Version](https://img.shields.io/pypi/v/aiomon.svg)](https://pypi.org/project/aiomon)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aiomon.svg)](https://pypi.org/project/aiomon)

A lightweight, async Python library for metrics and healthchecks with a uniform interface across all monitoring backends. Define metrics once, output anywhere — JSON, Prometheus format, files, stdout, or push to external systems. Supports both push (send to monitoring services) and pull (expose scrape endpoints) architectures.

-----

**Table of Contents**

- [Installation](#installation)
- [Development](#development)
- [License](#license)

## Installation

```console
pip install aiomon
```

## Examples

### Basic Usage

```python
import asyncio
from aiomon import Monitor, CounterMetric, GaugeMetric, JSONMonitorFormatter, MemoryMonitorStorage

async def main():
    storage = MemoryMonitorStorage()

    # Create metrics (they auto-register with storage)
    requests = CounterMetric("requests_total", storage=storage)
    temperature = GaugeMetric("temperature", storage=storage)

    # Create monitor
    monitor = Monitor(
        name="myapp",
        storage=storage,
        formatter=JSONMonitorFormatter(),
    )

    # Use metrics (storage is used automatically)
    await requests.inc()
    await temperature.set(25.0)

    # Get formatted output
    data = await monitor.format_()
    print(data)  # [{"name": "requests_total", "value": 1, ...}, ...]

asyncio.run(main())
```

### Using MetricGroup

```python
import asyncio
from aiomon import MetricGroup, CounterMetric, GaugeMetric, MemoryMonitorStorage

async def main():
    storage = MemoryMonitorStorage()

    class AppMetrics(MetricGroup, storage=storage):
        requests = CounterMetric("requests_total", storage=storage)
        temp = GaugeMetric("temperature", storage=storage)

    # Type-safe access (storage is bound automatically)
    await AppMetrics.requests.inc()
    await AppMetrics.temp.set(25.0)

asyncio.run(main())
```

### Web Server (FastAPI)

```python
from fastapi import FastAPI, Response
from aiomon import Monitor, MetricGroup, CounterMetric, PrometheusFormatter, MemoryMonitorStorage

app = FastAPI()
storage = MemoryMonitorStorage()

class AppMetrics(MetricGroup, storage=storage):
    requests_total = CounterMetric("requests_total", storage=storage)

@app.get("/")
async def root():
    await AppMetrics.requests_total.inc()
    return {"message": "Hello World"}

@app.get("/metrics")
async def metrics():
    monitor = Monitor("app", storage, PrometheusFormatter())
    data = await monitor.format_()
    return Response(content=data, media_type="text/plain")
```

### More Examples

See the [`examples/`](examples/) directory for complete working examples including:
- Basic usage
- Metric groups
- Multiple outputs (JSON, Prometheus, File)
- Web server integration with FastAPI

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and task running.

```console
# Sync dependencies
uv sync --extra dev

# Run tests with coverage
uv run coverage run -m pytest tests typesafety && uv run coverage report

# Run tests with XML coverage report
uv run coverage run -m pytest tests typesafety && uv run coverage xml

# Run linting
uv run ruff check . && uv run black --check . && uv run mypy src/aiomon tests

# Run formatting
uv run ruff check --fix . && uv run black .
```

## License

`aiomon` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
