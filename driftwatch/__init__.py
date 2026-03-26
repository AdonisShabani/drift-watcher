"""driftwatch - Detect configuration drift across Kubernetes and GCP infrastructure.

This is the top-level package. It exposes the main public API so users can write:

    from driftwatch import DriftReport, Snapshot
    from driftwatch.diff import diff_snapshots

instead of digging into submodules.
"""

from driftwatch.core.report import Diff, DriftReport, Severity
from driftwatch.core.snapshot import Snapshot

__all__ = ["Diff", "DriftReport", "Severity", "Snapshot"]

__version__ = "0.1.0"
