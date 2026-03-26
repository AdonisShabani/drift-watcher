"""Core module - contains the main classes: DriftWatcher, Snapshot, DriftReport."""

from driftwatch.core.report import Diff, DriftReport, Severity
from driftwatch.core.snapshot import Snapshot

__all__ = ["Diff", "DriftReport", "Severity", "Snapshot"]
