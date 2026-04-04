from driftwatch.core.report import DriftReport


def to_text(report: DriftReport) -> str:
    return report.summary()

def to_json(report: DriftReport) -> dict:
    data = {
      "baseline_source": report.baseline_source,
      "current_source": report.current_source,
      "total_diffs": len(report.diffs),
      "diffs": [
            {
            "resource": d.resource,
            "field": d.field,
            "expected": d.expected,
            "actual": d.actual,
            "severity": d.severity.name
            }
            for d in report.diffs
        ]
    }
    return data



    

