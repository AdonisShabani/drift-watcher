from math import exp
from driftwatch.core.snapshot import Snapshot
from driftwatch.core.report import Diff, Severity, DriftReport


def diff_snapshots(baseline: Snapshot, current: Snapshot) -> DriftReport:
    if baseline.source != current.source:
        raise ValueError("Baseline and current state have different sources")

    diffs = []

    for resource in baseline.data:
        if resource not in current.data:
            diffs.append(
                Diff(
                    resource=resource,
                    field="*",
                    expected=baseline.data[resource],
                    actual=None,
                    severity=Severity.HIGH
                )
            )
        else:
            for field in baseline.data[resource]:
                if field not in current.data[resource]:
                    diffs.append(
                        Diff(
                            resource=resource,
                            field=field,
                            expected=baseline.data[resource][field],
                            actual=None,
                            severity=Severity.MEDIUM
                        )
                    )
                elif baseline.data[resource][field] != current.data[resource][field]:
                    diffs.append(
                        Diff(
                            resource=resource,
                            field=field,
                            expected=baseline.data[resource][field],
                            actual=current.data[resource][field],
                            severity=Severity.MEDIUM
                        )
                    )
    for resource in current.data:
        if resource not in baseline.data:
            diffs.append(
                Diff(
                    resource=resource,
                    field="*",
                    expected=None,
                    actual=current.data[resource],
                    severity=Severity.HIGH
                )
            )
    return DriftReport(
        diffs=tuple(diffs),
        baseline_source=baseline.source,
        current_source=current.source
    )