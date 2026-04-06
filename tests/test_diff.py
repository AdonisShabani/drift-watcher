import json
import tempfile
import pytest
from dataclasses import FrozenInstanceError
from driftwatch import Snapshot, diff
from driftwatch.core.report import Severity, Diff, DriftReport
from driftwatch.diff.engine import diff_snapshots


def test_severity_ordering():
    assert Severity.CRITICAL > Severity.HIGH
    assert Severity.HIGH > Severity.MEDIUM
    assert Severity.MEDIUM > Severity.LOW

def test_diff_construction():
    d = Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1)
    assert d.resource == "deployment/nginx"
    assert d.field == "replicas"
    assert d.expected == 3
    assert d.actual == 1
    assert d.severity == Severity.MEDIUM

def test_diff_immutabilty():
    d = Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1)
    with pytest.raises(FrozenInstanceError):
        d.resource = "deployment/busybox"

def test_driftreport_no_drifts():
    d = DriftReport()
    assert d.has_drifts() == False

def test_driftreport_has_drifts():
    d = DriftReport(diffs=(Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1),))
    assert d.has_drifts() == True

def test_critical_drifts():
    d = DriftReport(diffs=(Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1, severity=Severity.CRITICAL),))
    assert d.has_critical() == True

def test_non_critical_drifts():
    d = DriftReport(diffs=(Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1, severity=Severity.HIGH),))
    assert d.has_critical() == False

def test_by_severity():
    d = DriftReport(diffs=(Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1, severity=Severity.HIGH),Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1, severity=Severity.LOW)))
    result = d.by_severity(Severity.HIGH)
    assert len(result) == 1
    assert result[0].severity == Severity.HIGH

def test_by_resource():
    d = DriftReport(diffs=(Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1, severity=Severity.HIGH),Diff(resource="deployment/busybox", field="replicas", expected=3, actual=1, severity=Severity.LOW)))
    result = d.by_resource(resource="deployment/nginx")
    assert len(result) == 1
    assert result[0].resource == "deployment/nginx"

def test_summary_with_no_drifts():
    d = DriftReport()
    assert d.summary() == "No drifts detected"

def test_summary_with_drifts():
    d = DriftReport(diffs=(Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1),))
    result = d.summary()
    assert "deployment/nginx" in result
    assert "replicas" in result
    assert "3" in result
    assert "1" in result

def test_export():
    d = DriftReport(diffs=(Diff(resource="deployment/nginx", field="replicas", expected=3, actual=1),))
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    d.export(path)
    with open(path) as f:
        data = json.load(f)

    assert data["total_diffs"] == 1
    assert data["diffs"][0]["resource"] == "deployment/nginx"
    assert data["diffs"][0]["field"] == "replicas"

def test_no_drift():
    baseline = Snapshot(source="kubernetes", data={"deployment/nginx": {"replicas": 3}})
    current = Snapshot(source="kubernetes", data={"deployment/nginx": {"replicas": 3}})
    report = diff_snapshots(baseline, current)
    assert report.has_drifts() == False

def test_with_drift_in_values():
    baseline = Snapshot(source="kubernetes", data={"deployment/nginx": {"replicas": 3}})
    current = Snapshot(source="kubernetes", data={"deployment/nginx": {"replicas": 1}})
    report = diff_snapshots(baseline, current)
    assert report.diffs[0].expected == 3
    assert report.diffs[0].actual == 1

def test_with_drfit_sources():
    baseline = Snapshot(source="kubernetes", data={"deployment/nginx": {"replicas": 3}})
    current = Snapshot(source="gcp", data={"cloud_run": {"replicas": 1}})
    with pytest.raises(ValueError):
        diff_snapshots(baseline, current)
        
    
def test_with_deleted_current_resource():
    baseline = Snapshot(source="kubernetes", data={"deployment/nginx": {"replicas": 3}})
    current = Snapshot(source="kubernetes", data={})
    report = diff_snapshots(baseline, current)
    assert report.diffs[0].actual is None
    assert report.diffs[0].field == "*"

def test_with_deleted_baseline_resource():
    baseline = Snapshot(source="kubernetes", data={})
    current = Snapshot(source="kubernetes", data={"deployment/nginx": {"replicas": 3}})
    report = diff_snapshots(baseline, current)
    assert report.diffs[0].expected is None
    assert report.diffs[0].field == "*"