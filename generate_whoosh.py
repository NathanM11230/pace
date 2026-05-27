"""
Generate the Pace brand transition sound — a calming windchime chirp.

Four chime tones in a G major pentatonic spread (G5, A5, C6, E6), struck gently
in sequence like a light breeze moving through chimes. Long natural decay, warm
spatial reverb tail.

Run once:
    python generate_whoosh.py
"""

from pathlib import Path

import numpy as np
from pydub import AudioSegment

# ---------------------------------------------------------------------------
# Wire pydub to bundled ffmpeg
# ---------------------------------------------------------------------------
try:
    import imageio_ffmpeg
    _ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    AudioSegment.converter = _ffmpeg_exe
    AudioSegment.ffmpeg = _ffmpeg_exe
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
SR          = 44100
DURATION    = 1.40   # longer — let all four chimes breathe and overlap
TARGET_DBFS = -10

OUTPUT_PATH = Path("audio_files/whoosh.mp3")

# ---------------------------------------------------------------------------
# Tube-chime synthesis (inharmonic free-bar partials)
# Softer upper partials and slower decays = warmer, more soothing ring
# ---------------------------------------------------------------------------
PARTIALS       = [1.000, 2.756, 5.404, 8.933]
PARTIAL_AMPS   = [1.00,  0.35,  0.12,  0.04]   # gentler upper partials
PARTIAL_DECAYS = [2.8,   6.5,   13.0,  22.0]   # slower decay = longer ring


def chime_tone(fundamental_hz: float, duration_s: float, sr: int) -> np.ndarray:
    n = int(sr * duration_s)
    t = np.linspace(0.0, duration_s, n, endpoint=False)
    tone = np.zeros(n)
    for ratio, amp, decay in zip(PARTIALS, PARTIAL_AMPS, PARTIAL_DECAYS):
        freq = fundamental_hz * ratio
        if freq >= sr / 2:
            continue
        tone += amp * np.exp(-decay * t) * np.sin(2.0 * np.pi * freq * t)
    # 2 ms soft mallet attack
    attack_n = int(0.002 * sr)
    tone[:attack_n] *= np.linspace(0.0, 1.0, attack_n)
    return tone


# ---------------------------------------------------------------------------
# Four chimes: G5, A5, C6, E6 — G major pentatonic, ascending like a breeze
# (freq_hz, offset_seconds, relative_amplitude)
# ---------------------------------------------------------------------------
CHIMES = [
    (784.0,  0.000, 1.00),   # G5 — warm, grounding
    (880.0,  0.095, 0.90),   # A5
    (1047.0, 0.200, 0.85),   # C6
    (1319.0, 0.310, 0.75),   # E6 — bright, airy top note
]

n_total = int(SR * DURATION)
result  = np.zeros(n_total)

for freq, offset_s, amp in CHIMES:
    offset_n = int(offset_s * SR)
    tone = chime_tone(freq, DURATION, SR) * amp
    end_n = min(offset_n + len(tone), n_total)
    result[offset_n:end_n] += tone[:end_n - offset_n]

# ---------------------------------------------------------------------------
# Spatial reverb — multiple early reflections for an open-air feel
# ---------------------------------------------------------------------------
reflections = [
    (0.018, 0.30),
    (0.038, 0.18),
    (0.062, 0.10),
    (0.095, 0.06),
]
dry = result.copy()
for delay_s, gain in reflections:
    d = int(delay_s * SR)
    result[d:] += dry[:-d] * gain

# ---------------------------------------------------------------------------
# Final fade-out over the last 250 ms
# ---------------------------------------------------------------------------
fade_n = int(0.25 * SR)
result[-fade_n:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade_n)))

# ---------------------------------------------------------------------------
# Normalize to target dBFS
# ---------------------------------------------------------------------------
target_amp = 10 ** (TARGET_DBFS / 20)
peak = np.max(np.abs(result))
if peak > 0:
    result = result * (target_amp / peak)

result_pcm = (result * 32767).astype(np.int16)

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

seg = AudioSegment(
    result_pcm.tobytes(),
    frame_rate=SR,
    sample_width=2,
    channels=1,
)
seg.export(str(OUTPUT_PATH), format="mp3")
print(f"Chime saved to: {OUTPUT_PATH.resolve()}  ({len(seg)} ms)")
