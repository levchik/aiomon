"""Prometheus exposition format formatter."""

from aiomon.base import MonitorFormatter, MonitorOutputData, MonitorOutputItem


class PrometheusFormatter(MonitorFormatter[str]):
    """Format metrics in Prometheus exposition format.

    Prometheus format uses plain text:
    - # HELP metric_name description
    - # TYPE metric_name type
    - metric_name{label="value"} value
    """

    def format_(
        self,
        metrics: MonitorOutputData,
        fields_only: set[str] | None = None,  # noqa: ARG002
    ) -> str:
        lines = []

        for item in metrics:
            metric = item.metric

            # Add HELP comment
            lines.append(f"# HELP {metric.name} {metric.name} metric")

            # Add TYPE comment based on metric type
            prom_type = self._map_metric_type(metric.type_)
            lines.append(f"# TYPE {metric.name} {prom_type}")

            # Format value based on metric type
            lines.extend(self._format_value(item))

        return "\n".join(lines) + "\n"

    def _map_metric_type(self, metric_type: str) -> str:
        """Map aiomon metric type to Prometheus type."""
        mapping = {
            "counter": "counter",
            "gauge": "gauge",
            "histogram": "histogram",
            "summary": "summary",
            "info": "gauge",
            "enum": "gauge",
        }
        return mapping.get(metric_type, "untyped")

    def _format_value(self, item: MonitorOutputItem) -> list[str]:
        """Format metric value based on type."""
        lines = []
        labels = self._format_labels(item)

        if item.metric.type_ in ("counter", "gauge"):
            value_str = f"{item.metric.name}{labels} {item.value}"
            lines.append(value_str)
        elif item.metric.type_ == "histogram":
            lines.extend(self._format_histogram(item, labels))
        elif item.metric.type_ == "summary":
            lines.extend(self._format_summary(item, labels))
        else:
            value_str = f"{item.metric.name}{labels} {item.value}"
            lines.append(value_str)

        return lines

    def _format_labels(self, item: MonitorOutputItem) -> str:
        """Convert tags and metadata to Prometheus labels."""
        labels = {}

        if item.metric.tags:
            for tag in item.metric.tags:
                if ":" in tag:
                    key, value = tag.split(":", 1)
                    labels[key] = value

        if item.metric.host:
            labels["host"] = item.metric.host

        if labels:
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
            return f"{{{label_str}}}"

        return ""

    def _format_histogram(
        self,
        item: MonitorOutputItem,
        base_labels: str,
    ) -> list[str]:
        """Format histogram metric."""
        lines = []
        value = item.value

        if isinstance(value, dict):
            buckets = value.get("buckets", {})
            for bucket, count in sorted(buckets.items()):
                bucket_label = "inf" if bucket == float("inf") else str(bucket)
                labels = self._add_label_to_base(
                    base_labels,
                    "le",
                    bucket_label,
                )
                lines.append(f"{item.metric.name}_bucket{labels} {count}")

            sum_labels = self._add_label_to_base(base_labels, None, None)
            sum_val = value.get("sum", 0)
            count_val = value.get("count", 0)
            lines.append(f"{item.metric.name}_sum{sum_labels} {sum_val}")
            lines.append(f"{item.metric.name}_count{sum_labels} {count_val}")

        return lines

    def _format_summary(
        self,
        item: MonitorOutputItem,
        base_labels: str,
    ) -> list[str]:
        """Format summary metric."""
        lines = []
        value = item.value

        if isinstance(value, dict):
            quantiles = value.get("quantiles", {})
            for q, v in quantiles.items():
                labels = self._add_label_to_base(
                    base_labels,
                    "quantile",
                    str(q),
                )
                lines.append(f"{item.metric.name}{labels} {v}")

            sum_labels = self._add_label_to_base(base_labels, None, None)
            sum_val = value.get("sum", 0)
            count_val = value.get("count", 0)
            lines.append(f"{item.metric.name}_sum{sum_labels} {sum_val}")
            lines.append(f"{item.metric.name}_count{sum_labels} {count_val}")

        return lines

    def _add_label_to_base(
        self,
        base_labels: str,
        new_key: str | None,
        new_value: str | None,
    ) -> str:
        """Add a new label to existing base labels."""
        if new_key is None or new_value is None:
            return base_labels

        # Parse existing labels
        if base_labels:
            # Remove surrounding braces
            inner = base_labels[1:-1]
            return f'{{{inner},{new_key}="{new_value}"}}'
        else:
            return f'{{{new_key}="{new_value}"}}'
