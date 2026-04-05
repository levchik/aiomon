import asyncio

from aiomon import (
    CounterMetric,
    FileMonitorOutput,
    GaugeMetric,
    JSONMonitorFormatter,
    MemoryMonitorStorage,
    MetricGroup,
    Monitor,
    PrometheusFormatter,
)


async def main():
    storage = MemoryMonitorStorage()

    # Create metrics
    class AppMetrics(MetricGroup, storage=storage):
        requests = CounterMetric("requests_total", storage=storage)
        temp = GaugeMetric("temperature", storage=storage)

    # Create multiple monitors with different formatters
    json_monitor = Monitor(
        name="json",
        storage=storage,
        formatter=JSONMonitorFormatter(),
    )

    prom_monitor = Monitor(
        name="prometheus",
        storage=storage,
        formatter=PrometheusFormatter(),
    )

    file_monitor = Monitor(
        name="file",
        storage=storage,
        formatter=JSONMonitorFormatter(),
        output=FileMonitorOutput("/tmp/metrics.json"),  # noqa: S108
    )

    # Update metrics
    await AppMetrics.requests.inc()
    await AppMetrics.temp.set(25.0)

    # Get data in different formats
    json_data = await json_monitor.format_()
    prom_data = await prom_monitor.format_()

    print(f"JSON format: {json_data}")  # noqa: T201
    print(f"\nPrometheus format:\n{prom_data}")  # noqa: T201

    # Push to file
    await file_monitor.output()
    print("\nMetrics written to /tmp/metrics.json")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
