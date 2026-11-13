"""The life layer: extra motion added on top of every shot, so no frame looks frozen.

anim.frame() calls apply() after the shot function has posed everything, when it is switched on with BT_LIFE=1. Everything here is ADDED to what the shot set, so a shot's
own poses, arm raises and camera moves still read; only held poses gain breathing, weight shifts and glances.
The amounts are scaled by BT_LIFE_AMOUNT (default 1.0; 0.5 calmer, 1.5 livelier).

Characters  breathing (squash/stretch), weight shift (lean/tilt), head turns and nods, arm sway,
            and a small squash-and-settle bounce on every cut.
Camera      a handheld wobble (tiny yaw/pitch/roll), a quick punch-in on every cut, a slow creep forward.
Scene       trees sway, clouds drift, tags and bubbles float.
"""
import math
import os
import zlib

from mathutils import Euler, Vector

import town

AMOUNT = float(os.environ.get("BT_LIFE_AMOUNT", "1.0") or "1.0")
_BASE = {}          # object name -> resting (location, rotation) for scene objects nothing else resets each frame


def _ph(name):
    return (zlib.crc32(name.encode()) % 1000) / 1000 * 2 * math.pi


def _s(T, hz, amp, ph=0.0):
    return amp * math.sin(2 * math.pi * hz * T + ph)


def _wobble(T, ph):
    """Smooth, non-repeating -1..1 noise from three detuned sines."""
    return (math.sin(1.13 * T + ph) + 0.6 * math.sin(2.71 * T + 1.7 * ph) + 0.35 * math.sin(4.37 * T + 2.3 * ph)) / 1.95


def _characters(T, t):
    k = AMOUNT
    rad = math.radians
    # squash on the cut: starts squashed, overshoots, settles in ~0.35 s
    cut = 0.06 * k * math.exp(-9.0 * t) * math.cos(22.0 * t)
    for c in town.CHARACTERS:
        root = c["root"]
        if root.location.x > 250:                 # parked off-stage
            continue
        ph = _ph(c.get("name", root.name))
        breath = _s(T, 0.45, 0.016 * k, ph)
        sz, sxy = 1 + breath - cut, 1 - breath / 2 + cut / 2
        root.scale = (root.scale[0] * sxy, root.scale[1] * sxy, root.scale[2] * sz)
        b = c["body"].rotation_euler
        b.x += rad(-_s(T, 0.42, 1.8 * k, ph + 1))            # lean
        b.y += rad(_s(T, 0.31, 2.6 * k, ph))                 # weight shift side to side
        n = c["neck"].rotation_euler
        n.z += rad(7.0 * k * _wobble(0.45 * T, ph))          # glance around
        n.x += rad(-_s(T, 0.37, 3.0 * k, ph + 2))            # nod
        for side, sgn in (("L", 1), ("R", -1)):
            a = c["arm" + side].rotation_euler
            a.x += rad(-_s(T, 0.55, 5.0 * k, ph + (0 if side == "L" else 2.1)))
            a.y += rad(sgn * _s(T, 0.4, 2.0 * k, ph + 0.7))


def _camera(T, t, d):
    k = AMOUNT
    cam, cd = town.cam, town.cam.data
    ph = 0.37
    shake = Euler((math.radians(0.35 * k * _wobble(T, ph)),
                   math.radians(0.45 * k * _wobble(T * 0.8, ph + 3)),
                   math.radians(0.30 * k * _wobble(T * 1.1, ph + 5))), "XYZ")
    cam.rotation_euler = (cam.rotation_euler.to_matrix() @ shake.to_matrix()).to_euler("XYZ")
    punch = 1 + 0.07 * k * math.exp(-10.0 * t)               # starts 7 % wide, snaps in
    creep = 1 - min(0.06, 0.022 * k * t)                       # then keeps drifting in
    cd.angle = cd.angle * punch * creep


def _scene(T):
    k = AMOUNT
    import bpy
    for o in bpy.context.scene.objects:
        if o.get("cloud"):
            loc, _ = _BASE.setdefault(o.name, (Vector(o.location), None))
            o.location = loc + Vector((2.2 * T, 0, 0))
        elif o.type == "EMPTY" and o.name.startswith("tree") and o.parent is None:
            _, rot = _BASE.setdefault(o.name, (None, Euler(o.rotation_euler)))
            ph = _ph(o.name)
            o.rotation_euler = (rot.x + math.radians(_s(T, 0.33, 1.1 * k, ph)),
                                rot.y + math.radians(_s(T, 0.27, 1.1 * k, ph + 1)), rot.z)


_TAGGED = {}


def _tagged(key):
    """Objects carrying a custom property set by a set piece: "spin", "pulse", "bar", "xmark"."""
    if not _TAGGED:
        import bpy
        for k in ("spin", "pulse", "bar", "xmark"):
            _TAGGED[k] = [o for o in bpy.data.objects if k in o.keys()]
    return _TAGGED[key]


def _props(T):
    """Screens and signs that should never sit still."""
    k = AMOUNT
    step = math.floor(T * 12)                                   # loading spinner: one dot per 1/12 s
    for o in _tagged("spin"):
        i, cx, cy, cz, r = o["spin"]
        a = math.radians((i + step) * 45)
        o.location = (cx + math.sin(a) * r, cy, cz + math.cos(a) * r)
    for o in _tagged("pulse"):                                  # Wi-Fi rings ripple outward, inner first
        w = max(0.0, math.sin(2 * math.pi * 1.1 * T - o["pulse"] * 0.9))
        s = 1 + 0.10 * k * w
        o.scale = (s, s, s)
    for o in _tagged("bar"):                                    # lit signal bars bounce like an equaliser
        i, lit, hgt = o["bar"]
        s = 1 + (0.22 * k * max(0.0, math.sin(2 * math.pi * 1.6 * T - i * 0.8)) if lit else 0.0)
        o.scale = (1, 1, s)
        o.location.z = hgt * s / 2
    for o in _tagged("xmark"):                                  # the red X throbs
        s = 1 + 0.14 * k * max(0.0, math.sin(2 * math.pi * 1.3 * T))
        o.scale = (s, 1, s)


def apply(T, t, d):
    """T = seconds into the video, t = seconds into the current shot, d = the shot's length."""
    _characters(T, t)
    _camera(T, t, d)
    _scene(T)
    _props(T)


# ---------------------------------------------------------------- tags: never covered, never off-screen
SAFE_X = (0.05, 0.85)      # TikTok's buttons sit on the right
SAFE_Y = (0.40, 0.90)      # captions sit at about 0.34 from the bottom; TikTok's top bar covers the top 10 %


def _corners(objs):
    out = []
    for o in objs:
        mw = o.matrix_world
        out += [mw @ Vector(c) for c in o.bound_box]
    return out


def _parts(o):
    return [c for c in o.children_recursive if c.type in ("MESH", "FONT") and not c.hide_render]


def _is_heart(card):
    return any(c.type == "FONT" and c.data.body.strip() == "♥" for c in card.children_recursive)


def place_cards(T, cards):
    """Lift tags that would sit in someone's hair and slide tags that would leave the frame back into the safe area.
    Call after the cards face the camera."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    shown = [c for c in cards if c.scale[0] > 0.002 and not _is_heart(c)]
    if not shown:
        return
    bpy.context.view_layer.update()
    scene, cam = bpy.context.scene, town.cam
    heads = []
    for ch in town.CHARACTERS:
        root = ch["root"]
        if root.location.x > 250:
            continue
        pts = _corners(_parts(root))
        if pts:
            heads.append((Vector((root.location.x, root.location.y)), max(p.z for p in pts), root.scale[2]))
    mw = cam.matrix_world
    right, up = Vector(mw.col[0][:3]).normalized(), Vector(mw.col[1][:3]).normalized()
    tan = math.tan(cam.data.angle / 2)
    aspect = scene.render.resolution_x / scene.render.resolution_y
    for card in shown:
        pts = _corners(_parts(card))
        if not pts:
            continue
        move = Vector((0, 0, 0))
        bottom, centre = min(p.z for p in pts), card.location.z
        for xy, top, s in heads:                     # a tag over a head goes above the hair, not into it
            if (Vector((card.location.x, card.location.y)) - xy).length < 1.6 * s and centre > top - 0.8 * s:
                need = top + 0.15 * s - bottom
                if need > move.z:
                    move.z = need
        pts = [p + move for p in pts]
        ndc = [world_to_camera_view(scene, cam, p) for p in pts]
        if min(v.z for v in ndc) <= 0:
            card.location += move
            continue
        x0, x1 = min(v.x for v in ndc), max(v.x for v in ndc)
        y0, y1 = min(v.y for v in ndc), max(v.y for v in ndc)

        def shift(a, b, lo, hi):
            if b - a > hi - lo:
                return (lo + hi) / 2 - (a + b) / 2
            return lo - a if a < lo else (hi - b if b > hi else 0.0)
        dx, dy = shift(x0, x1, *SAFE_X), shift(y0, y1, *SAFE_Y)
        depth = sum(v.z for v in ndc) / len(ndc)
        h = 2 * depth * tan
        card.location += move + right * dx * h * aspect + up * dy * h


def float_cards(T, cards):
    """Call after the cards face the camera: visible tags and bubbles bob gently."""
    k = AMOUNT
    for c in cards:
        if c.scale[0] > 0.002:
            ph = _ph(c.name)
            c.location.z += _s(T, 0.9, 0.07 * k, ph)
            s = 1 + _s(T, 1.6, 0.025 * k, ph)
            c.scale = (c.scale[0] * s, c.scale[1] * s, c.scale[2] * s)
