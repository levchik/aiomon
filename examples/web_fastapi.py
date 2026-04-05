"""
FastAPI web server with metrics endpoint.

Run with: uvicorn examples.web_fastapi:app --reload
Then visit: http://localhost:8000/metrics
"""

from fastapi import FastAPI, Response

from aiomon import (
    CounterMetric,
    GaugeMetric,
    JSONMonitorFormatter,
    MemoryMonitorStorage,
    MetricGroup,
    Monitor,
    PrometheusFormatter,
)

app = FastAPI()

# Shared storage
storage = MemoryMonitorStorage()


# Define metrics
class AppMetrics(MetricGroup, storage=storage):
    requests_total = CounterMetric("requests_total", storage=storage)
    active_connections = GaugeMetric("active_connections", storage=storage)


# Create monitors
prom_monitor = Monitor(
    name="prometheus",
    storage=storage,
    formatter=PrometheusFormatter(),
)

json_monitor = Monitor(
    name="json",
    storage=storage,
    formatter=JSONMonitorFormatter(),
)


@app.get("/")
async def root():
    """Root endpoint that increments request counter."""
    await AppMetrics.requests_total.inc()
    return {"message": "Hello World"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    data = await prom_monitor.format_()
    return Response(content=data, media_type="text/plain")


@app.get("/health")
async def health():
    """Health check endpoint with JSON metrics."""
    data = await json_monitor.format_()
    return {"status": "healthy", "metrics": data}


@app.post("/increment")
async def increment():
    """Manually increment counter."""
    await AppMetrics.requests_total.inc()
    return {"status": "ok"}
