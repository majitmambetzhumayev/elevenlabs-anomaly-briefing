import json
import pytest
from pathlib import Path
from src.models import AnomalyReport

SAMPLE_PATH = Path(__file__).parent.parent / "data" / "sample_anomalies.json"


@pytest.fixture
def sample_report() -> AnomalyReport:
    with open(SAMPLE_PATH) as f:
        return AnomalyReport(**json.load(f))


@pytest.fixture
def sample_json_path() -> Path:
    return SAMPLE_PATH
