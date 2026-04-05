# aiomon Examples

This directory contains example usage of aiomon for different scenarios.

## Examples

### Basic Usage
- [`basic_usage.py`](basic_usage.py) - Simplest possible usage with Counter and Gauge metrics

### Metric Groups
- [`metric_group.py`](metric_group.py) - Using MetricGroup for organized metric definitions

### Multiple Outputs
- [`multiple_outputs.py`](multiple_outputs.py) - Multiple monitors sharing storage with different formatters

### Web Integration
- [`web_fastapi.py`](web_fastapi.py) - FastAPI web server with /metrics endpoint

## Running Examples

```bash
# Basic usage
python examples/basic_usage.py

# Metric group
python examples/metric_group.py

# Multiple outputs
python examples/multiple_outputs.py

# Web server (requires FastAPI and uvicorn)
pip install fastapi uvicorn
uvicorn examples.web_fastapi:app --reload
```

Then visit:
- http://localhost:8000/ - Root endpoint
- http://localhost:8000/metrics - Prometheus metrics
- http://localhost:8000/health - Health check with JSON metrics
