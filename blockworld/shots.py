"""Ready-made shots for the Roblox-look episodes, from the patterns of ep05 and ep07. Use inside a shot function, after
posing the characters (so the camera can find them):

    front(c, dist, fov, side, rise, push, t)   a face shot from in front, pushing in (tag over the head: dist 9.5, fov 46)
    low(c, t, dist)                            a hero/threat shot from the ground looking up at a character
    high(c, t, dist)                           looking down at a character (small, alone, watched)
    over_shoulder(a, b, t)                     from behind a's shoulder onto b's face
    insert(phone, t, push)                     a big_phone insert, pushing in slowly
    street(t, y0, y1, z, fov)                  a wide move down the street (night streets, windows going dark)


The camera pack (world v2). Vary the framing: never two shots in a row with the same template.
    wide(c, t, d)                              an establishing shot: far, a little high, drifting sideways
    extreme(c, t, part="eyes")                 an extreme close-up: just the eyes (or part="mouth")
    pov(a, b, t)                               what a sees: from a's eyes onto b's face
    orbit(c, t, d, a0, a1)                     the camera circles the character (a reveal, "everyone turned")
    crash(c, t, d=0.35)                        a crash zoom: from far to the face in a third of a second
    dutch(c, t, roll=14)                       a tilted low frame (something is wrong)
    top_down(what, t)                          straight down from the sky (the narrator's view, a map of the scene)
    follow(c, t)                               behind and beside a walking character, looking where they go
    two_shot(a, b, t)                          two people side on, both faces in frame
    whip(t, d, pos, a, b)                      a fast pan from one thing to another

Every template moves (push, drift or crane): a shot where nothing moves is a weak shot (SKILL.md quality bar).
"""
import math

from mathutils import Vector

from anim import back, clamp, closeup, eyes, smooth
from town import shot


def front(c, dist=7.0, fov=34, side=0.9, rise=0.4, push=0.6, t=0.0, key_w=0):
    closeup(c, dist=max(2.5, dist - push * t), fov=fov, side=side, rise=rise, key_w=key_w)


def _dirs(c):
    yaw = c["root"].rotation_euler[2]
    return Vector((math.sin(yaw), -math.cos(yaw), 0)), Vector((math.cos(yaw), math.sin(yaw), 0))


def low(c, t=0.0, dist=7.5, fov=44, side=1.2, key_w=0, push=0.4):
    """From near the ground in front of c, looking up at the face."""
    front_v, right = _dirs(c)
    s = c["root"].scale[2]
    e = eyes(c)
    base = Vector(c["root"].location)
    pos = base + (front_v * (dist - push * t) + right * side) * s + Vector((0, 0, 0.9 * s))
    shot(pos, e + Vector((0, 0, 0.3 * s)), fov, key_w=key_w)


def high(c, t=0.0, dist=9.0, up=8.0, fov=44, side=1.5, key_w=0, drift=0.4):
    """From above and in front of c, looking down."""
    front_v, right = _dirs(c)
    s = c["root"].scale[2]
    e = eyes(c)
    pos = e + (front_v * dist + right * (side + drift * t)) * s + Vector((0, 0, up * s))
    shot(pos, e - Vector((0, 0, 1.0 * s)), fov, key_w=key_w)


def over_shoulder(a, b, t=0.0, fov=38, back=3.2, side=1.4, rise=0.6, push=0.3, key_w=0):
    """Behind a's shoulder (a in the foreground, blurred by distance), onto b's face."""
    ea, eb = eyes(a), eyes(b)
    d = (eb - ea)
    d.z = 0
    d.normalize()
    right = Vector((d.y, -d.x, 0))
    pos = ea - d * (back - push * t) + right * side + Vector((0, 0, rise))
    shot(pos, eb + Vector((0, 0, -0.2)), fov, key_w=key_w)


def insert(phone, t=0.0, push=1.2, fov=42):
    """A big_phone insert: the phone fills the frame and the camera pushes in."""
    x, y, z = phone.location
    shot((x + 0.3, y - 18 + push * t, z + 0.3), (x, y, z), fov)


def street(t, d, y0=-40.0, y1=-20.0, z=9.0, target_y=120.0, target_z=8.0, fov=50, x=0.0):
    """A wide move down the middle of the street over the shot (y0 -> y1)."""
    k = smooth(t / d) if d else 0.0
    shot((x, y0 + (y1 - y0) * k, z), (x * 0.3, target_y, target_z), fov)


# ---------------------------------------------------------------- the camera pack (world v2)
def _point(what):
    """A character (its eyes), an object (its origin) or a point."""
    if isinstance(what, dict):
        return eyes(what)
    if hasattr(what, "matrix_world"):
        return Vector(what.matrix_world.translation)
    return Vector(what)


def wide(c, t=0.0, d=1.0, dist=34.0, up=9.0, fov=50, side=6.0, drift=3.0, key_w=0):
    """An establishing shot: the character small in the street, the camera drifting sideways."""
    p = _point(c)
    front_v, right = _dirs(c) if isinstance(c, dict) else (Vector((0, -1, 0)), Vector((1, 0, 0)))
    k = (t / d) if d else 0.0
    pos = p + front_v * dist + right * (side + drift * (k - 0.5)) + Vector((0, 0, up))
    shot(pos, p + Vector((0, 0, 1.0)), fov, key_w=key_w)


def extreme(c, t=0.0, part="eyes", fov=20, dist=6.6, side=0.25, push=0.4, key_w=0):
    """Just the eyes (or the mouth): the moment a character realises something."""
    front_v, right = _dirs(c)
    s = c["root"].scale[2]
    e = eyes(c) + Vector((0, 0, (-0.02 if part == "eyes" else -0.42) * s))
    shot(e + (front_v * (dist - push * t) + right * side) * s, e, fov, key_w=key_w)


def pov(a, b, t=0.0, fov=52, push=0.5, key_w=0):
    """What a sees: from just in front of a's eyes onto b (a character, an object or a point)."""
    ea, eb = eyes(a), _point(b)
    d = (eb - ea).normalized()
    shot(ea + d * (1.2 + push * t), eb, fov, key_w=key_w)


def orbit(c, t, d, dist=8.0, fov=38, a0=-40.0, a1=40.0, rise=0.5, key_w=0):
    """Circle the character from angle a0 to a1 (degrees; 0 = straight in front, 90 = their armR side)."""
    front_v, right = _dirs(c)
    s = c["root"].scale[2]
    a = math.radians(a0 + (a1 - a0) * smooth(t / d if d else 0.0))
    e = eyes(c)
    shot(e + (front_v * math.cos(a) + right * math.sin(a)) * dist * s + Vector((0, 0, rise * s)), e, fov, key_w=key_w)


def crash(c, t, d=0.35, dist0=15.0, dist1=5.2, fov=36, side=0.5, rise=0.2, key_w=0):
    """A crash zoom: from dist0 to dist1 in d seconds with a small overshoot, then a slow creep."""
    k = back(clamp(t / d), 1.4) if d else 1.0
    closeup(c, dist=max(2.5, dist0 + (dist1 - dist0) * k - 0.3 * max(0.0, t - d)), fov=fov, side=side, rise=rise,
            key_w=key_w)


def dutch(c, t=0.0, roll=14.0, dist=7.5, fov=40, side=1.0, low=1.0, push=0.4, key_w=0):
    """A tilted frame from low down: unease, a threat, a world gone wrong."""
    front_v, right = _dirs(c)
    s = c["root"].scale[2]
    e = eyes(c)
    base = Vector(c["root"].location)
    pos = base + (front_v * (dist - push * t) + right * side) * s + Vector((0, 0, low * s))
    shot(pos, e, fov, key_w=key_w, roll=roll)


def top_down(what, t=0.0, height=28.0, fov=40, spin=8.0, offset=2.0, key_w=0):
    """Straight down from the sky, turning slowly."""
    p = _point(what)
    a = math.radians(spin * t)
    shot(p + Vector((math.sin(a) * offset, -math.cos(a) * offset, height)), p, fov, key_w=key_w)


def follow(c, t=0.0, back_=7.5, side=2.4, rise=1.0, fov=44, lead=4.0, key_w=0):
    """Behind and beside a walking character, looking past them at where they are going."""
    front_v, right = _dirs(c)
    s = c["root"].scale[2]
    e = eyes(c)
    shot(e - front_v * back_ * s + right * side * s + Vector((0, 0, rise * s)), e + front_v * lead * s, fov, key_w=key_w)


def two_shot(a, b, t=0.0, fov=40, dist=11.0, rise=0.2, push=0.5, key_w=0):
    """Two people side on: the camera stands at right angles to the line between them and backs off until both
    fit the narrow 9:16 frame (stand them 3-4 studs apart for big faces)."""
    ea, eb = eyes(a), eyes(b)
    mid = (ea + eb) / 2
    d = eb - ea
    d.z = 0
    d.normalize()
    n = Vector((d.y, -d.x, 0))
    if n.y > 0:                                # keep the camera on the road side when it can
        n = -n
    half = math.tan(math.radians(fov) / 2) * 9 / 16          # half the frame's width per stud of distance (9:16)
    dist = max(dist, ((eb - ea).length / 2 + 1.7) / half)    # far enough that both faces fit
    shot(mid + n * (dist - push * t) + Vector((0, 0, rise)), mid, fov, key_w=key_w)


def whip(t, d, pos, a, b, fov=44, when=0.5, key_w=0):
    """A fast pan from a to b (characters, objects or points) around when (0-1 of the shot), from a fixed spot."""
    pa, pb = _point(a), _point(b)
    k = smooth(clamp((t / d - when) / 0.18 + 0.5)) if d else 1.0
    shot(pos, pa + (pb - pa) * k, fov, key_w=key_w)
