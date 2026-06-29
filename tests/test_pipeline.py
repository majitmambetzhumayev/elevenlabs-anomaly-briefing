from pathlib import Path
from unittest.mock import patch
from src.pipeline import run


FAKE_SUMMARY = "This is a test briefing for City of Riverside."
FAKE_AUDIO_PATH = "/fake/output/briefing.mp3"


def test_pipeline_returns_expected_keys(sample_json_path):
    with patch("src.pipeline.summarize", return_value=FAKE_SUMMARY), \
         patch("src.pipeline.generate_audio", return_value=Path(FAKE_AUDIO_PATH)):
        result = run(sample_json_path)

    assert "report_id" in result
    assert "summary" in result
    assert "audio_path" in result


def test_pipeline_passes_summary_to_audio(sample_json_path):
    with patch("src.pipeline.summarize", return_value=FAKE_SUMMARY) as mock_summarize, \
         patch("src.pipeline.generate_audio", return_value=Path(FAKE_AUDIO_PATH)) as mock_audio:
        run(sample_json_path)

    mock_summarize.assert_called_once()
    mock_audio.assert_called_once()

    audio_call_args = mock_audio.call_args.args
    assert audio_call_args[0] == FAKE_SUMMARY


def test_pipeline_report_id_matches_json(sample_json_path):
    with patch("src.pipeline.summarize", return_value=FAKE_SUMMARY), \
         patch("src.pipeline.generate_audio", return_value=Path(FAKE_AUDIO_PATH)):
        result = run(sample_json_path)

    assert result["report_id"] == "FIN-2026-Q2-0047"
