import json
from dataclasses import dataclass, field
from enum import IntEnum


class Severity(IntEnum):
    """How critical a configuration change is.
    
    We use IntEnum (not plain Enum) for on practical reason: it lets us 
    compare severity levels with < and >, which we need for filtering
    ("show me everythinsg MEDIUM or higher")

    LOW      = cosmetics (label/tag changes, annotations)
    MEDIUM   = operationally relevant (env vars, port changes)
    HIGH     = capacity/availability risk (replica count, machine type)
    CRITICAL = security/compliance risk (firewall rules, IAM bindings)
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass(frozen=True)
class Diff:
    """A single detected difference between expected and actual state.
    
    This is frozen (immutable) for the same reason Snapshot is: once we
    detect a drift, the fact of that drift should never be mutated. A Diff
    is evidence — you record it and move on, just like an audit log entry.

    Args:
        resource: The type/name of the resource that drifted. Example:
            "deployment/nginx", "firewall/allow-ssh"

        field: The specific field that drifted. Example:
            "replicas", "port", "image"

        expected: The expected value (from the baseline snapshot).
            Typed as ``object`` because field values can be strings, ints,
            lists, or nested dicts — just like values in a Kubernetes manifest.

        actual: The value we found in the live infrastructure.
            ``None`` means the entire resource was missing (it was deleted).

        severity: How bad this drift is. Defaults to MEDIUM because most
            drifts are operationally relevant but not emergencies. The diff
            engine will override this based on rules (e.g., replica changes
            get HIGH, firewall changes get CRITICAL).
    """
    resource: str
    field: str
    expected: object
    actual: object
    severity: Severity = Severity.MEDIUM


@dataclass(frozen=True)
class DriftReport:
    """
    The complete result of comparing a baseline snapshot against a live state.

    This is kinda lika the output of ``terraform plan`` - it lists all the changes
    but it does not act on any of it.

    DriftReport is frozen (immutable). Once generated, a report is a historical record.
    If you want a new report, you run a new check

    Args:
        diffs: All detected differences, stored as an immutable tuple.
        baseline_source: Where the expected state came from.
            Example: "file:baseline.yaml", "snapshot:2026-03-17"
        current_source: Where the live state came from/
            Example: "kubernetes", "gcp:my-project"
    """

    diffs: tuple[Diff, ...] = field(default_factory=tuple)
    baseline_source: str = ""
    current_source: str = ""

    def has_drifts(self) -> bool:
        return bool(self.diffs)

    def has_critical(self) -> bool:
        return any(d.severity == Severity.CRITICAL for d in self.diffs)

    def by_severity(self, minimum: Severity = Severity.LOW) -> tuple[Diff, ...]:
        return tuple(d for d in self.diffs if d.severity >= minimum)

    def by_resource(self, resource: str) -> tuple[Diff, ...]:
        return tuple(d for d in self.diffs if d.resource == resource)
    
    def summary(self) -> str:
        if not self.has_drifts():
            return ("No drifts detected")

        lines = []

        lines.append(f"Drift Report: {len(self.diffs)} difference(s) detected")

        if self.baseline_source or self.current_source:
            lines.append(f"  baseline: {self.baseline_source}")
            lines.append(f"  current: {self.current_source}")

        counts = {}

        for d in self.diffs:
            counts[d.severity.name] = counts.get(d.severity.name, 0) + 1

        for sev in reversed(Severity):
            if counts.get(sev.name, 0):
                lines.append(f"  {sev.name}: {counts[sev.name]}")

        for d in self.diffs:
            lines.append(f"  [{d.severity.name}] {d.resource}.{d.field}: {d.expected} -> {d.actual}")
        
        return "\n".join(lines)
        

    def export(self, path: str) -> None:
        data = {
            "baseline_source": self.baseline_source,
            "current_source": self.current_source,
            "diffs": [
                {
                    "resource": d.resource,
                    "field": d.field,
                    "expected": d.expected,
                    "actual": d.actual,
                    "severity": d.severity.name
                }
                for d in self.diffs
            ],
            "total_diffs": len(self.diffs)
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
