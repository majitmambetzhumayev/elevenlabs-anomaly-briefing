from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnomalyType(str, Enum):
    BUDGET_OVERRUN = "budget_overrun"
    DUPLICATE_PAYMENT = "duplicate_payment"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    IRREGULAR_PATTERN = "irregular_pattern"
    MISSING_DOCUMENTATION = "missing_documentation"


class Anomaly(BaseModel):
    id: str
    type: AnomalyType
    severity: SeverityLevel
    department: str
    description: str
    amount_flagged: float = Field(gt=0)
    detected_at: datetime

    # champs optionnels selon le type d'anomalie
    vendor: Optional[str] = None
    invoice_ref: Optional[str] = None
    transaction_count: Optional[int] = None
    budget_limit: Optional[float] = None
    actual_spend: Optional[float] = None
    approval_threshold: Optional[float] = None


class SummaryStats(BaseModel):
    total_anomalies: int
    high_severity: int
    medium_severity: int
    low_severity: int
    total_amount_flagged: float


class AnomalyReport(BaseModel):
    report_id: str
    generated_at: datetime
    municipality: str
    fiscal_period: str
    anomalies: list[Anomaly]
    summary_stats: SummaryStats

    @model_validator(mode="after")
    def stats_match_anomalies(self) -> "AnomalyReport":
        actual_total = len(self.anomalies)
        actual_amount = sum(a.amount_flagged for a in self.anomalies)
        actual_high = sum(1 for a in self.anomalies if a.severity == SeverityLevel.HIGH)
        actual_medium = sum(1 for a in self.anomalies if a.severity == SeverityLevel.MEDIUM)
        actual_low = sum(1 for a in self.anomalies if a.severity == SeverityLevel.LOW)

        if self.summary_stats.total_anomalies != actual_total:
            raise ValueError(
                f"summary_stats.total_anomalies={self.summary_stats.total_anomalies} "
                f"but {actual_total} anomalies found"
            )
        if round(self.summary_stats.total_amount_flagged, 2) != round(actual_amount, 2):
            raise ValueError(
                f"summary_stats.total_amount_flagged={self.summary_stats.total_amount_flagged} "
                f"but anomalies sum to {actual_amount:.2f}"
            )
        if self.summary_stats.high_severity != actual_high:
            raise ValueError(f"summary_stats.high_severity={self.summary_stats.high_severity} but {actual_high} found")
        if self.summary_stats.medium_severity != actual_medium:
            raise ValueError(f"summary_stats.medium_severity={self.summary_stats.medium_severity} but {actual_medium} found")
        if self.summary_stats.low_severity != actual_low:
            raise ValueError(f"summary_stats.low_severity={self.summary_stats.low_severity} but {actual_low} found")
        return self
