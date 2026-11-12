"""Does a narration sound like the top "in this town" videos?   python3 -I SKILL/blockworld/voice_check.py EPISODE

Measures EPISODE/vo/voice.wav (with vo/times.json for the word count) and compares it with the ranges measured on 8
viral narrations (2026-11-12). Needs numpy. This checks pace and sound, not who the voice is: the voice itself is
fixed by vo_config.json (docs/VOICE.md)."""
import json, sys, wave
from pathlib import Path
import numpy as np

VIRAL = {  # measured on 8 viral narrations: low, high
    "words per minute": (231, 298),
    "silence %": (0, 9),
    "pauses over 0.25 s per minute": (0, 3),
    "brightness (spectral centroid, Hz)": (1680, 1980),
}
ep = Path(sys.argv[1]).resolve()
with wave.open(str(ep / "vo" / "voice.wav")) as w:
    sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
    raw = np.frombuffer(w.readframes(n), dtype={2: np.int16, 4: np.int32}[sw]).astype(np.float32)
y = raw.reshape(-1, ch).mean(axis=1)
y /= max(1e-9, np.abs(y).max())
if sr != 16000:                                    # resample by linear interpolation, enough for these measures
    t = np.arange(0, len(y) / sr, 1 / 16000)
    y = np.interp(t, np.arange(len(y)) / sr, y)
    sr = 16000
hop, win = 256, 1024
frames = np.lib.stride_tricks.sliding_window_view(y, win)[::hop]
rms = np.sqrt((frames ** 2).mean(axis=1))
db = 20 * np.log10(rms + 1e-9)
speech = db > db.max() - 32
idx = np.flatnonzero(speech)
first, last = idx[0], idx[-1]
active = speech[first:last + 1]
total = (last - first + 1) * hop / sr
gaps, run = [], 0
for v in active:
    if not v:
        run += 1
    elif run:
        gaps.append(run * hop / sr); run = 0
words = len(json.loads((ep / "vo" / "times.json").read_text()))
spec = np.abs(np.fft.rfft(frames * np.hanning(win), axis=1))
freqs = np.fft.rfftfreq(win, 1 / sr)
centroid = (spec * freqs).sum(axis=1) / (spec.sum(axis=1) + 1e-9)
ours = {
    "words per minute": words / total * 60,
    "silence %": 100 * (1 - active.mean()),
    "pauses over 0.25 s per minute": sum(g >= 0.25 for g in gaps) / total * 60,
    "brightness (spectral centroid, Hz)": float(np.median(centroid[speech])),
}
ok = True
print(f"{'':36} {'this take':>10}   viral range")
for k, (lo, hi) in VIRAL.items():
    good = lo * 0.95 <= ours[k] <= hi * 1.05 or (k != "words per minute" and k != "brightness (spectral centroid, Hz)"
                                               and ours[k] <= hi)
    ok &= good
    print(f"{k:36} {ours[k]:10.0f}   {lo}-{hi}  {'ok' if good else 'OFF'}")
print("matches the viral sound" if ok else "outside the viral range: see docs/VOICE.md (tighten, presence_db, tempo).\n"
      "A slow, scary script may sit under 231 words a minute on purpose.")
