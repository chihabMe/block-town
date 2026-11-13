"""Even out the narration: every sentence at the same loudness, so the voice never seems to drop mid-video.

    python3 -I blockworld/level_voice.py EPISODE_DIR            writes vo/voice_level.wav, prints each sentence's change

Only the level changes (one smooth gain per sentence, ramped in the pauses); the voice itself is untouched.
Use it from finish.json: {"voice": "vo/voice_level.wav"}.
"""
import json, sys, wave
from pathlib import Path

import numpy as np

MAX_DB = 4.0          # never push a sentence more than this up or down
RAMP = 0.08           # seconds of gain change, placed in the pause before a sentence


def level_db(x, sr):
    """Loudness of speech in dB: RMS over the 50 ms windows that are not silence."""
    n = int(sr * 0.05)
    if len(x) < n:
        return None
    win = x[: len(x) // n * n].reshape(-1, n)
    rms = np.sqrt((win ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    loud = db[db > db.max() - 30]
    return float(10 * np.log10((10 ** (loud / 10)).mean())) if len(loud) else None


def main():
    ep = Path(sys.argv[1]).resolve()
    src, dst = ep / "vo" / "voice.wav", ep / "vo" / "voice_level.wav"
    words = json.loads((ep / "vo" / "times.json").read_text())
    with wave.open(str(src)) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw != 2 or ch != 1:
        sys.exit("expects 16-bit mono narration")
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768

    sentences, cur = [], []
    for wd in words:
        cur.append(wd)
        if wd["w"].rstrip('"').endswith((".", "?", "!", ":")):
            sentences.append(cur); cur = []
    if cur:
        sentences.append(cur)
    spans = [(s[0]["t0"], s[-1]["t1"], " ".join(w["w"] for w in s)) for s in sentences]
    levels = [level_db(x[int(a * sr):int(b * sr)], sr) for a, b, _ in spans]
    target = float(np.median([l for l in levels if l is not None]))

    gain = np.ones_like(x)
    prev_end, prev_g = 0.0, 1.0
    for (a, b, text), lv in zip(spans, levels):
        db = 0.0 if lv is None else float(np.clip(target - lv, -MAX_DB, MAX_DB))
        g = 10 ** (db / 20)
        r0 = max(prev_end, a - RAMP)                  # ramp inside the pause before this sentence
        i0, i1 = int(r0 * sr), int(a * sr)
        if i1 > i0:
            gain[i0:i1] = np.linspace(prev_g, g, i1 - i0)
        gain[i1:] = g
        prev_end, prev_g = b, g
        print(f"{a:6.2f}-{b:6.2f}s  {lv if lv is not None else float('nan'):6.1f} dB -> {db:+4.1f} dB  {text[:50]}")
    y = x * gain
    peak = np.abs(y).max()
    if peak > 0.97:
        y *= 0.97 / peak
    with wave.open(str(dst), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"target {target:.1f} dB; wrote {dst}")


if __name__ == "__main__":
    main()
