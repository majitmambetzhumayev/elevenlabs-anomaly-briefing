import pytest
from pydantic import ValidationError
from src.models import AnomalyReport, SeverityLevel, AnomalyType


def test_report_loads_from_sample(sample_report):
    assert sample_report.report_id == "FIN-2026-Q2-0047"
    assert sample_report.municipality == "City of Riverside"
    assert len(sample_report.anomalies) == 5


def test_severity_distribution(sample_report):
    stats = sample_report.summary_stats
    assert stats.high_severity == 2
    assert stats.medium_severity == 2
    assert stats.low_severity == 1


def test_anomaly_types_are_valid(sample_report):
    for anomaly in sample_report.anomalies:
        assert isinstance(anomaly.severity, SeverityLevel)
        assert isinstance(anomaly.type, AnomalyType)


def test_invalid_severity_raises():
    with pytest.raises(ValidationError):
        AnomalyReport(**{
            "report_id": "X",
            "generated_at": "2026-01-01T00:00:00Z",
            "municipality": "Test",
            "fiscal_period": "Q1",
            "anomalies": [{
                "id": "A1",
                "type": "budget_overrun",
                "severity": "critical",  # valeur invalide
                "department": "IT",
                "description": "test",
                "amount_flagged": 100.0,
                "detected_at": "2026-01-01T00:00:00Z",
            }],
            "summary_stats": {
                "total_anomalies": 1,
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0,
                "total_amount_flagged": 100.0,
            }
        })


def test_negative_amount_raises():
    with pytest.raises(ValidationError):
        AnomalyReport(**{
            "report_id": "X",
            "generated_at": "2026-01-01T00:00:00Z",
            "municipality": "Test",
            "fiscal_period": "Q1",
            "anomalies": [{
                "id": "A1",
                "type": "budget_overrun",
                "severity": "high",
                "department": "IT",
                "description": "test",
                "amount_flagged": -500.0,  # montant invalide
                "detected_at": "2026-01-01T00:00:00Z",
            }],
            "summary_stats": {
                "total_anomalies": 1,
                "high_severity": 1,
                "medium_severity": 0,
                "low_severity": 0,
                "total_amount_flagged": 500.0,
            }
        })
