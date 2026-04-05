# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Complete rewrite with Pull/Push architecture support
- Multiple metric types: `CounterMetric`, `GaugeMetric`, `HistogramMetric`, `SummaryMetric`, `StateMetric`
- `MetricGroup` for declarative, type-safe metric definitions
- `MemoryMonitorStorage` with atomic `modify()` and metadata storage
- Formatters: `JSONMonitorFormatter`, `PrometheusFormatter`
- Outputs: `StdoutMonitorOutput`, `StderrMonitorOutput`, `FileMonitorOutput`
- Generic `Monitor` and `MonitorFormatter` types
- Type safety test suite with pytest-mypy-plugins
- Integration and unit test coverage

### Changed

- Metrics auto-register with storage (no more `add_metric()`)
- `Monitor` no longer requires output/formatter at construction
- Storage holds metric metadata (no separate registry)

### Removed

- `InfoMetric` (replaced by richer metric types)
- Direct `Monitor.output()` (use outputs explicitly)

## [0.0.1] - 2024-03-28

### Added

- Initial release: async healthcheck monitoring with JSON output
- `BaseMetric` and `InfoMetric` types
- `Monitor` with `add_metric()` and `metric()` API
- `JSONMonitorFormatter` for JSON serialization
- `FileMonitorOutput` for writing metrics to files
- `MemoryMonitorStorage` for in-memory metric storage
- Type-safe base classes and protocols
- CI/CD with pytest, coverage, mypy, ruff, and black
