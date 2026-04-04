from driftwatch.core.report import DriftReport
from driftwatch.sources.file import FileSource
from driftwatch.diff.engine import diff_snapshots
from driftwatch.sources.base import BaseSource

class DriftWatcher:
    def __init__(self, baseline):
        self.baseline = baseline
        self.sources: dict[str, BaseSource] = {}

    def add_source(self, name, source):
        self.sources[name] = source
    
    def check(self) -> DriftReport:
        baseline_snapshot = FileSource(self.baseline).collect()
        for source_values in self.sources.values():
            current_snapshot = source_values.collect()
            return diff_snapshots(baseline_snapshot, current_snapshot)
        return DriftReport()


