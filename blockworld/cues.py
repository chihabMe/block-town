"""Write cues.json from a readable cue list that names words instead of word numbers.

    python3 -I SKILL/blockworld/cues.py EPISODE cues_spec.json      -> EPISODE/cues.json (prints every cue's time)

The spec is a JSON list. Each entry is a cue for finish.py, with "say" instead of "word":
    {"sfx": "el-tag-pop.mp3", "say": "even", "volume": 0.45}
    {"sfx": "el-no-signal.mp3", "say": "zero", "after": "held", "volume": 0.28}      the first "zero" after "held"
    {"sfx": "ep05-yell.mp3", "say": "yelled", "nth": 2, "volume": 0.5}              the second "yelled"
    {"sfx": "el-whoosh-cut.mp3", "shot": "s05", "offset": -0.08, "volume": 0.22}      at a cut
    {"sfx": "el-street-day-loop.mp3", "shot": "s01", "until": "end", "volume": 0.07}  a bed looped to the "end" mark
    {"sfx": "el-spinner-loop.mp3", "shot": "s17", "until": "s18", "volume": 0.22}     ...or to the next shot
Words match without punctuation or case. A word that is not in script.txt stops with a clear error.
Volumes are relative to the voice when finish.json has "loudness": "static" (docs/SOUND.md).
"""
import json, sys
from pathlib import Path


def norm(w):
    return w.strip(".,?!:;\"'()").lower()


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    ep = Path(sys.argv[1]).resolve()
    spec_path = Path(sys.argv[2])
    spec_path = spec_path if spec_path.is_absolute() else ep / spec_path
    words = [norm(w) for w in (ep / "script.txt").read_text().split()]
    shots = {s["name"]: s["start"] for s in json.loads((ep / "shots.json").read_text())}
    times = json.loads((ep / "vo" / "times.json").read_text())
    out = []
    for c in json.loads(spec_path.read_text()):
        c = dict(c)
        if "say" in c:
            start = 0
            if "after" in c:
                a = norm(c.pop("after"))
                if a not in words:
                    sys.exit(f"'{a}' (after) is not in script.txt: {c}")
                start = words.index(a)
            hits = [i for i in range(start, len(words)) if words[i] == norm(c["say"])]
            nth = int(c.pop("nth", 1))
            if len(hits) < nth:
                sys.exit(f"'{c['say']}' (#{nth}) is not in script.txt after word {start}: {c}")
            c["word"] = hits[nth - 1]
            c.pop("say")
        if "until" in c:
            until = c.pop("until")
            if "shot" not in c or until not in shots:
                sys.exit(f"'until' needs a shot and a shot name or 'end' from shots.json: {c}")
            c["length"] = round(shots[until] - shots[c["shot"]] - float(c.get("offset", 0)), 2)
        out.append(c)
        t = times[c["word"]]["t0"] if "word" in c else shots[c["shot"]]
        print(f"  {t + float(c.get('offset', 0)):6.2f}s  {c['volume']:4.2f}  {c['sfx']}"
              + (f"  (loops {c['length']} s)" if "length" in c else ""))
    (ep / "cues.json").write_text(json.dumps(out, indent=1))
    print(f"wrote {ep / 'cues.json'}: {len(out)} cues, {len({c['sfx'] for c in out})} sounds")


if __name__ == "__main__":
    main()
