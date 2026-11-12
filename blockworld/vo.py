"""Narration for one episode, with the local Kokoro blend. Free and offline.

    python3 blockworld/vo.py EPISODE_DIR

Reads EPISODE_DIR/script.txt (one sentence a line) and EPISODE_DIR/vo_config.json.
Writes EPISODE_DIR/vo/voice_raw.wav, voice.wav and lines.json.
Then run blockworld/words.py on the same folder to make vo/times.json.

Two engines, picked by "engine" in vo_config.json:

  "fish"   (recommended) the niche's narrator voice, Fish Audio community voice "Roblox", through OpenRouter.
           Scores 0.95-0.97 against the niche voice. The whole script is sent as ONE take, so it sounds like one
           recording. No pitch or speed change. Needs OPENROUTER_API_KEY (environment or ~/.env); never printed.
      {"engine": "fish", "voice": "eb4bcc6dbb634e9eaee239c94266935e", "model": "fish-audio/s2.1-pro-free:free"}
           The :free model is for tests. Fish Audio's terms limit free use to non-commercial work, so make the take
           you post with "model": "fish-audio/s2.1-pro" (paid, about $0.04 per 2-minute script). Ask before paying.
           "say": {"Nia": "Nee-ah"} respells words in the text sent to the voice only (script.txt stays as it is).
           Then the take is made to sound like the top videos (measured on 8 of them, 2026-11-12):
           "tighten": true    cuts every pause down to 0.05 s: they have 0-9% silence and almost no pauses
           "presence_db": 4.5 a treble lift above 2.5 kHz: their voices are brighter than the raw Fish take

  "kokoro" (default, free and offline, scores about 0.85-0.88):
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


def openrouter_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    env = Path.home() / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("OPENROUTER_API_KEY is not set (environment or ~/.env). Get a key at openrouter.ai.")


def fish(ep, cfg):
    import re, urllib.error, urllib.request
    out = ep / "vo"
    out.mkdir(parents=True, exist_ok=True)
    lines = [ln.strip() for ln in (ep / "script.txt").read_text().splitlines() if ln.strip()]
    text = " ".join(lines)
    for word, said in cfg.get("say", {}).items():
        text = re.sub(rf"\b{re.escape(word)}\b", said, text)
    model = cfg.get("model", "fish-audio/s2.1-pro-free:free")
    body = json.dumps({"model": model, "input": text, "voice": cfg.get("voice", "eb4bcc6dbb634e9eaee239c94266935e"),
                       "response_format": "mp3"}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/audio/speech", data=body,
                                 headers={"Authorization": f"Bearer {openrouter_key()}", "Content-Type": "application/json"})
    print(f"one take, {len(text)} characters, model {model}")
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            (out / "voice_raw.mp3").write_bytes(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"OpenRouter said {e.code}: {e.read()[:300].decode(errors='replace')}")
    af = []
    if cfg.get("tighten", True):
        af.append("silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.08"
                  ":stop_threshold=-42dB:stop_silence=0.05")
    if cfg.get("presence_db", 4.5):
        af.append(f"highshelf=f=2500:g={float(cfg.get('presence_db', 4.5))}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out / "voice_raw.mp3"),
                    *(["-af", ",".join(af)] if af else []), "-ar", "44100", "-ac", "1", str(out / "voice.wav")], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(out / "voice.wav")], capture_output=True, text=True).stdout)
    words = len(" ".join(lines).split())
    (out / "lines.json").write_text(json.dumps([{"n": n, "text": t} for n, t in enumerate(lines, 1)], indent=1))
    print(f"total {dur:.2f}s, {words / dur * 60:.0f} words a minute  wrote {out / 'voice.wav'}")
    print("next: python3 blockworld/words.py", ep)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ep0 = Path(sys.argv[1]).resolve()
    cfg0 = json.loads((ep0 / "vo_config.json").read_text())
    if cfg0.get("engine") == "fish":
        return fish(ep0, cfg0)
    if cfg0.get("engine", "kokoro") != "kokoro":
        sys.exit(f"vo_config.json engine must be 'fish' or 'kokoro', not {cfg0['engine']!r}")
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
