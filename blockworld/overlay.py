"""Flat 2D graphics over the picture, the way the viral videos label things (viral pack, Nov 2026).

House style "Roblox game UI" (the user's pick, 14 Nov 2026, after agy scored six style families): tags, meters, the
top bar and time cards are outlined text on a see-through dark slate plate, like Roblox's own HUD. label(color=...)
is the TEXT colour (white for names, blue / orange / red for meters). Pops are outlined game numbers (green = a gain,
pass color="#FF5A4A" for a loss). Comic sound words keep the bold yellow comic look.

Call these inside a shot function, every frame they should show (like put() for cards). They are drawn sharp on top
of the Three.js frame (blockworld/threejs/scene.html), so they cost no render time and never clip into the scene.
`from anim import *` brings them in.

    label("THE KNOCKER", BOY)                       a pill-shaped name tag over a head (or a world point)
    icon("crown", BOY)                              crown, heart, question, exclaim, coin, star, zzz over a head
    icon("counter", NIA, text="39")                 a friend-counter pill (a person icon and a number)
    pop("+1", NIA, t - 0.4)                          "+1" floats up and fades (t = seconds since it popped)
    comic("KNOCK!", (0.5, 0.35), t)                  a big comic sound word that pops in and shakes (screen x, y)
    timecard("DAY 2", t)                             a full-width time card ("1 WEEK LATER") that slides in and out
    hud("STORM IN 0:56", "ALIVE 300")                game HUD pills at the top (left, right)
    endcard("FLIP IT?", t)                           the end question with two buttons (YES / NO)

`at` is a character (the anchor is just above the head), a world point (x, y, z) or a screen point ("s", x, y) with
x, y from 0 to 1 (top-left is 0, 0). Graphics are pushed into TikTok's safe area (7 % from the left, 12 % from the
right where its buttons are, HUD below its top bar). Put comic words beside the action, not over a face.
"""
import math

__all__ = ["label", "icon", "pop", "comic", "timecard", "hud", "endcard"]

ITEMS = []                    # this frame's requests; the bake turns them into screen positions (flush)


def _at(at, gap):
    if isinstance(at, dict) and "root" in at:
        return {"char": at, "gap": gap}
    if isinstance(at, tuple) and at and at[0] == "s":
        return {"screen": (float(at[1]), float(at[2]))}
    return {"world": tuple(float(v) for v in at)}


def label(text, at, k=1.0, color="#FFD84A", ink="#15161B", size=0.034, gap=1.0):
    """A pill-shaped name tag, like the viral videos' "THE KNOCKER" / "40 LOCKS" tags. k scales it (0 hides it)."""
    if k > 0.001:
        ITEMS.append({"kind": "label", "text": str(text), "k": k, "color": color, "ink": ink, "size": size,
                      **_at(at, gap)})


def icon(kind, at, k=1.0, text=None, color=None, size=0.072, gap=1.2):
    """An icon over a head: crown, heart, question, exclaim, coin, star, zzz, or counter (with text, e.g. "39")."""
    if k > 0.001:
        ITEMS.append({"kind": "icon", "icon": kind, "text": text, "k": k, "color": color, "size": size,
                      **_at(at, gap)})


def pop(text, at, t, color="#7CFF6B", size=0.05, life=0.9, gap=1.0):
    """A "+1" that floats up from `at` and fades out over `life` seconds (t = seconds since it popped)."""
    if 0 <= t <= life:
        ITEMS.append({"kind": "pop", "text": str(text), "u": t / life, "color": color, "size": size, **_at(at, gap)})


def comic(text, xy, t, color="#FFE14A", size=0.11, angle=-8.0, life=None):
    """A comic sound word ("KNOCK!", "TAP", "BOOM") at screen point xy: pops in with an overshoot and shakes.
    life (seconds) fades it out at the end; None keeps it."""
    if t < 0 or (life is not None and t > life):
        return
    fade = 1.0 if life is None else min(1.0, (life - t) / 0.15)
    ITEMS.append({"kind": "comic", "text": str(text), "t": t, "color": color, "size": size, "angle": angle,
                  "alpha": fade, "screen": tuple(xy)})


def timecard(text, t, dur=1.2, sub=None, color="#FFFFFF", y=0.2):
    """A time card band ("DAY 2", "1 WEEK LATER") in the upper third (y = its height on screen, 0 top, 1 bottom,
    kept clear of faces): slides in, holds, slides out."""
    if 0 <= t <= dur:
        ITEMS.append({"kind": "timecard", "text": str(text), "sub": sub, "u": t / dur, "dur": dur, "color": color,
                      "y": y})


def hud(left=None, right=None, warn=False):
    """Game-style HUD pills along the top: left (e.g. "STORM IN 0:56", with a clock) and right (e.g. "ALIVE 300").
    warn=True turns the left pill red (the last seconds)."""
    ITEMS.append({"kind": "hud", "left": left, "right": right, "warn": bool(warn)})


def endcard(question, t, a="YES", b="NO", title_y=0.17, buttons_y=0.6):
    """The end question with two buttons ("FLIP IT?  YES / NO"): the title drops into the top, the buttons pop one
    after the other low in the frame (title_y / buttons_y: 0 top, 1 bottom), so the face between stays clear."""
    if t >= 0:
        ITEMS.append({"kind": "endcard", "text": str(question), "a": a, "b": b, "t": t, "ty": title_y,
                      "by": buttons_y})


def flush(scene, cam):
    """Called by the bake once per frame, after posing: turns this frame's requests into screen positions (x, y from
    0 to 1, top-left 0, 0; items behind the camera are dropped) and clears the list."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    out = []
    for it in ITEMS:
        it = dict(it)
        world = None
        if "char" in it:
            import anim
            world = Vector(anim.over(it.pop("char"), it.pop("gap")))
        elif "world" in it:
            world = Vector(it.pop("world"))
        if world is not None:
            v = world_to_camera_view(scene, cam, world)
            if v.z <= 0:
                continue
            it["screen"] = (round(v.x, 4), round(1.0 - v.y, 4))
        out.append({k: (round(v, 4) if isinstance(v, float) else v) for k, v in it.items()})
    ITEMS.clear()
    return out
