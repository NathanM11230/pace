import io
import logging
import random
import re
from pathlib import Path

import requests
from pydub import AudioSegment

from app.config import settings
from app.services.voice_pairs import get_voice_pair

# ---------------------------------------------------------------------------
# Wire pydub to the bundled ffmpeg binary (imageio-ffmpeg) when system ffmpeg
# is not on PATH. This avoids requiring a manual ffmpeg install on Windows.
# ---------------------------------------------------------------------------
try:
    import imageio_ffmpeg
    _ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    AudioSegment.converter = _ffmpeg_exe
    AudioSegment.ffmpeg = _ffmpeg_exe
except ImportError:
    pass  # Fall back to whatever pydub finds on PATH

# Wire ffprobe from conda if it exists but isn't on PATH.
# pydub calls get_prober_name() internally so we patch it directly.
import os as _os, shutil as _shutil
import pydub.utils as _pydub_utils
if not _shutil.which("ffprobe"):
    _candidate = _os.path.expanduser("~/anaconda3/Library/bin/ffprobe.exe")
    if _os.path.exists(_candidate):
        _pydub_utils.get_prober_name = lambda: _candidate

logger = logging.getLogger(__name__)

_ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


# ---------------------------------------------------------------------------
# Dialogue parser
# ---------------------------------------------------------------------------

def parse_dialogue(script: str) -> list[dict]:
    """
    Parse a dialogue script into a list of line dicts.

    Each line prefixed "A:" or "B:" becomes:
        {
            voice:            "A" or "B",
            text:             cleaned line text (dash stripped for interruptions),
            has_interruption: True if the line ended with "-",
            ends_with:        one of ".", "?", "!", "...", "-"
        }

    Lines that don't match the A:/B: pattern are silently skipped.
    """
    lines = []
    for raw in script.splitlines():
        raw = raw.strip()
        if not raw:
            continue

        match = re.match(r"^([AB]):\s*(.+)$", raw)
        if not match:
            continue

        voice = match.group(1)
        text = match.group(2).strip()

        # Detect ends_with in order of specificity.
        # Handle both ASCII hyphen (-) and em dash (—) as interruption markers,
        # since Claude occasionally outputs em dashes in place of hyphens.
        if text.endswith("-") or text.endswith("\u2014"):
            ends_with = "-"
            has_interruption = True
            text = text.rstrip("-").rstrip("\u2014").rstrip()
        elif text.endswith("..."):
            ends_with = "..."
            has_interruption = False
        elif text.endswith("?"):
            ends_with = "?"
            has_interruption = False
        elif text.endswith("!"):
            ends_with = "!"
            has_interruption = False
        else:
            ends_with = "."
            has_interruption = False

        lines.append(
            {
                "voice": voice,
                "text": text,
                "has_interruption": has_interruption,
                "ends_with": ends_with,
            }
        )

    return lines


# ---------------------------------------------------------------------------
# ElevenLabs TTS helper
# ---------------------------------------------------------------------------

def _fetch_tts(text: str, voice_id: str, api_key: str) -> bytes | None:
    """Call ElevenLabs TTS for a single line and return raw MP3 bytes."""
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
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        return response.content
    except requests.exceptions.Timeout:
        logger.error("Timeout calling ElevenLabs for voice '%s'.", voice_id)
        return None
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        logger.error(
            "ElevenLabs HTTP error %s for voice '%s': %s", status, voice_id, exc
        )
        return None
    except Exception as exc:
        logger.exception(
            "Unexpected error calling ElevenLabs for voice '%s': %s", voice_id, exc
        )
        return None


# ---------------------------------------------------------------------------
# Humanization helpers
# ---------------------------------------------------------------------------

def _compute_pause_ms(prev_line: dict, curr_line: dict) -> int:
    """
    Technique 2 — Variable Pause Timing.
    Returns milliseconds of silence to insert between two clips.
    """
    ends_with = prev_line["ends_with"]
    curr_word_count = len(curr_line["text"].split())

    # Very short current line gets a snappy gap regardless of what came before
    if curr_word_count < 5:
        return random.randint(50, 150)

    if ends_with == "-":
        return 0
    elif ends_with == "?":
        return random.randint(100, 200)
    elif ends_with == "!":
        return random.randint(100, 300)
    elif ends_with == "...":
        return random.randint(400, 800)
    else:  # "."
        return random.randint(200, 500)


def _apply_humanization(seg: AudioSegment, line: dict) -> AudioSegment:
    """
    Apply per-clip humanization: fades, volume, and interruption trim.

    Technique 3 — Cut-Off Speech: trim + fade-out for interrupted lines.
    Technique 4 — Fade In/Out: 30-50 ms on every clip.
    Technique 5 — Volume Dynamics: short reactions quieter, excited lines louder.
    """
    # Technique 3: Cut-off speech for interruption lines
    if line["has_interruption"]:
        trim_ms = random.randint(100, 200)
        # Guard against trimming more than we have
        trim_ms = min(trim_ms, len(seg) - 100)
        if trim_ms > 0:
            seg = seg[:-trim_ms]
        seg = seg.fade_out(50)

    # Technique 4: Fade in/out on every clip
    fade_ms = random.randint(30, 50)
    seg = seg.fade_in(fade_ms).fade_out(fade_ms)

    # Technique 5: Volume dynamics
    word_count = len(line["text"].split())
    if word_count < 4:
        # Short reactions (e.g. "Yeah.", "Huh.") — 85% volume ≈ -1.4 dB
        seg = seg - 1.4
    elif line["ends_with"] == "!":
        # Excited lines — 105% volume ≈ +0.4 dB
        seg = seg + 0.4

    return seg


# ---------------------------------------------------------------------------
# Main audio generation entry point
# ---------------------------------------------------------------------------

def generate_audio(
    script: str, category: str, filename: str, output_dir: Path
) -> str | None:
    """
    Generate a multi-voice MP3 from a dialogue *script* for the given *category*.

    Steps:
      1. Look up the voice pair for the category.
      2. Parse the dialogue into lines.
      3. Fetch TTS audio for each line with the correct voice.
      4. Apply per-clip humanization (fades, volume, interruption trim).
      5. Stitch clips with variable pauses or overlaps.
      6. Export to *output_dir/filename*.

    Returns the absolute file-path string on success, None on failure.
    """
    api_key = settings.elevenlabs_api_key.strip()
    if not api_key or api_key.lower() in ("none", ""):
        logger.warning(
            "ELEVENLABS_API_KEY is not configured. Skipping audio generation."
        )
        return None

    voice_pair = get_voice_pair(category)
    show_name = voice_pair["show"]
    logger.info(
        "Generating audio for show '%s' (category: '%s').", show_name, category
    )

    lines = parse_dialogue(script)
    if not lines:
        logger.error("No dialogue lines parsed from script for category '%s'.", category)
        return None

    # ---- Fetch TTS for each line ----------------------------------------
    segments: list[tuple[dict, AudioSegment]] = []
    for i, line in enumerate(lines):
        voice_id = (
            voice_pair["voice_a"] if line["voice"] == "A" else voice_pair["voice_b"]
        )
        logger.debug(
            "Line %d [%s]: voice=%s  text=%r", i, line["ends_with"], line["voice"], line["text"][:60]
        )
        audio_bytes = _fetch_tts(line["text"], voice_id, api_key)
        if audio_bytes is None:
            logger.warning("Skipping line %d — TTS failed.", i)
            continue

        seg = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3", codec="mp3")
        seg = _apply_humanization(seg, line)
        segments.append((line, seg))

    if not segments:
        logger.error("All TTS calls failed for category '%s'.", category)
        return None

    # ---- Stitch clips together ------------------------------------------
    result: AudioSegment = segments[0][1]

    for i in range(1, len(segments)):
        prev_line, _ = segments[i - 1]
        curr_line, curr_seg = segments[i]

        if prev_line["has_interruption"]:
            # Technique 1 — Strategic Overlap: slide curr_seg under the tail of result
            overlap_ms = random.randint(200, 400)
            overlap_ms = min(overlap_ms, len(result), len(curr_seg))
            position = max(0, len(result) - overlap_ms)
            logger.debug(
                "  Transition %d→%d: OVERLAP %d ms", i - 1, i, overlap_ms
            )
            result = result.overlay(curr_seg, position=position)
        else:
            # Technique 2 — Variable Pause Timing
            pause_ms = _compute_pause_ms(prev_line, curr_line)
            logger.debug(
                "  Transition %d→%d: pause %d ms (prev ends_with=%r, curr_words=%d)",
                i - 1,
                i,
                pause_ms,
                prev_line["ends_with"],
                len(curr_line["text"].split()),
            )
            if pause_ms > 0:
                result = result + AudioSegment.silent(duration=pause_ms) + curr_seg
            else:
                result = result + curr_seg

        # TODO: Technique 6 — Backchannel Sounds (future iteration)
        # Insert short ambient reactions (mm-hmm, uh-huh) during Voice A's longer lines.

    # ---- Export ---------------------------------------------------------
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        if not filename.endswith(".mp3"):
            filename = filename + ".mp3"
        file_path = output_dir / filename
        result.export(str(file_path), format="mp3")
        logger.info(
            "Multi-voice audio saved to '%s' (%d ms, %d lines).",
            file_path,
            len(result),
            len(segments),
        )
        return str(file_path)
    except OSError as exc:
        logger.error("Failed to write audio file '%s': %s", filename, exc)
        return None
    except Exception as exc:
        logger.exception("Unexpected error exporting audio '%s': %s", filename, exc)
        return None
