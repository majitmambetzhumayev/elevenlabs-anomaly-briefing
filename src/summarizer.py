import os
import anthropic

from .models import AnomalyReport

SYSTEM_PROMPT = """You are a financial compliance officer delivering an audio briefing.
Your summaries will be converted to speech, so follow these rules:
- Write in plain prose, no bullet points, no markdown, no special characters
- Use natural spoken language with smooth transitions
- Spell out numbers and amounts (say "one hundred forty two thousand dollars" not "$142,000")
- Keep the tone professional but clear — this will be heard, not read
- Structure: open with the report context, cover high-severity issues first, close with a summary"""

USER_PROMPT_TEMPLATE = """Generate an audio briefing for the following anomaly report.

Municipality: {municipality}
Fiscal period: {fiscal_period}
Report ID: {report_id}

Anomalies detected ({total} total — {high} high severity, {medium} medium, {low} low):

{anomaly_details}

Total amount flagged: {total_amount}

Deliver a clear, professional briefing suitable for audio playback. Around 150 words."""


def _format_anomaly_details(report: AnomalyReport) -> str:
    lines = []
    for a in report.anomalies:
        lines.append(
            f"[{a.severity.value.upper()}] {a.type.value} — {a.department}: "
            f"{a.description} (flagged amount: {a.amount_flagged:,.2f} USD)"
        )
    return "\n".join(lines)


def summarize(report: AnomalyReport) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = USER_PROMPT_TEMPLATE.format(
        municipality=report.municipality,
        fiscal_period=report.fiscal_period,
        report_id=report.report_id,
        total=report.summary_stats.total_anomalies,
        high=report.summary_stats.high_severity,
        medium=report.summary_stats.medium_severity,
        low=report.summary_stats.low_severity,
        anomaly_details=_format_anomaly_details(report),
        total_amount=f"{report.summary_stats.total_amount_flagged:,.2f}",
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    if message.stop_reason == "max_tokens":
        raise RuntimeError("Claude response was truncated — increase max_tokens or reduce anomaly count")

    text_blocks = [b for b in message.content if hasattr(b, "text")]
    if not text_blocks:
        raise RuntimeError("Claude returned no text content")

    return text_blocks[0].text
