import json
from pathlib import Path
from uuid import uuid4

import streamlit as st
from pydantic import ValidationError

from src.pipeline import run

SAMPLE_PATH = Path(__file__).parent / "data" / "sample_anomalies.json"

st.set_page_config(page_title="Anomaly Briefing", page_icon="🔊", layout="centered")

st.title("Anomaly Briefing Generator")
st.caption("Powered by Claude + ElevenLabs — financial anomaly reports → audio briefings")

st.divider()

source = st.radio("Data source", ["Use sample report", "Upload JSON"], horizontal=True)

json_path = None

if source == "Use sample report":
    json_path = SAMPLE_PATH
    with open(SAMPLE_PATH) as f:
        st.json(json.load(f), expanded=False)
else:
    uploaded = st.file_uploader("Upload anomaly report JSON", type="json")
    if uploaded:
        tmp_path = Path("/tmp") / f"{uuid4()}_{uploaded.name}"
        tmp_path.write_bytes(uploaded.read())
        json_path = tmp_path
        with open(json_path) as f:
            st.json(json.load(f), expanded=False)

voice_id = st.text_input(
    "Voice ID (optional)",
    placeholder="Leave blank to use default",
    help="ElevenLabs voice ID — find voices at elevenlabs.io/voice-library",
)

st.divider()

if st.button("Generate briefing", type="primary", disabled=json_path is None):
    with st.spinner("Generating briefing..."):
        try:
            result = run(json_path, voice_id=voice_id or None)
        except ValidationError as e:
            st.error(f"Invalid report format: {e.error_count()} field(s) failed validation. Check your JSON.")
            st.stop()
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.stop()

    st.success(f"Briefing ready — report `{result['report_id']}`")

    st.subheader("Summary")
    st.write(result["summary"])

    st.subheader("Audio")
    audio_bytes = Path(result["audio_path"]).read_bytes()
    st.audio(audio_bytes, format="audio/mp3")
    st.download_button(
        label="Download MP3",
        data=audio_bytes,
        file_name=Path(result["audio_path"]).name,
        mime="audio/mpeg",
    )
