"""Ready-made shots for the Roblox-look episodes, from the patterns of ep05 and ep07. Use inside a shot function, after
posing the characters (so the camera can find them):

    front(c, dist, fov, side, rise, push, t)   a face shot from in front, pushing in (tag over the head: dist 9.5, fov 46)
    low(c, t, dist)                            a hero/threat shot from the ground looking up at a character
    high(c, t, dist)                           looking down at a character (small, alone, watched)
    over_shoulder(a, b, t)                     from behind a's shoulder onto b's face
    insert(phone, t, push)                     a big_phone insert, pushing in slowly
    street(t, y0, y1, z, fov)                  a wide move down the street (night streets, windows going dark)

Every template moves (push, drift or crane): a shot where nothing moves is a weak shot (SKILL.md quality bar).
"""
import math

from mathutils import Vector

from anim import closeup, eyes, smooth
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
