import asyncio

from aiomon import (
    CounterMetric,
    GaugeMetric,
    JSONMonitorFormatter,
    MemoryMonitorStorage,
    Monitor,
)


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
    print(f"Metrics: {data}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
