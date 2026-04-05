import asyncio

from aiomon import (
    CounterMetric,
    GaugeMetric,
    JSONMonitorFormatter,
    MemoryMonitorStorage,
    MetricGroup,
    Monitor,
)


async def main():
    storage = MemoryMonitorStorage()

    # Define metrics as a group
    class AppMetrics(MetricGroup, storage=storage):
        requests_total = CounterMetric("requests_total", storage=storage)
        temperature = GaugeMetric("temperature", storage=storage)
        latency = GaugeMetric("latency", storage=storage)

    monitor = Monitor(
        name="myapp",
        storage=storage,
        formatter=JSONMonitorFormatter(),
    )

    # Use metrics via group
    await AppMetrics.requests_total.inc()
    await AppMetrics.temperature.set(25.0)

    data = await monitor.format_()
    print(f"Metrics: {data}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
