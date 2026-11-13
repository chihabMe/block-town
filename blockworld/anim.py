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
import json, math, os, re, sys, time, wave
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector

import life
import stillcheck
import town
from stillcheck import focus
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
    "size", "feet", "card", "put", "over", "eyes", "closeup", "stand", "walk", "walk_dir", "run", "math", "Vector",
    "wcut", "wpop", "before_each_frame", "focus",
    # action moves (ep09)
    "sprint", "fall", "sit", "clap", "cheer", "gasp", "look_up", "drum", "juggle", "magic", "see_through", "dof",
]

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not ARGS:
    raise SystemExit("usage: blender -b --factory-startup -P run.py -- EPISODE_DIR [check|stills|frame|render|resume]")
EP = Path(ARGS[0]).resolve()
MODE = ARGS[1] if len(ARGS) > 1 else "check"
FPS = int(os.environ.get("BT_FPS", "30"))   # 240 for the motion-blur render (finish.json "render_fps")
LIFE = os.environ.get("BT_LIFE") == "1"   # extra motion layer, see life.py

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


# ---------------------------------------------------------------- action moves (ep09: the camera and pose pack)
def _fwd(yaw):
    """The direction a character faces for a yaw (0 = -Y)."""
    a = math.radians(yaw)
    return Vector((math.sin(a), -math.cos(a), 0.0))


def walk_dir(c, start, yaw, t, face, ph=0.0, speed=4.5):
    """Walk in any direction: from start (x, y, z) the way yaw faces (0 = -Y, 90 = +X), t seconds after setting off.
    Same stride as walk(). Handy with place marks: walk_dir(c, p.spot("door"), p.yaw("door"), t, "happy")."""
    sw = math.sin(2 * math.pi * 2.2 * t + ph)
    s = c["root"].scale[2]
    p = Vector(start) + _fwd(yaw) * speed * s * t
    pose(c, (p.x, p.y, start[2] + abs(sw) * 0.22 * s), yaw, face,
         armL=(58 * sw, 10), armR=(-58 * sw, 10), legL=-48 * sw, legR=48 * sw, lean=-8, tilt=7 * sw)


def sprint(c, x, y0, way, T, face="scared", ph=0.0, speed=11.0, z=WALK, arms_up=False):
    """Run (twice walk's speed, a deep lean, big arm pumps, a hop on every stride). way = 1 toward +Y, -1 back.
    arms_up=True runs with both hands over the head (cats falling from the sky)."""
    sw = math.sin(2 * math.pi * 3.2 * T + ph)
    s = c["root"].scale[2]
    arms = ((165, 25 + 10 * sw), (165, 25 - 10 * sw)) if arms_up else ((80 * sw, 12), (-80 * sw, 12))
    pose(c, (x, y0 + way * speed * s * T, z + abs(sw) * 0.55 * s), 180 if way > 0 else 0, face,
         armL=arms[0], armR=arms[1], legL=-62 * sw, legR=62 * sw, lean=-20, tilt=5 * sw)


def fall(c, loc, yaw, face, k, T=0.0):
    """Trip and fall flat on the face: k = 0 standing, 1 lying on the ground (use smooth or back for k).
    Arms fly forward, one leg kicks up, a small bounce when he lands."""
    k = clamp(k)
    land = max(0.0, k - 0.85) / 0.15
    bounce = 0.25 * math.sin(min(1.0, land) * math.pi) if k > 0.85 else 0.0
    s = c["root"].scale[2]
    f = _fwd(yaw)
    p = Vector(loc) + f * (1.4 * s * k) + Vector((0, 0, (-1.45 * k + bounce) * s))
    pose(c, tuple(p), yaw, face, armL=(160 * k, 25), armR=(150 * k, 15), legL=-20 * k, legR=-60 * k,
         head=(0, 40 * k), lean=-88 * k)


def sit(c, loc, yaw, face, T, ph=0.0, **kw):
    """Sit on a chair whose seat is at loc's z + 2 (the hall's seats): legs straight ahead, hands on the knees.
    Extra keywords (armL, armR, head, lean) override, e.g. sit(..., armR=(170, 20)) to raise a hand."""
    kw.setdefault("armL", (55 + osc(T, 0.5, 2, ph), 8))
    kw.setdefault("armR", (55 + osc(T, 0.5, -2, ph), 8))
    kw.setdefault("head", (osc(T, 0.33, 4, ph), osc(T, 0.5, 2, ph)))
    pose(c, loc, yaw, face, legL=88, legR=88, **kw)


def clap(c, loc, yaw, face, T, ph=0.0, seated=False, hz=3.2):
    """Clap in front of the chest, hands meeting about hz times a second."""
    o = 22 * abs(math.sin(math.pi * hz * T + ph))
    kw = dict(armL=(78, -24 + o), armR=(78, -24 + o), head=(osc(T, 0.4, 5, ph), 6))
    (sit if seated else stand)(c, loc, yaw, face, T, ph, **kw)


def cheer(c, loc, yaw, face, T, ph=0.0, seated=False):
    """Both arms up and waving, a little jump (standing) or a bounce in the seat."""
    w = math.sin(2 * math.pi * 2.4 * T + ph)
    hop = abs(math.sin(2 * math.pi * 1.6 * T + ph)) * (0.25 if seated else 0.7) * c["root"].scale[2]
    kw = dict(armL=(165, 28 + 12 * w), armR=(165, 28 - 12 * w), head=(0, 12))
    l = Vector(loc) + Vector((0, 0, hop))
    (sit if seated else stand)(c, tuple(l), yaw, face, T, ph, **kw)


def gasp(c, loc, yaw, k, T, ph=0.0, seated=False, face="shock"):
    """Hands fly to the cheeks and the body jolts back: k 0 -> 1 (use wpop or snap)."""
    k = clamp(k)
    kw = dict(armL=(mix(5, 150, k), mix(5, -32, k)), armR=(mix(5, 150, k), mix(5, -32, k)), head=(0, 8 * k),
              lean=10 * k)
    (sit if seated else stand)(c, loc, yaw, face, T, ph, **kw)


def look_up(c, loc, yaw, face, T, k=1.0, ph=0.0, point=False):
    """Look straight up at the sky (the narrator): head back, a step back, one arm pointing up if point."""
    k = clamp(k)
    kw = dict(head=(osc(T, 0.3, 3, ph), 55 * k), lean=12 * k)
    if point:
        kw["armR"] = (mix(5, 165, k), 10)
    stand(c, loc, yaw, face, T, ph, **kw)


def drum(c, loc, yaw, face, T, bpm=240, ph=0.0):
    """Sit behind drum_kit() and hit it: sticks come down in turn on every beat, the head bangs on the beat."""
    b = 2 * math.pi * (bpm / 60.0) * T / 2 + ph
    l, r = abs(math.sin(b)), abs(math.cos(b))
    pose(c, loc, yaw, face, legL=80, legR=80, armL=(40 + 50 * l, 10), armR=(40 + 50 * r, 10),
         head=(0, -8 + 10 * abs(math.sin(2 * b))), lean=-6)


def juggle(c, loc, yaw, face, T, balls, hz=1.1, height=4.5, ph=0.0, drop=None):
    """Juggle: balls (from rprops.ball) loop between the hands in a cascade, the arms toss in turn.
    drop = (ball index, seconds since it slipped): that ball falls to the floor and bounces away."""
    n = len(balls)
    s = c["root"].scale[2]
    f = _fwd(yaw)
    side = Vector((f.y * -1, f.x, 0)) * -1                      # the character's armR side when facing the camera
    base = Vector(loc) + Vector((0, 0, 3.0 * s)) + f * 1.2 * s
    toss = math.sin(2 * math.pi * hz * n / 2 * T + ph)
    stand(c, loc, yaw, face, T, ph, armL=(70 + 25 * max(0, toss), -5), armR=(70 + 25 * max(0, -toss), -5),
          head=(0, 30))
    for i, b in enumerate(balls):
        u = (hz * T + i / n) % 1.0                              # 0 -> 1 around the loop
        x = math.cos(2 * math.pi * u) * 1.3 * s
        z = max(0.0, math.sin(2 * math.pi * u)) * height * s
        p = base + side * x + Vector((0, 0, z))
        if drop and drop[0] == i and drop[1] >= 0:
            tt = drop[1]
            zz = max(0.0, p.z - 0.5 * 30 * tt * tt)
            if zz <= Vector(loc).z + 0.45:                     # on the floor: roll off forward
                zz = Vector(loc).z + 0.45 + 0.6 * abs(math.sin(6 * tt)) * math.exp(-3 * tt)
            p = Vector((p.x, p.y, zz)) + f * 3.0 * tt
        b.location = p


def magic(c, loc, yaw, face, T, k, ph=0.0):
    """The magic reveal: the cap comes off in the right hand and goes up high (k 0 -> 1). Parent a rabbit to the cap
    first: rprops.rabbit(parent=cap_object). Returns nothing; the cap rides on the hand."""
    k = clamp(k)
    stand(c, loc, yaw, face, T, ph, armR=(mix(10, 170, k), 12), armL=(mix(5, 60, k), 30 * k), head=(-10 * k, 20 * k))


def dof(k=1.0):
    """Background blur for this shot (world v2 renderer): 0 = everything sharp, 1 = full blur. Without it, a shot that
    calls focus(character) blurs by distance on its own: close-ups a lot, wide shots not at all."""
    town.DOF = k


_GHOST_UNDO = []          # (object, slot, material) and (object, None, hide_render) to put back at the next frame


def _ghost_undo(T):
    for o, i, v in reversed(_GHOST_UNDO):
        if i is None:
            o.hide_render = v
        else:
            o.data.materials[i] = v
    _GHOST_UNDO.clear()


def see_through(c, k):
    """Draw a character see-through: k = 1 solid, 0.35 a ghost nobody notices. Call it inside a shot AFTER the pose
    (stand / walk / pose set the face again). Every frame starts solid. Printed decals (shirt prints) hide meanwhile."""
    k = round(clamp(k) * 20) / 20
    if k >= 1:
        return
    if _ghost_undo not in RESETS:
        before_each_frame(_ghost_undo)
    for o in c["root"].children_recursive:
        if o.type not in ("MESH", "FONT") or not o.data or o.hide_render:
            continue
        for i, m in enumerate(o.data.materials):
            if m is None or m.name.startswith("ghost"):
                continue
            b = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
            if b is None or b.inputs["Alpha"].is_linked:      # a printed decal: hide it while see-through
                _GHOST_UNDO.append((o, None, o.hide_render))
                o.hide_render = True
                break
            key = f"ghost{k:.2f}|{m.name}"
            g = bpy.data.materials.get(key)
            if g is None:
                g = m.copy()
                g.name = key
                g.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = k
                g.surface_render_method = "BLENDED"
            _GHOST_UNDO.append((o, i, m))
            o.data.materials[i] = g


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
        town.DOF = None
        time_of_day(tod)
        for i, c in enumerate(town.CHARACTERS):
            size(c, c["scale"])
            pose(c, loc=(300 + i * 12, -300, 0))     # parked off screen (the face stays: no mesh rebuild)
        for c in CARDS:
            c.location, c.scale = (300, -320, -50), (0.001,) * 3
        for fn in RESETS:
            fn(T)
        stillcheck.reset()
        i = max(i for i, s in enumerate(shots) if s[1] <= T + 1e-6)
        shots[i][2](T - shots[i][1], stops[i] - shots[i][1], T)
        if LIFE:                           # extra idle motion, camera wobble and scene sway (blockworld/life.py)
            life.apply(T, T - shots[i][1], stops[i] - shots[i][1])
        face = town.cam.rotation_euler.to_quaternion() @ Quaternion((1, 0, 0), math.radians(-90))
        for c in CARDS:                    # cards face the shot's final camera, even if put() came before shot()
            if c.scale[0] > 0.002:
                c.rotation_quaternion = face
        if LIFE:
            life.place_cards(T, CARDS)
            life.float_cards(T, CARDS)
        return i

    def words_in(a, b):
        return " ".join(w for w, t in zip(SCRIPT, WT) if a - 0.05 <= t < b - 0.05)

    report = []

    def still_check(n, T):
        for p in stillcheck.check(CARDS):
            line = f"{n} at {T:.2f}s: {p}"
            if not any(r.split(": ", 1)[1] == line.split(": ", 1)[1] and r.startswith(n + " ") for r in report):
                report.append(line)

    def write_report():
        (EP / "still_check.txt").write_text("\n".join(report) + ("\n" if report else "no problems found\n"))
        print(f"\nSTILL CHECK: {len(report)} problem(s)" + ("" if report else ", none found"))
        for r in report:
            print("STILL CHECK", r)

    if MODE == "check":
        town.scene.render.resolution_x, town.scene.render.resolution_y = 1080, 1920   # the still checks need 9:16
        warn = []
        print(f"\n{'#':>3} {'shot':<16}{'start':>7}{'len':>6}  words")
        for i, (n, s, _) in enumerate(shots):
            d = stops[i] - s
            for k in (0.0, 0.3, 0.6, 0.999):
                frame(s + d * k)
                still_check(n, s + d * k)
            print(f"{i + 1:>3} {n:<16}{s:>7.2f}{d:>6.2f}  {words_in(s, stops[i])}")
            if d > 2.5:
                warn.append(f"shot {n!r} is {d:.2f} s: over 2.5 s, split it or add a second angle")
            if d < 0.5:
                warn.append(f"shot {n!r} is only {d:.2f} s")
        print(f"\n{len(shots)} shots, {END:.2f} s, average {END / len(shots):.2f} s per shot, {math.ceil(END * FPS)} frames"
              + (" (word times ESTIMATED)" if ESTIMATED else ""))
        for w in warn:
            print("WARNING:", w)
        write_report()
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
                    still_check(n, s + (stops[i] - s) * k)
                    town.render_still(EP / "stills" / f"{i + 1:03d}_{n}_{tag}.jpg")
                    print("still", n, tag, flush=True)
            write_report()
    elif MODE in ("render", "resume"):
        if ESTIMATED:
            raise SystemExit("word times are estimated: make the narration (vo.py, words.py) before the final render")
        samples = int(os.environ.get("BT_SAMPLES", "32"))
        frame_root = Path(os.environ["BT_FRAME_DIR"]) if os.environ.get("BT_FRAME_DIR") else (EP / "frames")
        town.setup_render(1080, 1920, samples)
        if os.environ.get("BT_ENGINE", "").lower() == "workbench":
            # Workbench reads the material viewport colour, not the shader nodes.
            town.scene.render.engine = "BLENDER_WORKBENCH"
            sh = town.scene.display.shading
            sh.light = "STUDIO"
            sh.color_type = "MATERIAL"
            for name, val in (("show_shadows", True), ("use_scene_lights", False), ("use_scene_world", False)):
                if hasattr(sh, name):
                    setattr(sh, name, val)
            for m in bpy.data.materials:
                nt = m.node_tree
                if not m.use_nodes or nt is None or "Principled BSDF" not in nt.nodes:
                    continue
                sock = nt.nodes["Principled BSDF"].inputs.get("Base Color")
                if sock is not None:
                    m.diffuse_color = sock.default_value
            if town.scene.world is not None:
                town.scene.world.color = (0.55, 0.78, 0.95)
            print("BT_ENGINE workbench", flush=True)
        elif os.environ.get("BT_ENGINE", "").lower() == "cycles":
            # CPU only. This Vega is before RDNA1, so Cycles HIP cannot run.
            town.scene.render.engine = "CYCLES"
            try:
                prefs = bpy.context.preferences.addons["cycles"].preferences
                prefs.compute_device_type = "NONE"
            except (KeyError, AttributeError, TypeError):
                pass
            cyc = town.scene.cycles
            cyc.device = "CPU"
            cyc.samples = samples
            for name, val in (
                ("use_adaptive_sampling", False),
                ("use_denoising", True),
                ("max_bounces", 4),
                ("diffuse_bounces", 2),
                ("glossy_bounces", 2),
                ("transmission_bounces", 0),
                ("volume_bounces", 0),
            ):
                if hasattr(cyc, name):
                    setattr(cyc, name, val)
            print("BT_ENGINE cycles CPU samples", samples, flush=True)
        frame_root.mkdir(parents=True, exist_ok=True)
        f0 = int(ARGS[2]) if MODE == "render" and len(ARGS) > 2 else 0
        f1 = int(ARGS[3]) if MODE == "render" and len(ARGS) > 3 else math.ceil(END * FPS) - 1
        cap = float(os.environ.get("BT_MAX_FRAME_SECONDS", "0") or "0")
        for f in range(f0, f1 + 1):
            out = frame_root / f"f_{f:04d}.jpg"
            if MODE == "resume" and out.exists():
                continue
            t0 = time.perf_counter()
            frame(f / FPS)
            town.render_still(out)
            dt = time.perf_counter() - t0
            print(f"frame {f} of {f1} in {dt:.2f}s", flush=True)
            # The first frame pays for kernel startup. Later frames must each beat the cap.
            if cap and f > f0 and dt > cap:
                print(f"STOP frame {f} took {dt:.1f}s over {cap:.0f}s", flush=True)
                raise SystemExit(3)
    else:
        raise SystemExit(f"unknown mode {MODE!r}: use check, stills, frame, render or resume")
