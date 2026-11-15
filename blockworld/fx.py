"""Effects and moods (viral pack, Nov 2026): blocky particles drawn by Three.js and colour moods.

Effects are asked for every frame inside a shot (like overlays) and drawn by blockworld/threejs/scene.html as small
blocks, which fits the toy look and costs almost nothing to render. `from anim import *` brings them in.

    sparks(at, t)                      a burst of glowing sparks (t = seconds since the burst)
    confetti(at, t, width=10)          confetti falling over an area (keeps falling while you call it);
                                       colors=FEATHERS for black-and-white feathers
    money_rain(at, t, width=10)        green bills raining down
    poof(at, t, size=2.5)              a smoke puff (an appearance, a vanishing, a transformation)
    fire(at, T, size=2.0)              blocky flames, flickering and rising
    ring(at, T, radius=2.5)            a glowing ring on the ground (a magic circle, a pill stage, a target)
    beam(at, T, length=14, radius=3)   a floodlight / spotlight beam pointing down from `at`
    flashback(k)                       black-and-white with a warm tint (k 0 -> 1), for memories
    flash(k)                           a white flash over the whole frame (k 0 -> 1), between beats

Moods for time_of_day / run(tod=...): "sunset" (pink and purple sky), "neon" (purple night, saturated), "horror"
(dark red, hard contrast), "apocalypse" (burnt orange sky). Each comes with its own colour grade.
`at` is a world point (x, y, z).
"""
import town as T

__all__ = ["FEATHERS", "sparks", "confetti", "money_rain", "poof", "fire", "ring", "beam", "flashback", "flash"]

ITEMS = []
GRADE = {}

# horizon, zenith, sky strength, sun strength, sun colour, sun elevation, windows, bulbs, lamp watts, clouds
T.TIMES.setdefault("sunset", ("#FFB38A", "#7A5FB8", 1.35, 2.2, "#FFC59A", 14, 1.6, 2.0, 1500, 0.9))
T.TIMES.setdefault("neon", ("#5A2A8A", "#120A2E", 1.7, 1.0, "#C9A8FF", 42, 3.4, 9.0, 14000, 0.0))
T.TIMES.setdefault("horror", ("#6A1A1A", "#140508", 1.5, 0.9, "#FF9A8A", 30, 2.4, 6.0, 9000, 0.0))
T.TIMES.setdefault("apocalypse", ("#F28A3A", "#6A2A1A", 1.4, 1.6, "#FFB070", 18, 1.2, 1.5, 800, 0.0))
# the colour grade each mood gets on top (saturation, contrast, vignette, tint r g b)
MOOD_GRADE = {
    "sunset": {"sat": 1.15, "con": 1.06, "vig": 0.2, "tint": (1.06, 0.95, 1.02)},
    "neon": {"sat": 1.3, "con": 1.12, "vig": 0.3, "tint": (1.02, 0.86, 1.14)},
    "horror": {"sat": 0.85, "con": 1.22, "vig": 0.42, "tint": (1.22, 0.78, 0.78)},
    "apocalypse": {"sat": 1.05, "con": 1.14, "vig": 0.32, "tint": (1.18, 0.96, 0.74)},
}


def _p(at):
    return [round(float(v), 3) for v in at]


def sparks(at, t, n=50, color=(6.0, 3.4, 1.0), seed=1, life=1.3):
    if 0 <= t <= life:
        ITEMS.append({"k": "sparks", "at": _p(at), "t": round(t, 4), "n": n, "c": color, "seed": seed, "life": life})


def confetti(at, t, width=10.0, height=14.0, n=90, seed=2, colors=None):
    """colors: a list of (r, g, b) in 0..1 (linear) instead of the party colours, e.g. FEATHERS."""
    it = {"k": "confetti", "at": _p(at), "t": round(t, 4), "n": n, "w": width, "h": height, "seed": seed}
    if colors:
        it["cols"] = [list(c) for c in colors]
    ITEMS.append(it)


FEATHERS = [(0.02, 0.02, 0.03), (0.9, 0.9, 0.88), (0.04, 0.04, 0.05)]   # black and white penguin feathers


def money_rain(at, t, width=10.0, height=14.0, n=60, seed=3):
    ITEMS.append({"k": "money", "at": _p(at), "t": round(t, 4), "n": n, "w": width, "h": height, "seed": seed})


def poof(at, t, size=2.5, seed=4, life=1.1):
    if 0 <= t <= life:
        ITEMS.append({"k": "poof", "at": _p(at), "t": round(t, 4), "s": size, "seed": seed, "life": life})


def fire(at, T_, size=2.0, n=34, seed=5):
    ITEMS.append({"k": "fire", "at": _p(at), "t": round(T_, 4), "s": size, "n": n, "seed": seed})


def ring(at, T_, radius=2.5, color=(1.0, 3.0, 4.0)):
    ITEMS.append({"k": "ring", "at": _p(at), "t": round(T_, 4), "r": radius, "c": color})


def beam(at, T_, length=14.0, radius=3.0, color=(1.0, 0.95, 0.8), k=1.0):
    if k > 0.001:
        ITEMS.append({"k": "beam", "at": _p(at), "t": round(T_, 4), "l": length, "r": radius, "c": color, "a": k})


def flashback(k=1.0):
    """Black and white with a warm tint (a memory), k 0 -> 1."""
    GRADE["sepia"] = max(GRADE.get("sepia", 0.0), float(k))


def flash(k):
    """A white flash over the whole frame, k 0 -> 1."""
    GRADE["flash"] = max(GRADE.get("flash", 0.0), float(k))


def flush():
    """Called by the bake once per frame: this frame's effects and colour grade, then clears them."""
    g = dict(MOOD_GRADE.get(T.TOD or "", {}))
    g.update(GRADE)
    out = {"items": list(ITEMS), "grade": g} if (ITEMS or g) else None
    ITEMS.clear()
    GRADE.clear()
    return out
