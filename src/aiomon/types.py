import enum


class MetricType(str, enum.Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    SUMMARY = "summary"
    HISTOGRAM = "histogram"
    INFO = "info"
    ENUM = "enum"
