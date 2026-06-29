import typer
from pathlib import Path
from typing import Optional
from src.pipeline import run

app = typer.Typer()


@app.command()
def generate(
    json_path: Path = typer.Argument(..., help="Path to anomaly report JSON"),
    voice_id: Optional[str] = typer.Option(None, "--voice-id", "-v", help="ElevenLabs voice ID"),
):
    """Generate an audio briefing from an anomaly report."""
    if not json_path.exists():
        typer.echo(f"Error: file not found — {json_path}", err=True)
        raise typer.Exit(1)

    try:
        result = run(json_path, voice_id=voice_id)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    typer.echo("\n--- Summary ---")
    typer.echo(result["summary"])
    typer.echo(f"\nAudio → {result['audio_path']}")


if __name__ == "__main__":
    app()
