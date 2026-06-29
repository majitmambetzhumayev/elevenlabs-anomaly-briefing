from unittest.mock import patch, MagicMock
from src.summarizer import summarize, _format_anomaly_details


def test_format_anomaly_details(sample_report):
    result = _format_anomaly_details(sample_report)
    assert "Public Works" in result
    assert "HIGH" in result
    assert "duplicate_payment" in result


def test_summarize_calls_anthropic(sample_report):
    mock_text = "This is the audio briefing for City of Riverside."
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=mock_text)]

    with patch("src.summarizer.anthropic.Anthropic") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.messages.create.return_value = mock_message

        result = summarize(sample_report)

    assert result == mock_text
    mock_client.messages.create.assert_called_once()


def test_summarize_prompt_contains_municipality(sample_report):
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="briefing")]

    with patch("src.summarizer.anthropic.Anthropic") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.messages.create.return_value = mock_message

        summarize(sample_report)

    call_kwargs = mock_client.messages.create.call_args.kwargs
    user_content = call_kwargs["messages"][0]["content"]
    assert "City of Riverside" in user_content
    assert "FIN-2026-Q2-0047" in user_content
