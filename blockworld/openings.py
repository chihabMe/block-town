"""Opening variants: several versions of the first ~15 s of an episode, so the user can pick the strongest hook.

    python3 -I SKILL/blockworld/openings.py EPISODE new A B C D [--until 15]   make EPISODE/openings/A ... D
    python3 -I SKILL/blockworld/openings.py EPISODE list                     what each variant has so far
    python3 -I SKILL/blockworld/openings.py EPISODE grid                     the drafts in one compare video

`new` makes each variant a small episode folder of its own, so every normal command works on it (check, stills,
render_threejs.sh --draft, finish.py --draft):
  * script.txt  the script's first whole lines that end by --until seconds (default 15)
  * vo/         the same narration, cut after those lines (times.json, lines.json, voice.wav, voice_level.wav)
  * episode.py  a copy of the main episode.py: keep only the hook shots and change them for this variant
  * finish.json, vo_config.json, pictures.json, cues.json (word cues inside the hook only), pictures/ (a link)
A variant that changes the hook's WORDS needs its own voice: edit its script.txt, then vo.py, words.py and
level_voice.py on the variant folder (the free take costs nothing, the paid one needs the user's yes).

When the user picks one, move its shots into the main episode.py (and its lines into script.txt if they changed,
which means a new full voice take), then delete the openings/ folder.
`grid` puts up to four <name>_draft.mp4 next to each other (two: 1080x960, three or four: 2x2 at 1080x1920), lettered, with the first variant's
sound (all variants share the narration unless their words changed: the grid then warns).
"""
import json, shutil, subprocess, sys
from pathlib import Path

FONT = Path(__file__).resolve().parent / "fonts" / "InterDisplay-Black.ttf"


def hook_lines(ep, until):
    lines = [l for l in (ep / "script.txt").read_text().splitlines() if l.strip()]
    times = json.loads((ep / "vo" / "times.json").read_text())
    n_words, k, n = 0, 0, 0
    for i, line in enumerate(lines):
        n += len(line.split())
        if n > len(times):
            sys.exit("times.json has fewer words than script.txt: run words.py again")
        if times[n - 1]["t1"] <= until or i == 0:
            k, n_words = i + 1, n
        else:
            break
    return lines, times, k, n_words


def cut_wav(src, dst, end):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af",
                    f"atrim=0:{end:.3f},afade=t=out:st={max(0, end - 0.04):.3f}:d=0.04,apad=pad_dur=0.6",
                    str(dst)], check=True)


def new(ep, names, until):
    if not (ep / "vo" / "times.json").exists():
        sys.exit("make the voice first (vo.py, words.py): the openings reuse it")
    lines, times, k, n = hook_lines(ep, until)
    end = times[n - 1]["t1"]
    if n < len(times):
        end = min(end + 0.25, max(end, times[n]["t0"] - 0.02))
    print(f"hook = lines 1-{k} ({n} words, ends at {end:.2f} s):")
    for line in lines[:k]:
        print("   ", line)
    root = ep / "openings"
    for name in names:
        d = root / name
        if d.exists():
            sys.exit(f"{d} already exists: delete it or pick another name")
        (d / "vo").mkdir(parents=True)
        (d / "script.txt").write_text("\n".join(lines[:k]) + "\n")
        (d / "vo" / "times.json").write_text(json.dumps(times[:n], indent=0))
        if (ep / "vo" / "lines.json").exists():
            lj = json.loads((ep / "vo" / "lines.json").read_text())
            (d / "vo" / "lines.json").write_text(json.dumps(lj[:k], indent=1))
        for wav in ("voice.wav", "voice_level.wav"):
            if (ep / "vo" / wav).exists():
                cut_wav(ep / "vo" / wav, d / "vo" / wav, end)
        for f in ("finish.json", "vo_config.json", "pictures.json"):
            if (ep / f).exists():
                shutil.copy2(ep / f, d / f)
        if (ep / "cues.json").exists():
            cues = json.loads((ep / "cues.json").read_text())
            keep = [c for c in cues if "word" in c and c["word"] < n]
            dropped = len(cues) - len(keep)
            (d / "cues.json").write_text(json.dumps(keep, indent=1))
            if dropped:
                print(f"  {name}: {dropped} cues after the hook or tied to a shot name were left out")
        if (ep / "pictures").is_dir():
            (d / "pictures").symlink_to((ep / "pictures").resolve(), target_is_directory=True)
        if (ep / "episode.py").exists():
            code = (ep / "episode.py").read_text()
            note = (f'# OPENING VARIANT {name} of {ep.name}: keep only the shots up to {end:.2f} s (word {n - 1} is the\n'
                    f'# last word) and change them for this variant. Shots that use later words will fail `check`.\n')
            (d / "episode.py").write_text(note + code)
        print(f"  made {d}")
    print("next, for each variant: edit episode.py, `check`, stills, render_threejs.sh VARIANT --draft, "
          "finish.py VARIANT --draft, then `openings.py EPISODE grid`")


def variants(ep):
    root = ep / "openings"
    return sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []


def show(ep):
    vs = variants(ep)
    if not vs:
        print("no openings yet: openings.py EPISODE new A B")
    main = (ep / "script.txt").read_text().split()
    for d in vs:
        words = (d / "script.txt").read_text().split()
        same = words == main[:len(words)]
        draft = d / f"{d.name}_draft.mp4"
        print(f"{d.name:6} {len(words):3} words  {'same words' if same else 'NEW WORDS (own voice take)':26}"
              f"shots.json {'yes' if (d / 'shots.json').exists() else 'no ':3}  draft {draft if draft.exists() else '-'}")


def grid(ep):
    vs = [d for d in variants(ep) if (d / f"{d.name}_draft.mp4").exists()][:4]
    if len(vs) < 2:
        sys.exit("need at least two variants with <name>_draft.mp4 (finish.py VARIANT --draft)")
    first = (vs[0] / "script.txt").read_text().split()
    if any((d / "script.txt").read_text().split() != first for d in vs[1:]):
        print("WARNING: the variants' words differ; the grid plays only the first variant's sound")
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for d in vs:
        cmd += ["-i", str(d / f"{d.name}_draft.mp4")]
    parts, labels = [], []
    font = str(FONT).replace(":", "\\:")
    for i, d in enumerate(vs):
        parts.append(f"[{i}:v]scale=540:960,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=30,"
                     f"drawtext=fontfile='{font}':text='{d.name}':x=24:y=24:fontsize=72:fontcolor=white:"
                     f"borderw=6:bordercolor=black[v{i}]")
        labels.append(f"[v{i}]")
    cells = 2 if len(vs) == 2 else 4                     # two side by side (1080x960), else 2x2 (1080x1920)
    for i in range(len(vs), cells):
        parts.append(f"color=c=black:s=540x960:r=30[v{i}]")
        labels.append(f"[v{i}]")
    dur = max(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(d / f"{d.name}_draft.mp4")], capture_output=True, text=True).stdout)
              for d in vs)
    out = ep / "openings" / "OPENINGS_GRID.mp4"
    cmd += ["-filter_complex", ";".join(parts) + ";" + "".join(labels) +
            (f"xstack=inputs=4:layout=0_0|540_0|0_960|540_960[g]" if cells == 4 else "hstack=inputs=2[g]"),
            "-map", "[g]", "-map", "0:a?", "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(out)]
    subprocess.run(cmd, check=True)
    print("wrote", out, "with", ", ".join(d.name for d in vs))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    ep = Path(sys.argv[1]).resolve()
    cmd = sys.argv[2]
    if cmd == "new":
        rest = sys.argv[3:]
        until = 15.0
        if "--until" in rest:
            i = rest.index("--until")
            until = float(rest[i + 1])
            rest = rest[:i] + rest[i + 2:]
        new(ep, rest or ["A", "B"], until)
    elif cmd == "list":
        show(ep)
    elif cmd == "grid":
        grid(ep)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
