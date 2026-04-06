import pytest
from driftwatch.sources.file import FileSource
from driftwatch.core.watcher import DriftWatcher
from driftwatch.diff.formatters import to_text, to_json
from driftwatch.core.report import DriftReport

BASELINE_PATH = "tests/fixtures/baseline.yaml"
CURRENT_PATH = "tests/fixtures/current.yaml"
INVALID_PATH = "tests/fixtures/invalid.yaml"
NON_EXISTENT_PATH = "tests/fixtures/nonexistent.yaml"

def test_loading_yaml():
    snapshot_source = FileSource(BASELINE_PATH).collect()
    assert snapshot_source.source ==  "file"

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        FileSource(NON_EXISTENT_PATH).collect()

def test_invalid_file_structure():
    with pytest.raises(KeyError):
        FileSource(INVALID_PATH).collect()

def test_to_text():
    report = DriftReport()
    result = to_text(report)
    assert isinstance(result, str)

def test_to_json():
    report = DriftReport()
    result = to_json(report)
    assert isinstance(result, dict)

def test_watcher_no_drifts():
    watcher = DriftWatcher(baseline=BASELINE_PATH)
    watcher.add_source("file", FileSource(BASELINE_PATH))
    report = watcher.check()
    assert report.has_drifts() == False

def test_watcher_has_drifts():
    watcher = DriftWatcher(baseline=BASELINE_PATH)
    watcher.add_source("file", FileSource(CURRENT_PATH))
    report = watcher.check()
    assert report.has_drifts() == True