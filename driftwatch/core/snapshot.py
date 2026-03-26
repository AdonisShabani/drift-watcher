from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(frozen=True)
class Snapshot:
    """An immutable record of infrastructure state at a point in time.

    Args:
        source: Where this snapshot came from. Examples:
            "kubernetes", "gcp", "file:baseline.yaml"

        data: The actual infrastructure state being tracked for drift.
            Outer key is "resource_type/resource_name", inner dict holds
            the resource's fields. Example:
            {
                "deployment/nginx": {"replicas": 3, "image": "nginx:1.25"},
                "configmap/app-config": {"LOG_LEVEL": "info"},
            }

        timestamp: When this snapshot was taken (UTC ISO format). Example:
            "2026-03-17T12:00:00+00:00"

        metadata: Descriptive labels about the snapshot itself — not the
            infrastructure state. Example:
            {"collector": "manual", "environment": "staging"}
    """
    source: str
    data: dict[str, dict[str, object]]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, str] = field(default_factory=dict)


    def __post_init__(self):
        if not self.source:
            raise ValueError("source is required")
        if not isinstance(self.data, dict):
            raise TypeError("data must be a dictionary of dictionaries")
        for value in self.data.values():
            if not isinstance(value, dict):
                raise TypeError("data must be a dictionary of dictionaries")

    
    # def to_dict(self):
        
        