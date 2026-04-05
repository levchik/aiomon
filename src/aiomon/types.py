from enum import StrEnum


class MetricType(StrEnum):
    COUNTER = "counter"
    GAUGE = "gauge"
    SUMMARY = "summary"
    HISTOGRAM = "histogram"
    INFO = "info"
    ENUM = "enum"
