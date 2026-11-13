"""Automatic still checks: catch the problems the user kept finding by eye, before any still is shown.

A shot names what must be seen with focus(...): a character (its face), a card/tag or prop object, or a point.
After the frame is posed, check() tests, from the camera:

  blocked   a ray from the lens to the face / prop hits something else first (a lamp post, a tree, another person, a tag)
  edge      the face or prop is outside the frame, or a tag is outside the TikTok safe area (x 5-85 %, between the
            top bar and the captions)
  lens      something sits less than 1 stud in front of the lens (blobs filling the frame)
  overlap   two shown tags cover each other
  captions  a face sits where the captions go (66 % from the top)

Runs in `check` and `stills` (run.py), prints STILL CHECK lines and writes EPISODE/still_check.txt.
"""
import math

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

import town

FOCUS = []
SAFE_X = (0.05, 0.85)       # TikTok's buttons are on the right
SAFE_Y_TAG = 0.38           # tags stay above the caption band (y measured from the bottom)
SAFE_TOP = 0.90             # ...and under TikTok's top bar (Following / For You), the top 10 %
import os
DEBUG = os.environ.get("BT_CHECK_DEBUG") == "1"
CAPTION_Y = (0.28, 0.40)    # finish.py puts captions at 66 % from the top: keep faces out of this band
NEAR = 1.0                  # studs: nothing closer than this to the lens


def focus(*things):
    """Inside a shot: name what the viewer must see. Characters (their face), cards / props (objects) or points."""
    FOCUS.extend(things)


def reset():
    FOCUS.clear()


def _mesh_parts(o):
    return [c for c in o.children_recursive if c.type in ("MESH", "FONT") and not c.hide_render]


def _ancestors(o):
    while o.parent is not None:
        o = o.parent
        yield o


def _owner(o, roots):
    while o is not None:
        if o in roots:
            return o
        o = o.parent
    return None


def _label(o):
    """A readable name for an object that blocks the view: its top-level parent's name."""
    while o.parent is not None:
        o = o.parent
    n = o.name
    for key in ("lamp", "tree", "house", "shop", "bus", "car", "sign", "card", "bars", "pricetag"):
        if key in n.lower():
            return key if key not in ("card", "bars", "pricetag") else "a tag"
    w = o.matrix_world.translation
    return f"{n.split('.')[0]} at ({w.x:.0f}, {w.y:.0f})"


def _name(o):
    """A tag by its words ("$40"), anything else by its object name."""
    words = [c.data.body for c in o.children_recursive if c.type == "FONT"]
    return f"'{' '.join(words[:1])}'" if words else o.name.split(".")[0]


def _corners(objs):
    pts = []
    for o in objs:
        mw = o.matrix_world
        pts += [mw @ Vector(c) for c in o.bound_box]
    return pts


def _cards_shown(cards):
    return [c for c in cards if c.scale[0] > 0.002]


def check(cards):
    """Return a list of problem strings for the current frame."""
    bpy.context.view_layer.update()
    scene, cam = bpy.context.scene, town.cam
    deps = bpy.context.evaluated_depsgraph_get()
    eye = cam.matrix_world.translation.copy()
    shown = _cards_shown(cards)
    card_set = set(shown)
    probs = []

    def ndc(p):
        return world_to_camera_view(scene, cam, p)

    def first_hit(p):
        """The first visible object between the lens and p (hidden helpers such as rain tiles are skipped)."""
        d = p - eye
        dist, direction, start = d.length, d.normalized(), eye.copy()
        for _ in range(8):
            left = dist - (start - eye).length - 0.05
            if left <= 0:
                return None
            ok, loc, _n, _i, obj, _m = scene.ray_cast(deps, start, direction, distance=left)
            if not ok:
                return None
            if not obj.hide_render and not any(a.hide_render for a in _ancestors(obj)):
                return obj
            start = loc + direction * 0.02
        return None

    # 1. nothing right in front of the lens
    mw = cam.matrix_world
    fwd, right, up = -Vector(mw.col[2][:3]).normalized(), Vector(mw.col[0][:3]).normalized(), Vector(mw.col[1][:3]).normalized()
    near = set()
    for i in range(5):
        for j in range(9):
            v = (fwd + right * ((i - 2) * 0.18) + up * ((j - 4) * 0.2)).normalized()
            ok, _l, _n, _i, obj, _m = scene.ray_cast(deps, eye, v, distance=NEAR)
            if ok and not obj.hide_render:
                near.add(_label(obj))
    if near:
        probs.append(f"lens: {', '.join(sorted(near))} less than {NEAR:g} stud from the camera")

    # 2. every focus thing in frame and not blocked
    for f in FOCUS:
        if isinstance(f, dict):                       # a character: test points across the face
            root, s = f["root"], f["root"].scale[2]
            yaw = root.rotation_euler[2]
            side = Vector((math.cos(yaw), math.sin(yaw), 0))
            c = Vector(root.location) + Vector((0, 0, 4.6 * s))
            pts = [c, c + side * 0.4 * s, c - side * 0.4 * s, c + Vector((0, 0, 0.45 * s)), c - Vector((0, 0, 0.35 * s)),
                   c + side * 0.2 * s + Vector((0, 0, 0.2 * s)), c - side * 0.2 * s - Vector((0, 0, 0.2 * s))]
            what, roots, is_tag = f["name"], {root}, False
        elif isinstance(f, bpy.types.Object):
            parts = _mesh_parts(f) or [f]
            cs = _corners(parts)
            mid = sum(cs, Vector()) / len(cs)
            pts = [mid] + cs
            what, roots, is_tag = _name(f), {f}, f in card_set
            if f.scale[0] <= 0.002:
                continue                                # not shown in this frame
        else:
            pts, what, roots, is_tag = [Vector(f)], "point", set(), False
        v = [ndc(p) for p in pts]
        if any(q.z <= 0 for q in v):
            probs.append(f"edge: {what} is behind the camera")
            continue
        x0, x1 = min(q.x for q in v), max(q.x for q in v)
        y0, y1 = min(q.y for q in v), max(q.y for q in v)
        if is_tag:
            if x0 < SAFE_X[0] - 0.01 or x1 > SAFE_X[1] + 0.01 or y0 < SAFE_Y_TAG - 0.01 or y1 > SAFE_TOP:
                probs.append(f"edge: tag {what} leaves the safe area (x {x0:.2f}-{x1:.2f}, y {y0:.2f}-{y1:.2f})")
            continue                                    # tags are drawn on top of everything: no blocking test
        if x0 < 0.02 or x1 > 0.98 or y0 < 0.02 or y1 > 0.98:
            probs.append(f"edge: {what} is cut by the frame (x {x0:.2f}-{x1:.2f}, y {y0:.2f}-{y1:.2f})")
        if isinstance(f, dict) and CAPTION_Y[0] <= v[0].y <= CAPTION_Y[1]:
            probs.append(f"captions: {what}'s face is under the caption band ({1 - v[0].y:.0%} from the top)")
        blockers = []
        test = pts if isinstance(f, dict) else pts[:1]
        for p in test:
            hit = first_hit(p)
            if hit is not None and isinstance(f, dict):  # the character's own raised arm in front of its face
                arms = {f.get("armL"), f.get("armR")} - {None}
                if _owner(hit, arms):
                    blockers.append("its own arm")
                    continue
            if DEBUG:
                print(f"  debug {what}: eye {tuple(round(x, 1) for x in eye)} -> {tuple(round(x, 1) for x in p)} hit {hit.name if hit else None}")
            if hit is None or _owner(hit, roots):
                continue
            blockers.append("a tag" if _owner(hit, card_set) else _label(hit))
        if blockers:                                    # any part of a face covered counts (a thin lamp post too)
            probs.append(f"blocked: {len(blockers)}/{len(test)} of {what} is behind {', '.join(sorted(set(blockers)))}")

    # 3. tags covering each other (a focus tag and any other shown tag)
    rects = []
    focus_cards = {f for f in FOCUS if isinstance(f, bpy.types.Object)}
    for c in shown:
        cs = _corners(_mesh_parts(c))
        if not cs:
            continue
        v = [ndc(p) for p in cs]
        if any(q.z <= 0 for q in v):
            continue
        rects.append((_name(c), min(q.x for q in v), max(q.x for q in v), min(q.y for q in v),
                      max(q.y for q in v), c in focus_cards))
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            if not (a[5] or b[5]):
                continue
            w = min(a[2], b[2]) - max(a[1], b[1])
            h = min(a[4], b[4]) - max(a[3], b[3])
            if w > 0 and h > 0:
                small = min((a[2] - a[1]) * (a[4] - a[3]), (b[2] - b[1]) * (b[4] - b[3]))
                if small > 0 and w * h / small > 0.15:
                    probs.append(f"overlap: tags {a[0]} and {b[0]} cover each other")
    return probs
