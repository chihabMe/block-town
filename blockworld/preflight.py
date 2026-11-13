"""Before rendering: is everything there? Checks the machine, the keys (only whether they are set, never their value)
and the episode's files, and says what to run for anything missing.

    python3 -I SKILL/blockworld/preflight.py EPISODE            everything up to the draft render
    python3 -I SKILL/blockworld/preflight.py EPISODE --final    also what the final render needs (music file, paid take)

Exit code 1 if something needed is missing. Optional things (ElevenLabs, music) are listed but do not fail the check.
"""
import json, os, re, shutil, sys, wave
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
BW = SKILL / "blockworld"
HOME = Path.home()
rows, failed = [], []


def row(ok, what, fix="", need=True):
    mark = "ok " if ok else ("XX " if need else "-- ")
    rows.append(f"  {mark} {what}" + ("" if ok or not fix else f"   -> {fix}"))
    if not ok and need:
        failed.append(what)


def key_set(*names):
    if any(os.environ.get(n) for n in names):
        return True
    env = HOME / ".env"
    if env.exists():
        text = env.read_text(errors="ignore")
        return any(re.search(rf"^{n}=\S", text, re.M) for n in names)
    return False


def chrome():
    tries = [os.environ.get("CHROME"), "/usr/bin/google-chrome-stable", "/usr/bin/google-chrome", "/usr/bin/chromium",
             "/usr/bin/chromium-browser", "/snap/bin/chromium",
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    return next((p for p in tries if p and Path(p).exists()), None)


def machine():
    rows.append("machine")
    for tool in ("blender", "ffmpeg", "ffprobe", "node", "npm"):
        row(bool(shutil.which(tool)), tool, f"install {tool}")
    row(bool(chrome()), "Chrome or Chromium", "install it or set CHROME=/path")
    row((BW / "threejs" / "node_modules" / "three").is_dir(), "three.js packages",
        "render_threejs.sh installs them on first use", need=False)
    cli = os.environ.get("WHISPER_CLI") or shutil.which("whisper-cli") or \
        (HOME / ".cache/hyperframes/whisper/whisper.cpp/build/bin/whisper-cli")
    row(Path(cli).exists(), "whisper-cli (word times)", "set WHISPER_CLI")
    model = Path(os.environ.get("WHISPER_MODEL") or HOME / ".cache/hyperframes/whisper/models/ggml-small.en.bin")
    row(model.exists(), "whisper model", "set WHISPER_MODEL to ggml-small.en.bin")
    row((BW / "fonts" / "InterDisplay-Black.ttf").exists(), "caption font")
    rows.append("keys (set or not; values are never read out)")
    row(key_set("OPENROUTER_API_KEY"), "OPENROUTER_API_KEY (Fish voice)", "add it to ~/.env")
    row(key_set("SOUND_KEY", "ELEVENLABS_API_KEY"), "ElevenLabs key (sound effects)",
        "optional: Pixabay sounds in sfx/ work without it", need=False)


def episode(ep, final):
    rows.append(f"episode {ep}")
    script = ep / "script.txt"
    row(script.exists(), "script.txt", "gate 2")
    if not script.exists():
        return
    words = script.read_text().split()
    vo = ep / "vo"
    row((ep / "vo_config.json").exists(), "vo_config.json", "copy examples/ep05-wifi/vo_config.json")
    row((vo / "voice.wav").exists(), "vo/voice.wav", "vo.py EPISODE")
    times = vo / "times.json"
    if times.exists():
        n = len(json.loads(times.read_text()))
        row(n == len(words), f"vo/times.json matches the script ({n} of {len(words)} words)",
            "words.py EPISODE (the script changed after the voice)")
    else:
        row(False, "vo/times.json", "words.py EPISODE")
    conf = json.loads((ep / "finish.json").read_text()) if (ep / "finish.json").exists() else {}
    row(bool(conf), "finish.json", 'copy examples/ep05-wifi/finish.json')
    voice = ep / conf.get("voice", "vo/voice.wav")
    row(voice.exists(), f"narration for the mix ({voice.relative_to(ep)})", "level_voice.py EPISODE")
    if voice.exists() and times.exists():
        with wave.open(str(voice)) as w:
            length = w.getnframes() / w.getframerate()
        last = json.loads(times.read_text())[-1]["t1"]
        row(length + 0.05 >= last, f"narration covers the last word ({length:.1f} s vs {last:.1f} s)",
            "the voice file is older than times.json: run level_voice.py again")
    if (ep / "pictures.json").exists():
        names = json.loads((ep / "pictures.json").read_text()).keys()
        missing = [n for n in names if not (ep / "pictures" / f"{n}.png").exists()]
        row(not missing, f"pictures drawn ({len(names) - len(missing)} of {len(names)})", "pictures.py EPISODE")
    row((ep / "episode.py").exists(), "episode.py", "gate 5")
    shots = ep / "shots.json"
    fresh = shots.exists() and (ep / "episode.py").exists() and \
        shots.stat().st_mtime >= (ep / "episode.py").stat().st_mtime
    row(fresh, "shots.json newer than episode.py", "run `check`")
    sc = ep / "still_check.txt"
    if sc.exists():
        text = sc.read_text().strip()
        bad = [] if text.lower().startswith("no problems") else [l for l in text.splitlines() if l.strip()]
        row(not bad, f"still_check.txt clean ({len(bad)} lines to fix)" if bad else "still_check.txt clean",
            "fix the shots it lists, run `check` again")
    else:
        row(False, "still_check.txt", "run `check` (call focus() in every shot)", need=False)
    if (ep / "cues.json").exists():
        cues = json.loads((ep / "cues.json").read_text())
        gone = sorted({c["sfx"] for c in cues if not (SKILL / "sfx" / c["sfx"]).exists()})
        row(not gone, f"sound files for cues.json ({len(cues)} cues)", "missing: " + ", ".join(gone[:5]))
    else:
        row(False, "cues.json", "cues.py EPISODE cues_spec.json", need=False)
    if final:
        rows.append("final render")
        music = conf.get("music")
        if music:
            song = Path(music).expanduser()
            song = song if song.is_absolute() else ep / song
            row(song.exists(), f"music file {song.name}", "fix finish.json music")
        else:
            row(False, "music file", "none set: only the clean MP4 will be written", need=False)
        vc = json.loads((ep / "vo_config.json").read_text()) if (ep / "vo_config.json").exists() else {}
        row(":free" not in vc.get("model", ""), "voice is the paid take",
            "the free Fish take is for tests; ask the user before paying for the posting take", need=False)
        row(int(conf.get("render_fps", 30)) > 30, f"finish.json render_fps {conf.get('render_fps', 30)}",
            'set "render_fps": 240, "blur": 4 for 60 fps with motion blur', need=False)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    machine()
    episode(Path(sys.argv[1]).resolve(), "--final" in sys.argv)
    print("\n".join(rows))
    print("\nready" if not failed else f"\nnot ready: {len(failed)} missing")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
