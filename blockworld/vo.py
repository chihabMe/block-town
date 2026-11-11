"""Narration for one episode, with the local Kokoro blend. Free and offline.

    python3 blockworld/vo.py EPISODE_DIR

Reads EPISODE_DIR/script.txt (one sentence a line) and EPISODE_DIR/vo_config.json.
Writes EPISODE_DIR/vo/voice_raw.wav, voice.wav and lines.json.
Then run blockworld/words.py on the same folder to make vo/times.json.

vo_config.json:
    {"blend": "af_jessica:3,am_puck:2", "pitch_semitones": 3, "default_speed": 1.3, "default_pause": 0.18,
     "speed": {"1": 1.22}, "pause": {"1": 0.28}}
Keys in speed and pause are 1-based line numbers. Pitch is applied once to the joined track.

Kokoro is not inside this skill. This script uses, in order:
    $KOKORO_PYTHON, then ~/.venvs/kokoro/bin/python, then the current python if it has kokoro_onnx.
Models are expected at ~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx and voices/voices-v1.0.bin.
"""
import json, os, subprocess, sys
from pathlib import Path


def kokoro_python():
    candidates = []
    if os.environ.get("KOKORO_PYTHON"):
        candidates.append(Path(os.environ["KOKORO_PYTHON"]))
    candidates.append(Path.home() / ".venvs/kokoro/bin/python")
    for path in candidates:
        if path.exists() and path.resolve() != Path(sys.executable).resolve():
            return path
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    try:
        import numpy as np
        import soundfile as sf
        from kokoro_onnx import Kokoro
    except ImportError:
        other = kokoro_python()
        if other and not os.environ.get("BLOCKTOWN_VO_TRIED"):
            env = dict(os.environ, BLOCKTOWN_VO_TRIED="1")
            os.execve(str(other), [str(other), __file__, *sys.argv[1:]], env)
        sys.exit("Kokoro is not installed for this python.\n"
                 "Create it once: uv venv ~/.venvs/kokoro && ~/.venvs/kokoro/bin/pip install kokoro-onnx soundfile numpy\n"
                 "Put kokoro-v1.0.onnx and voices-v1.0.bin in ~/.cache/hyperframes/tts/models and .../voices/\n"
                 "Or set KOKORO_PYTHON to a python that already has them.\n"
                 "A voice.wav you already have can be dropped in EPISODE_DIR/vo/ and words.py run on it.")

    ep = Path(sys.argv[1]).resolve()
    cfg = json.loads((ep / "vo_config.json").read_text())
    out = ep / "vo"
    out.mkdir(parents=True, exist_ok=True)
    cache = Path.home() / ".cache/hyperframes/tts"
    model, voices = cache / "models/kokoro-v1.0.onnx", cache / "voices/voices-v1.0.bin"
    if not model.exists() or not voices.exists():
        sys.exit(f"Kokoro files not found:\n  {model}\n  {voices}")
    k = Kokoro(str(model), str(voices))
    parts = [(n, float(w)) for n, w in (p.split(":") for p in cfg["blend"].split(","))]
    weight = sum(w for _, w in parts)
    style = sum(k.get_voice_style(n) * (w / weight) for n, w in parts).astype(np.float32)

    chunks, meta, t, sr = [], [], 0.0, 24000
    lines = [ln.strip() for ln in (ep / "script.txt").read_text().splitlines() if ln.strip()]
    for n, text in enumerate(lines, 1):
        speed = cfg.get("speed", {}).get(str(n), cfg["default_speed"])
        audio, sr = k.create(text, voice=style, speed=speed, lang="en-us")
        pause = cfg.get("pause", {}).get(str(n), cfg["default_pause"])
        meta.append({"n": n, "text": text, "start": round(t, 3), "end": round(t + len(audio) / sr, 3)})
        chunks += [audio, np.zeros(int(pause * sr), dtype=np.float32)]
        t += len(audio) / sr + pause
        print(f"{n:02d} {meta[-1]['start']:6.2f}s  {text}")
    sf.write(out / "voice_raw.wav", np.concatenate(chunks), sr)
    ratio = 2 ** (cfg.get("pitch_semitones", 0) / 12)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out / "voice_raw.wav"),
                    "-af", f"rubberband=pitch={ratio}", str(out / "voice.wav")], check=True)
    (out / "lines.json").write_text(json.dumps(meta, indent=1))
    print(f"total {t:.2f}s  wrote {out / 'voice.wav'}")
    print("next: python3 blockworld/words.py", ep)


if __name__ == "__main__":
    main()
