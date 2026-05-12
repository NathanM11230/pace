import logging
from pathlib import Path

import requests

from app.config import settings

logger = logging.getLogger(__name__)

_ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


def generate_audio(text: str, filename: str, output_dir: Path) -> str | None:
    """
    Generate an MP3 audio file from *text* using ElevenLabs TTS.

    Parameters
    ----------
    text:       The script text to convert to speech.
    filename:   The desired filename (without directory). Should end in .mp3.
    output_dir: Directory in which to save the audio file.

    Returns the absolute file-path string on success, None on failure.
    """
    api_key = settings.elevenlabs_api_key.strip()
    if not api_key or api_key.lower() in ("none", ""):
        logger.warning(
            "ELEVENLABS_API_KEY is not configured. Skipping audio generation."
        )
        return None

    voice_id = "nQ1MuXZfEsbTXioZJgdm"
    url = f"{_ELEVENLABS_BASE}/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        # Ensure the filename ends with .mp3
        if not filename.endswith(".mp3"):
            filename = filename + ".mp3"

        file_path = output_dir / filename
        file_path.write_bytes(response.content)

        logger.info("Audio saved to '%s' (%d bytes).", file_path, len(response.content))
        return str(file_path)

    except requests.exceptions.Timeout:
        logger.error("Timeout while calling ElevenLabs for file '%s'.", filename)
        return None
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        logger.error(
            "ElevenLabs HTTP error %s for file '%s': %s", status, filename, exc
        )
        return None
    except OSError as exc:
        logger.error("Failed to write audio file '%s': %s", filename, exc)
        return None
    except Exception as exc:
        logger.exception(
            "Unexpected error generating audio for file '%s': %s", filename, exc
        )
        return None
