"""Animation helpers and the episode runner. An episode file starts with:  from anim import *

Run an episode through run.py (never directly):
    blender -b --factory-startup --python-exit-code 1 -P <skill>/blockworld/run.py -- EPISODE_DIR MODE [args]
MODE:  check                 no rendering: runs every shot function, prints the shot table and warnings (fast)
       stills [shot ...]     two half-size stills per shot (30% and 85% through) -> EPISODE_DIR/stills/
       frame SECONDS         one half-size still at that time -> EPISODE_DIR/stills/at_<seconds>.jpg
       render [f0 f1]        final frames 1080x1920 -> EPISODE_DIR/frames/f_####.jpg (optionally only a frame range)
       resume                render only the frames that are missing

Nothing is keyframed. Every frame is posed from code: a shot is a function f(t, d, T)
(t = seconds since the shot began, d = the shot's length, T = seconds since the video began).
"""
import json, math, re, sys, wave
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector

import town
from town import (ALL, BOY, DAD, GRAN, HOUSE_Y, KID, LX, MAN, NIA, ROAD, RX, TALL, TEACH, WALK, WIN, banded, box, brick,
                  build_town, character, cylinder, empty, face_names, lin, mat, park, pose, shot, sign_mat, text,
                  time_of_day)

__all__ = [
    # from town
    "ALL", "BOY", "DAD", "GRAN", "HOUSE_Y", "KID", "LX", "MAN", "NIA", "ROAD", "RX", "TALL", "TEACH", "WALK", "WIN",
    "banded", "box", "brick", "build_town", "character", "cylinder", "empty", "face_names", "lin", "mat", "park", "pose",
    "shot", "sign_mat", "text", "time_of_day", "town",
    # from here
    "EP", "FPS", "SCRIPT", "WT", "WE", "widx", "line", "at", "cut", "clamp", "smooth", "back", "snap", "mix", "osc",
    "size", "feet", "card", "put", "over", "eyes", "closeup", "stand", "walk", "run", "math", "Vector",
    "wcut", "wpop", "before_each_frame",
]

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not ARGS:
    raise SystemExit("usage: blender -b --factory-startup -P run.py -- EPISODE_DIR [check|stills|frame|render|resume]")
EP = Path(ARGS[0]).resolve()
MODE = ARGS[1] if len(ARGS) > 1 else "check"
FPS = 30

# ---------------------------------------------------------------- the words and when they are spoken
LINES = [l.split() for l in (EP / "script.txt").read_text().splitlines() if l.strip()]
SCRIPT = [w for l in LINES for w in l]


def _norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))


_times = EP / "vo" / "times.json"
ESTIMATED = not _times.exists()
if ESTIMATED:      # no narration yet: guess at about 250 words a minute so shots can be planned and stills made
    WT, WE, t = [], [], 0.0
    for l in LINES:
        for w in l:
            WT.append(round(t, 3))
            t += 0.11 + 0.028 * len(_norm(w))
            WE.append(round(t, 3))
        t += 0.25
    print("NOTE: vo/times.json not found, word times are ESTIMATED. Make the narration before any final render.")
else:
    _j = json.loads(_times.read_text())
    assert len(_j) == len(SCRIPT), f"times.json has {len(_j)} words, script.txt has {len(SCRIPT)}: run words.py again"
    WT, WE = [w["t0"] for w in _j], [w["t1"] for w in _j]


def widx(word, n=1):
    """Index of a script word. widx(7) -> 7.  widx("lie") -> its first use.  widx("you", 2) -> its second use."""
    if isinstance(word, int):
        return word
    hits = [i for i, w in enumerate(SCRIPT) if _norm(w) == _norm(word)]
    if len(hits) < n:
        raise ValueError(f"the script has {len(hits)} x {word!r}, asked for number {n}")
    return hits[n - 1]


def line(k):
    """Index of the first word of script line k (1-based)."""
    return sum(len(l) for l in LINES[:k - 1])


def at(word, n=1):
    """The time (seconds) a word is spoken. at(7), at("lie"), at("you", 2)."""
    return WT[widx(word, n)]


def cut(word, n=1):
    """Where a shot that starts on this word should begin: 0.04 s before the word."""
    return max(0.0, at(word, n) - 0.04)


# ---------------------------------------------------------------- small maths
def clamp(x):
    return max(0.0, min(1.0, x))


def smooth(x):
    """Soft 0 -> 1. For camera moves over a shot: smooth(t / d)."""
    x = clamp(x)
    return x * x * (3 - 2 * x)


def back(x, s=2.2):
    x = clamp(x) - 1
    return x * x * ((s + 1) * x + s) + 1


def snap(t, t0, d=0.14):
    """0 before t0, then a fast overshooting move to 1. Every pose change and every pop uses this."""
    return back((t - t0) / d) if t >= t0 else 0.0


def mix(a, b, k):
    """Blend two numbers, or two tuples / vectors, by k (0 = a, 1 = b)."""
    if isinstance(a, (tuple, list, Vector)):
        return tuple(x + (y - x) * k for x, y in zip(a, b))
    return a + (b - a) * k


def osc(T, hz, amp, ph=0.0):
    """A sine wobble for breathing, waving and bouncing. Give each character its own ph."""
    return amp * math.sin(2 * math.pi * hz * T + ph)


def size(c, s, squash=1.0):
    """Scale a character (1.0 = 5.3 studs). squash < 1 flattens and widens it for an impact."""
    c["root"].scale = (s / math.sqrt(squash), s / math.sqrt(squash), s * squash)


def feet(s):
    """Tag text for a character of scale s: feet(1.4) -> '7 ft 5'. (1 stud = 1 foot.)"""
    inches = round(s * 5.3 * 12)
    return f"{inches // 12} ft {inches % 12}"


def over(c, gap=0.85):
    """The point gap studs above a character's head, for a tag. Use a small gap (0.15-0.3) over tiny characters."""
    r = c["root"]
    return Vector(r.location) + Vector((0, 0, r.scale[2] * 5.3 + gap))


def eyes(c):
    """The point between a character's eyes (ignores lean), for aiming the camera."""
    r = c["root"]
    return Vector(r.location) + Vector((0, 0, 4.6 * r.scale[2]))


def closeup(c, dist=8.0, fov=36, side=0.6, rise=0.1, key_w=0):
    """Face close-up from in front of a character, whatever its place, direction and size.
    dist / side / rise are in studs for a normal-size person and shrink or grow with the character."""
    r = c["root"]
    s, yaw = r.scale[2], r.rotation_euler[2]
    front, right = Vector((math.sin(yaw), -math.cos(yaw), 0)), Vector((math.cos(yaw), math.sin(yaw), 0))
    e = eyes(c)
    shot(e + (front * dist + right * side + Vector((0, 0, rise))) * s, e + Vector((0, 0, -0.2 * s)), fov, key_w=key_w)


# ---------------------------------------------------------------- cards: tags and bubbles that always face the camera
CARDS = []


def card(lines, sz, col="#FFD84A", bubble=False):
    """A tag (glowing text with a dark outline) or, with bubble=True, a white speech bubble with dark text.
    lines = list of strings. sz = letter height in studs (0.6-0.85 reads well over a normal-size person).
    Create cards once, before the shots. Show one with put() inside a shot function."""
    e = empty("card")
    e.rotation_mode = "QUATERNION"
    n = len(lines)
    for i, ln in enumerate(lines):
        z = ((n - 1) / 2 - i) * sz * 1.2
        if bubble:
            text(ln, sz, (0, -0.06, z), mat("#15151A"), e, extrude=0.0)
        else:
            text(ln, sz, (0, -0.05, z), mat(col, emit=2.0, key=("tag", col)), e, extrude=0.0)
            o = text(ln, sz, (0, 0, z), mat("#0E0E12", key="tagbg"), e, extrude=0.0)
            o.data.offset = sz * 0.09
    if bubble:
        w = max(len(l) for l in lines) * sz * 0.64 + sz * 0.9
        h = n * sz * 1.2 + sz * 0.6
        white = mat("#FFFFFF", emit=1.0, key="bubble")
        box((w, 0.04, h), (0, 0, 0), white, e)
        box((w + 0.18, 0.04, h + 0.18), (0, 0.05, 0), mat("#15151A"), e)
        box((0.5, 0.04, 0.5), (w * 0.22, 0.02, -h / 2), white, e, rot=(0, 45, 0))
    CARDS.append(e)
    return e


def put(c, loc, k=1.0):
    """Show a card at loc, facing the camera, at scale k. Call AFTER shot(). For a pop: put(tag, loc, snap(t, t0))."""
    c.location = loc
    c.scale = (k, k, k)
    c.rotation_quaternion = town.cam.rotation_euler.to_quaternion() @ Quaternion((1, 0, 0), math.radians(-90))


# ---------------------------------------------------------------- stock moves
def stand(c, loc, yaw, face, T, ph=0.0, **kw):
    """A held pose that still breathes. Extra keywords (armL, armR, head, lean, tilt, legL, legR) override the idle."""
    kw.setdefault("armL", (osc(T, 0.5, 2, ph), 5 + osc(T, 0.4, 1.5, ph)))
    kw.setdefault("armR", (osc(T, 0.5, -2, ph), 5 + osc(T, 0.4, 1.5, ph + 1)))
    kw.setdefault("head", (osc(T, 0.33, 3, ph), osc(T, 0.5, 2, ph)))
    pose(c, loc, yaw, face, **kw)


def walk(c, x, y0, way, T, face, ph=0.0, speed=4.5, z=WALK):
    """Walk along the street: way = 1 toward the town hall (+Y), -1 back. Starts at y0 when T = 0. z = ground height.

    The stride is big enough to read on a phone: opposite arms and legs, a forward lean, and a bounce on each step.
    """
    sw = math.sin(2 * math.pi * 2.2 * T + ph)
    s = c["root"].scale[2]
    pose(c, (x, y0 + way * speed * s * T, z + abs(sw) * 0.22 * s), 180 if way > 0 else 0, face,
         armL=(58 * sw, 10), armR=(-58 * sw, 10), legL=-48 * sw, legR=48 * sw, lean=-8, tilt=7 * sw)


# ---------------------------------------------------------------- word-index helpers (the Roblox-look episodes)
def wcut(i):
    """The cut time for script word i (0-based index into script.txt's words): 0.04 s before it is spoken."""
    return round(WT[i] - 0.04, 3)


def wpop(i, d=0.14):
    """0 -> 1 over d seconds as script word i is spoken (the current frame's time). Use it to pop a tag or swap a face:
    put(tag, loc, wpop(25)) or face = "sad" if wpop(84) > 0 else "smile"."""
    return snap(town.NOW, WT[i], d)


RESETS = []


def before_each_frame(fn):
    """Register fn(T), called at the start of every frame before the shot: put props that appear, disappear or move in
    only some shots back to their default state (a poster that goes up later, a box held in one shot)."""
    RESETS.append(fn)
    return fn


# ---------------------------------------------------------------- the runner
def _voice_end():
    wav = EP / "vo" / "voice.wav"
    if wav.exists():
        with wave.open(str(wav)) as w:
            return w.getnframes() / w.getframerate()
    return WE[-1]


def run(shots, end=None, tod="day"):
    """Render the episode. shots = [(name, start_seconds, function), ...] in order; the first starts at 0.0.
    end = total length in seconds (default: 0.5 s after the last spoken word). tod = the default time of day."""
    names = [n for n, _, _ in shots]
    assert len(set(names)) == len(names), "shot names must be unique"
    assert shots[0][1] == 0.0, "the first shot must start at 0.0"
    for a, b in zip(shots, shots[1:]):
        assert b[1] > a[1], f"shot {b[0]!r} starts at {b[1]:.2f}, not after {a[0]!r} ({a[1]:.2f})"
    END = round(WE[-1] + 0.5, 2) if end is None else end
    if (EP / "vo" / "voice.wav").exists() and _voice_end() + 0.05 < WE[-1]:
        print(f"WARNING: voice.wav ends at {_voice_end():.2f}s, before the last word at {WE[-1]:.2f}s")
    assert END > shots[-1][1], "end is before the last shot starts"
    stops = [s[1] for s in shots[1:]] + [END]
    (EP / "shots.json").write_text(json.dumps(
        [{"name": n, "start": round(s, 3)} for n, s, _ in shots] + [{"name": "end", "start": END}], indent=1))

    def frame(T):
        town.NOW = T
        time_of_day(tod)
        for i, c in enumerate(town.CHARACTERS):
            size(c, c["scale"])
            pose(c, loc=(300 + i * 12, -300, 0), face="smile")
        for c in CARDS:
            c.location, c.scale = (300, -320, -50), (0.001,) * 3
        for fn in RESETS:
            fn(T)
        i = max(i for i, s in enumerate(shots) if s[1] <= T + 1e-6)
        shots[i][2](T - shots[i][1], stops[i] - shots[i][1], T)
        face = town.cam.rotation_euler.to_quaternion() @ Quaternion((1, 0, 0), math.radians(-90))
        for c in CARDS:                    # cards face the shot's final camera, even if put() came before shot()
            if c.scale[0] > 0.002:
                c.rotation_quaternion = face
        return i

    def words_in(a, b):
        return " ".join(w for w, t in zip(SCRIPT, WT) if a - 0.05 <= t < b - 0.05)

    if MODE == "check":
        warn = []
        print(f"\n{'#':>3} {'shot':<16}{'start':>7}{'len':>6}  words")
        for i, (n, s, _) in enumerate(shots):
            d = stops[i] - s
            for k in (0.0, 0.3, 0.6, 0.999):
                frame(s + d * k)
            print(f"{i + 1:>3} {n:<16}{s:>7.2f}{d:>6.2f}  {words_in(s, stops[i])}")
            if d > 2.5:
                warn.append(f"shot {n!r} is {d:.2f} s: over 2.5 s, split it or add a second angle")
            if d < 0.5:
                warn.append(f"shot {n!r} is only {d:.2f} s")
        print(f"\n{len(shots)} shots, {END:.2f} s, average {END / len(shots):.2f} s per shot, {math.ceil(END * FPS)} frames"
              + (" (word times ESTIMATED)" if ESTIMATED else ""))
        for w in warn:
            print("WARNING:", w)
        print("check passed: every shot function runs")
    elif MODE in ("stills", "frame"):
        town.setup_render(540, 960, 12)
        (EP / "stills").mkdir(exist_ok=True)
        if MODE == "frame":
            T = float(ARGS[2])
            frame(T)
            town.render_still(EP / "stills" / f"at_{T:07.2f}.jpg")
        else:
            for i, (n, s, _) in enumerate(shots):
                if ARGS[2:] and n not in ARGS[2:]:
                    continue
                for tag, k in (("a", 0.3), ("b", 0.85)):
                    frame(s + (stops[i] - s) * k)
                    town.render_still(EP / "stills" / f"{i + 1:03d}_{n}_{tag}.jpg")
                    print("still", n, tag, flush=True)
    elif MODE in ("render", "resume"):
        if ESTIMATED:
            raise SystemExit("word times are estimated: make the narration (vo.py, words.py) before the final render")
        town.setup_render(1080, 1920, 32)
        (EP / "frames").mkdir(exist_ok=True)
        f0 = int(ARGS[2]) if MODE == "render" and len(ARGS) > 2 else 0
        f1 = int(ARGS[3]) if MODE == "render" and len(ARGS) > 3 else math.ceil(END * FPS) - 1
        for f in range(f0, f1 + 1):
            out = EP / "frames" / f"f_{f:04d}.jpg"
            if MODE == "resume" and out.exists():
                continue
            frame(f / FPS)
            town.render_still(out)
            print("frame", f, "of", f1, flush=True)
    else:
        raise SystemExit(f"unknown mode {MODE!r}: use check, stills, frame, render or resume")
