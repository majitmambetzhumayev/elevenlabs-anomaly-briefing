# ElevenLabs Anomaly Briefing

A Python pipeline that transforms structured financial anomaly reports into audio briefings — combining an LLM summarization layer with ElevenLabs Text-to-Speech.

Built as a Solutions Engineer portfolio project: demonstrates a realistic enterprise integration pattern where data pipelines produce audio output for async consumption.

---

## Architecture

```
sample_anomalies.json
        │
        ▼
  [Pydantic models]     ← validation at the system boundary
        │
        ▼
   summarizer.py        ← LLM → structured data to natural language
        │
        ▼
 voice_generator.py     ← ElevenLabs TTS → text to audio bytes
        │
        ▼
    pipeline.py         ← orchestration, error handling
        │
        ▼
  output/briefing.mp3
```

The pipeline is intentionally stateless and synchronous — each `run()` call is self-contained, making it easy to embed in a Celery task, a webhook handler, or a batch job.

---

## Stack

- **Python 3.11+**
- [`elevenlabs`](https://pypi.org/project/elevenlabs/) — official Python SDK v2.x
- [`anthropic`](https://pypi.org/project/anthropic/) — LLM summarization
- [`pydantic`](https://pypi.org/project/pydantic/) v2 — input validation
- [`streamlit`](https://pypi.org/project/streamlit/) — demo UI

---

## Setup

```bash
git clone <repo>
cd elevenlabs-anomaly-briefing

pip install -r requirements.txt

cp .env.example .env
# fill in your API keys
```

### Environment variables

```env
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb   # optional — defaults to George (EN)
```

---

## Usage

### Streamlit UI (recommended for demo)

```bash
streamlit run app.py
```

Open `http://localhost:8501` — use the sample report or upload your own JSON.

### Programmatic

```python
from src.pipeline import run

result = run("data/sample_anomalies.json")
print(result["summary"])   # LLM-generated text
print(result["audio_path"])  # path to output MP3
```

---

## Input format

The pipeline expects a JSON report with this structure:

```json
{
  "report_id": "FIN-2026-Q2-0047",
  "generated_at": "2026-06-29T08:00:00Z",
  "municipality": "City of Riverside",
  "fiscal_period": "Q2 2026",
  "anomalies": [
    {
      "id": "ANO-001",
      "type": "budget_overrun",
      "severity": "high",
      "department": "Public Works",
      "description": "Infrastructure maintenance spend exceeded approved budget by 34%",
      "amount_flagged": 142500.00,
      "detected_at": "2026-06-15T14:22:00Z"
    }
  ],
  "summary_stats": {
    "total_anomalies": 1,
    "high_severity": 1,
    "medium_severity": 0,
    "low_severity": 0,
    "total_amount_flagged": 142500.00
  }
}
```

Valid `type` values: `budget_overrun`, `duplicate_payment`, `threshold_exceeded`, `irregular_pattern`, `missing_documentation`

Valid `severity` values: `high`, `medium`, `low`

Pydantic validates the report on ingestion and cross-checks `summary_stats` against the actual anomaly list — mismatches raise a `ValidationError` before any API call is made.

---

## Adapting to other data sources

The pipeline decouples ingestion from generation. To plug in a different data source:

1. Map your data to the `AnomalyReport` schema (or extend the Pydantic models)
2. Call `pipeline.run(path_to_json)` — everything downstream is unchanged

The summarization prompt (`src/summarizer.py`) is the only place that encodes domain knowledge. Swap it to change tone, language, or output structure without touching the audio layer.

---

## Tests

```bash
python3 -m pytest tests/ -v
```

All tests mock external APIs — no keys required to run the suite.

---

## Output example

Input: `data/sample_anomalies.json` (5 anomalies, $196k flagged)

Generated summary:

> Good morning. This is a financial compliance briefing for the City of Riverside, covering Q2 2026. Five anomalies have been detected, with a combined flagged amount of one hundred ninety-six thousand six hundred sixty-five dollars. The two high-severity findings require immediate attention: Public Works exceeded its infrastructure budget by thirty-four percent, and Finance processed a duplicate payment of twenty-eight thousand dollars to Acme Contractors. Medium-severity items involve an unapproved purchase order in Parks and Recreation and irregular vendor transactions in IT. A low-severity documentation gap was flagged in Human Resources. Two findings demand urgent escalation before close of period. End of briefing.

Audio: `output/briefing_FIN-2026-Q2-0047_20260629_120000.mp3`
