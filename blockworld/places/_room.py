"""Shared pieces for indoor places: a closed room (floor, four two-tone walls, ceiling), windows that are bright by day
and dark blue at night, a door, ceiling light panels, and ceiling lamps that switch on at dusk and night (they join
town.LAMPS, like the street lamps).

Walls are named by side: "N" (+Y), "S" (-Y), "E" (+X), "W" (-X). An item on a wall is placed by its offset along the
wall (x for N/S, y for E/W) and its height z, all in the room's local studs.
"""
import math

import bpy

import town as T
from roblox import plastic, rbox
from world2 import multi

WALL_T = 0.6
LAMP_K = 0.5          # indoor lamps share the street lamps' strength (town.TIMES); their colour scales them down
WINDOW_DAY = {"day": 1.1, "dusk": 0.55, "night": 0.12, "fog": 0.7, "rain": 0.6, "sun": 1.1}


def on_wall(room, side, off, z, sw, sh, depth, inset=0.0):
    """Size and centre of a w x h item lying flat on the inside of a wall (depth = how far it sticks out)."""
    w, d = room["w"], room["d"]
    face = WALL_T / 2 + inset
    if side == "N":
        return (sw, depth, sh), (off, d / 2 - face - depth / 2, z)
    if side == "S":
        return (sw, depth, sh), (off, -d / 2 + face + depth / 2, z)
    if side == "E":
        return (depth, sw, sh), (w / 2 - face - depth / 2, off, z)
    if side == "W":
        return (depth, sw, sh), (-w / 2 + face + depth / 2, off, z)
    raise ValueError(side)


def room(name, x, y, w, d, h, floor="#C49A6C", low="#7FB3A6", high="#F3E9D2", ceiling="#F4F1EA", wainscot=4.2,
         planks=True):
    """The shell. Returns a dict the other helpers take: root, w, d, h, frames (parts for one frame mesh)."""
    r = T.empty(name, (x, y, 0))
    r["bt_root"] = True
    rm = {"root": r, "w": w, "d": d, "h": h, "name": name, "frames": [], "lamps": []}
    rbox((w + 1.2, d + 1.2, 0.4), (0, 0, -0.2), plastic(floor, 0.5), r, bv=0.04)
    if planks:                                                       # floorboards: thin darker seams along x
        multi(f"{name}.planks", [((w, 0.08, 0.02), (0, -d / 2 + 1.6 * (i + 1), 0.005)) for i in range(int(d / 1.6))],
              plastic(_darker(floor), 0.6), r)
    lo, hi = plastic(low, 0.6), plastic(high, 0.7)
    for side, (sx, sy), length in (("N", (0, d / 2), w), ("S", (0, -d / 2), w), ("E", (w / 2, 0), d), ("W", (-w / 2, 0), d)):
        size_lo = (length + WALL_T, WALL_T, wainscot) if side in "NS" else (WALL_T, length + WALL_T, wainscot)
        size_hi = (length + WALL_T, WALL_T, h - wainscot) if side in "NS" else (WALL_T, length + WALL_T, h - wainscot)
        rbox(size_lo, (sx, sy, wainscot / 2), lo, r, bv=0.03)
        rbox(size_hi, (sx, sy, wainscot + (h - wainscot) / 2), hi, r, bv=0.03)
        s, c = on_wall(rm, side, 0, wainscot, length - 0.2, 0.3, 0.25)          # the rail on top of the wainscot
        rm["frames"].append((s, c))
        s, c = on_wall(rm, side, 0, 0.3, length - 0.2, 0.6, 0.2)                # skirting board
        rm["frames"].append((s, c))
    ceil = rbox((w + 1.2, d + 1.2, 0.5), (0, 0, h + 0.25), plastic(ceiling, 0.8), r, bv=0.03)
    ceil.visible_shadow = False                                                  # the sun still lights the room
    return rm


def _darker(hexcol, k=0.8):
    h = hexcol.lstrip("#")
    return "#" + "".join(f"{int(int(h[i:i + 2], 16) * k):02X}" for i in (0, 2, 4))


def window(rm, side, off, z=7.0, sw=6.0, sh=6.0, sill="#FFFFFF"):
    """A window: glass that glows like the sky outside (bright by day, dark blue at night), a frame with a cross, a sill."""
    key = ("roomwin", rm["name"], round(rm["root"].location.x, 2), round(rm["root"].location.y, 2))
    m = T.MATS.get(key)
    if m is None:
        m = T.mat("#1B2340", emit=1.1, key=key)
        m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = T.lin("#D6EEFF")
        m["bt_window"] = True
    rm["win"] = m
    s, c = on_wall(rm, side, off, z, sw, sh, 0.08)
    o = rbox(s, c, m, rm["root"], bv=0)
    o.visible_shadow = False
    t = 0.35
    for (ww, hh, oo, zz) in ((sw + t * 2, t, off, z + sh / 2 + t / 2), (sw + t * 2, t, off, z - sh / 2 - t / 2),
                             (t, sh, off - sw / 2 - t / 2, z), (t, sh, off + sw / 2 + t / 2, z),
                             (0.2, sh, off, z), (sw, 0.2, off, z)):
        rm["frames"].append(on_wall(rm, side, oo, zz, ww, hh, 0.3))
    s, c = on_wall(rm, side, off, z - sh / 2 - 0.5, sw + 1.4, 0.3, 0.9)
    rbox(s, c, plastic(sill, 0.5), rm["root"], bv=0.05)
    return o


def door(rm, side, off, colour="#8A5A3C", sw=4.4, sh=8.4):
    """A closed door with a frame and a knob. Returns the floor spot just inside it (local x, y)."""
    s, c = on_wall(rm, side, off, sh / 2, sw, sh, 0.25)
    rbox(s, c, plastic(colour, 0.55), rm["root"], bv=0.06)
    for (ww, hh, oo, zz) in ((sw + 0.8, 0.4, off, sh + 0.2), (0.4, sh, off - sw / 2 - 0.2, sh / 2),
                             (0.4, sh, off + sw / 2 + 0.2, sh / 2)):
        rm["frames"].append(on_wall(rm, side, oo, zz, ww, hh, 0.35))
    for k in (0.3, 0.7):                                                         # two panels on the door
        s, c = on_wall(rm, side, off, sh * k, sw - 1.4, sh * 0.32, 0.32)
        rbox(s, c, plastic(_darker(colour, 0.88), 0.55), rm["root"], bv=0.05)
    s, c = on_wall(rm, side, off + sw / 2 - 0.6, 4.0, 0.35, 0.35, 0.6)
    rbox(s, c, plastic("#D8A93A", 0.25), rm["root"], bv=0.08)
    _, (cx, cy, _) = on_wall(rm, side, off, 0, 1, 1, 3.0)
    return cx, cy


def ceiling_lights(rm, spots, panel=(5.0, 2.0)):
    """Light panels in the ceiling and one lamp under each (on at dusk and night, like the street lamps)."""
    r, h = rm["root"], rm["h"]
    pm = T.mat("#FFF6DE", emit=1.4, key="roompanel")
    for (lx, ly) in spots:
        rbox((panel[0], panel[1], 0.2), (lx, ly, h - 0.05), pm, r, bv=0.05).visible_shadow = False
        li = bpy.data.lights.new(f"{rm['name']}.lamp", "SPOT")
        li.color = [v * LAMP_K for v in T.lin("#FFD9A8")[:3]]            # dimmer than a street lamp
        li.spot_size = math.radians(150)
        li.spot_blend = 0.8
        li.shadow_soft_size = 1.0
        li["bt_lamp"] = True
        lo = bpy.data.objects.new(f"{rm['name']}.lamp", li)
        lo.location = (lx, ly, h - 0.4)
        lo.parent = r
        T.COL.objects.link(lo)
        T.LAMPS.append(li)
        rm["lamps"].append(lo)


def finish(rm, colour="#FFFFFF"):
    """Every frame, window rail and skirting board of the room as one object."""
    multi(f"{rm['name']}.frames", rm["frames"], plastic(colour, 0.45), rm["root"])


def window_hook(p):
    """Call from a place's dress(): its windows follow the time of day (they glow like the sky outside)."""
    mats = {m.as_pointer(): m for o in p.objs if o.type == "MESH" for m in o.data.materials if m and m.get("bt_window")}

    def hook(mode):
        for m in mats.values():
            T.emission(m, WINDOW_DAY.get(mode, 0.8))
    T.TOD_HOOKS.append(hook)
    if T.TOD:
        hook(T.TOD)


def colour_boxes(name, by_colour, parent, rough=0.4):
    """Many small boxes in a few colours (shop products, books) as one object per colour."""
    for col, parts in by_colour.items():
        if parts:
            multi(f"{name}.{col.lstrip('#')}", parts, plastic(col, rough), parent)
