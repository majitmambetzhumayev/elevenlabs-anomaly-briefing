import json
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from .models import AnomalyReport
from .summarizer import summarize
from .voice_generator import generate_audio

load_dotenv()


def _safe_filename(report_id: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", report_id)
    return f"briefing_{sanitized}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"


def run(json_path: str | Path, voice_id: str | None = None) -> dict:
    with open(json_path) as f:
        raw = json.load(f)

    report = AnomalyReport(**raw)

    print(f"[pipeline] Summarizing {report.summary_stats.total_anomalies} anomalies via Claude...")
    text = summarize(report)
    print(f"[pipeline] Summary ready ({len(text)} chars)")

    print(f"[pipeline] Generating audio via ElevenLabs...")
    output_path = generate_audio(text, _safe_filename(report.report_id), voice_id=voice_id)
    print(f"[pipeline] Audio saved → {output_path}")

    return {
        "report_id": report.report_id,
        "summary": text,
        "audio_path": str(output_path),
    }
