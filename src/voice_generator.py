import os
from pathlib import Path
from elevenlabs.client import ElevenLabs

# eleven_multilingual_v2 — supports 70+ languages, best quality/latency tradeoff for voice briefings
DEFAULT_MODEL = "eleven_multilingual_v2"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def generate_audio(text: str, output_filename: str, voice_id: str | None = None) -> Path:
    # George — ElevenLabs pre-built, professional male EN, voice ID: JBFqnCBsd6RMkjVDRZzb
    # evaluated here (not at import time) so load_dotenv() in pipeline.py has already run
    voice_id = voice_id or os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=DEFAULT_MODEL,
        output_format="mp3_44100_128",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename

    try:
        with open(output_path, "wb") as f:
            written = 0
            for chunk in audio_stream:
                f.write(chunk)
                written += len(chunk)
    except OSError:
        output_path.unlink(missing_ok=True)
        raise

    if written == 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError("ElevenLabs returned an empty audio stream")

    return output_path
