"""Generate sound effects with ElevenLabs from sfx/ELEVENLABS_LIST.md (the narration is never touched).

    python3 -I blockworld/sfx_gen.py --credits                     how many credits are left this month
    python3 -I blockworld/sfx_gen.py el-tag-pop ep05-yell ...      generate these (skips files that already exist)
    python3 -I blockworld/sfx_gen.py --redo el-tag-pop             make a new version of one

The key is read from ELEVENLABS_API_KEY or ~/.config/elevenlabs/env (ELEVENLABS_API_KEY=...). It is never printed.
Each generation costs credits; the script checks the balance first and stops if fewer than --reserve would remain.
Files are written to sfx/<name>.mp3, trimmed of leading silence and peak-normalised to -1 dBFS.
"""
import json, os, re, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SFX = SKILL / "sfx"
LIST = SFX / "ELEVENLABS_LIST.md"
API = "https://api.elevenlabs.io/v1"
COST = 200                   # approximate credits per generation (ElevenLabs pricing page)
LOOPS = ("-loop",)


def key():
    k = os.environ.get("ELEVENLABS_API_KEY", "")
    f = Path.home() / ".config" / "elevenlabs" / "env"
    if not k and f.exists():
        for line in f.read_text().splitlines():
            if line.startswith("ELEVENLABS_API_KEY="):
                k = line.split("=", 1)[1].strip()
    if not k:
        sys.exit("no ElevenLabs key: set ELEVENLABS_API_KEY or create ~/.config/elevenlabs/env")
    return k


def call(path, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"xi-api-key": key(), "Content-Type": "application/json",
                                          "User-Agent": "block-town-sfx/1.0"},
                                 method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def credits():
    s = json.loads(call("/user/subscription"))
    return s.get("tier"), s["character_limit"] - s["character_count"], s["character_limit"]


def entries():
    """name -> (prompt, seconds) from the markdown tables."""
    out = {}
    for line in LIST.read_text().splitlines():
        m = re.match(r"\|\s*((?:el|ep\d\d)-[\w-]+)\s*\|\s*(.+?)\s*\|\s*([\d.]+)\s*s\s*\|", line)
        if m:
            out[m.group(1)] = (m.group(2), float(m.group(3)))
    return out


def tidy(raw, dst):
    """Trim leading silence, normalise the peak to -1 dBFS, write mp3."""
    tmp = dst.with_suffix(".raw.mp3")
    tmp.write_bytes(raw)
    vol = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    peak = float(re.search(r"max_volume: (-?[\d.]+) dB", vol).group(1)) if "max_volume" in vol else 0.0
    loop = any(t in dst.stem for t in LOOPS)
    trim = "" if loop else "silenceremove=start_periods=1:start_threshold=-45dB,"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-af", f"{trim}volume={-1.0 - peak:.2f}dB",
                    "-ar", "44100", "-b:a", "192k", str(dst)], check=True)
    tmp.unlink()


def generate(name, prompt, secs):
    body = {"text": prompt, "duration_seconds": max(0.5, min(30.0, secs)), "prompt_influence": 0.45}
    if any(t in name for t in LOOPS):
        body["loop"] = True
    try:
        raw = call("/sound-generation?output_format=mp3_44100_128", body)
    except urllib.error.HTTPError as e:
        if body.pop("loop", None) and e.code in (400, 422):
            raw = call("/sound-generation?output_format=mp3_44100_128", body)
        else:
            raise SystemExit(f"{name}: ElevenLabs said {e.code} {e.read()[:300]!r}")
    tidy(raw, SFX / f"{name}.mp3")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    reserve = 2000
    if "--reserve" in args:
        i = args.index("--reserve"); reserve = int(args[i + 1]); del args[i:i + 2]
    tier, left, limit = credits()
    print(f"plan {tier}: {left} of {limit} credits left")
    if args == ["--credits"]:
        return
    redo = "--redo" in args
    names = [a for a in args if not a.startswith("--")]
    table = entries()
    for n in names:
        if n not in table:
            sys.exit(f"{n} is not in {LIST.name}")
    todo = [n for n in names if redo or not (SFX / f"{n}.mp3").exists()]
    need = len(todo) * COST
    if left - need < reserve:
        sys.exit(f"{len(todo)} sounds need about {need} credits; only {left} left (keeping {reserve} in reserve)")
    for n in todo:
        prompt, secs = table[n]
        generate(n, prompt, secs)
        print(f"  made {n}.mp3 ({secs:.1f} s)", flush=True)
    tier, after, _ = credits()
    print(f"done: used {left - after} credits, {after} left")


if __name__ == "__main__":
    main()
