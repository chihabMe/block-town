"""Ready-made Roblox-look pieces, first built for the Wi-Fi episode (examples/ep05-wifi). Use after build_town(...,
style="roblox"). Everything is code-built from rounded boxes; nothing is downloaded.

Tags over heads (shown with put(), hidden again every frame like any card):
    bars(n, x_mark)                      signal bars, n of 4 lit; x_mark adds a red X (a "zero" counter)
Phones:
    phone_in_hand(c)                     a phone in the right hand; raise the arm forward ~72 to look at it
    big_phone(x, y, z, lines, ...)       a giant phone screen for insert shots; park it far away (y = -380)
Costumes:
    sash(c, "MAYOR"), top_hat(c), hivis(c)
Props:
    poster(x, y, z, face, skin, lines)   a wanted-style poster with a character's face
    bus(x, y), door(x, y, z, yaw), hand_box(c, colour), beam(), pigeon(x, y), wifi_tower(x, y)
"""
import math

import bpy

import anim
import town as T
from roblox import blob, cone, disc, plastic, rbox

GREEN, OFF, CYAN = "#3BE37E", "#3A3F4A", "#2FD4FF"


def glow(hexcol, k=3.0):
    """A glowing colour (signs, screens, light)."""
    return T.mat(hexcol, emit=k, key=("glow", hexcol, k))


# ---------------------------------------------------------------- tags
def bars(n, x_mark=False):
    """A floating signal-bars tag: n of 4 bars lit. Create once before the shots; show with put(tag, loc, k)."""
    e = T.empty("bars")
    e.rotation_mode = "QUATERNION"
    rbox((2.5, 0.08, 1.75), (0, 0.06, 0.55), plastic("#15171C", 0.5), e, bv=0.25)
    for i in range(4):
        h = 0.35 + 0.27 * i
        rbox((0.4, 0.1, h), (-0.81 + i * 0.54, 0, h / 2), glow(GREEN, 2.2) if i < n else plastic(OFF, 0.5), e, bv=0.05)
    if x_mark:
        for a in (45, -45):
            rbox((1.5, 0.12, 0.3), (0.5, -0.06, 0.7), glow("#FF3B30", 2.5), e, rot=(0, a, 0), bv=0.05)
    anim.CARDS.append(e)
    return e


# ---------------------------------------------------------------- phones
def phone_in_hand(c, side="R", screen="#7FD7FF"):
    """A phone held in a hand (it moves with the arm). Look at it with arm=(72, -8), head=(0, -10)."""
    r = T.empty(c["name"] + ".phone", (0, -0.25, -2.0), c["arm" + side])
    r.rotation_euler = (math.radians(-90), 0, 0)
    rbox((0.62, 0.12, 1.1), (0, 0, 0), plastic("#1A1C22", 0.25), r, bv=0.05)
    rbox((0.52, 0.02, 0.96), (0, 0.07, 0), glow(screen, 1.6), r, bv=0)
    return r


def big_phone(x, y, z, lines=("Searching...",), bars_on=0, yaw=0, spinner=True, size=0.62, ink="#1E2230"):
    """A giant phone screen (12 studs tall) for insert shots. Faces local -Y. Film it with
    shot((x + 0.3, y - 18, z + 0.3), (x, y, z), 42). Each insert needs its own phone at its own spot."""
    r = T.empty("bigphone", (x, y, z), yaw=yaw)
    rbox((6.0, 0.6, 12.0), (0, 0, 0), plastic("#15161B", 0.25), r, bv=0.8)
    rbox((5.3, 0.1, 10.8), (0, -0.3, 0), glow("#F2F6FF", 1.2), r, bv=0.3)
    for i in range(4):
        h = 0.18 + 0.12 * i
        rbox((0.18, 0.06, h), (1.5 + i * 0.26, -0.37, 4.6 + h / 2), glow(GREEN, 2) if i < bars_on else
             plastic("#AEB4C0", 0.5), r, bv=0)
    for i, ln in enumerate(lines):
        T.text(ln, size, (0, -0.4, 1.0 + (len(lines) - 1) * size * 0.8 - i * size * 1.6),
               plastic(ink, 0.4, key=("phoneink", ink)), r, extrude=0.02, max_w=4.6)
    for i in range(8 if spinner else 0):
        a = math.radians(i * 45)
        blob((0.16, 0.06, 0.16), (math.sin(a) * 0.7, -0.38, -1.4 + math.cos(a) * 0.7), glow("#2B62D9", 0.4 + 0.25 * i), r)
    return r


# ---------------------------------------------------------------- costumes
def sash(c, label="MAYOR", colour="#E8C33A"):
    rbox((0.4, 1.12, 2.8), (0, 0, 1.0), plastic(colour, 0.3), c["body"], rot=(0, 40, 0), bv=0.05)
    T.text(label, 0.3, (0.05, -0.58, 1.05), plastic("#3A2A10", 0.4, key="sashink"), c["body"], rot=(90, 40, 0),
           extrude=0.01)


def top_hat(c, band="#D62B2B"):
    blk = plastic("#17171C", 0.3)
    disc(0.62, 1.3, (0, 0.04, 1.15), blk, c["head"], rot=(0, 0, 0), bv=0.06, verts=32)
    disc(1.0, 0.12, (0, 0.04, 0.56), blk, c["head"], rot=(0, 0, 0), bv=0.04, verts=32)
    disc(0.64, 0.25, (0, 0.04, 0.72), plastic(band, 0.3), c["head"], rot=(0, 0, 0), bv=0.03, verts=32)


def hivis(c):
    """Two reflective bands (use with an orange shirt): workers, repairmen."""
    for z in (0.55, 1.25):
        rbox((2.06, 1.06, 0.2), (0, 0, z), glow("#E9F3FF", 0.6), c["body"], bv=0.03)


# ---------------------------------------------------------------- props
def poster(x, y, z, face="angry", skin="#C98A5A", lines=("MEANEST KID", "IN TOWN"), cap=None, yaw=0, parent=None):
    """A red-framed poster with a character's face (a face name from rlook/faces) and two lines. Faces local -Y.
    cap = a hex colour to draw that character's cap on the picture."""
    r = T.empty("poster", (x, y, z), parent, yaw=yaw)
    rbox((9.6, 0.3, 11.0), (0, 0, 0), plastic("#D62B2B", 0.4), r, bv=0.1)
    rbox((9.0, 0.32, 10.4), (0, -0.02, 0), plastic("#FAF6EA", 0.5), r, bv=0.05)
    m = bpy.data.materials.new("poster_face")
    m.use_nodes = True
    nt = m.node_tree
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(T.KIT / "rlook" / "faces" / f"{face}.png"), check_existing=True)
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    mx.inputs["A"].default_value = T.lin(skin)
    nt.links.new(img.outputs["Alpha"], mx.inputs["Factor"]); nt.links.new(img.outputs["Color"], mx.inputs["B"])
    nt.links.new(mx.outputs["Result"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    T.mesh_obj("poster_face", [(-2.9, -0.2, -2.9), (2.9, -0.2, -2.9), (2.9, -0.2, 2.9), (-2.9, -0.2, 2.9)],
               [(0, 1, 2, 3)], m, r, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)]).location = (0, 0, 1.3)
    if cap:
        rbox((6.4, 0.34, 0.9), (0, -0.05, 4.3), plastic(cap, 0.4), r, bv=0.05)
    for i, ln in enumerate(lines[:2]):
        T.text(ln, 1.05, (0, -0.25, -2.8 - 1.4 * i), plastic("#D62B2B", 0.35, key="signred"), r, extrude=0.04, max_w=8.4)
    return r


def bus(x, y, yaw=0):
    """A yellow school bus, nose toward -Y; the open door is on its +X side near the front (x + 4, y - 10.6).
    It is 26 studs long: keep it away from the landmark's sight lines."""
    r = T.empty("bus", (x, y, T.ROAD), yaw=yaw)
    yel, dark, glass = plastic("#F5B91E", 0.35), plastic("#1A1C22", 0.4), glow("#BFE9FA", 0.5)
    rbox((8.0, 26.0, 7.6), (0, 0, 4.6), yel, r, bv=0.6)
    rbox((8.1, 22.0, 2.4), (0, 1.6, 6.2), glass, r, bv=0.3)
    rbox((7.0, 0.3, 3.0), (0, -13.0, 5.9), glass, r, bv=0.2)
    rbox((8.2, 26.2, 0.5), (0, 0, 3.3), dark, r, bv=0.1)
    rbox((0.3, 2.6, 5.4), (4.05, -10.6, 3.6), dark, r, bv=0.1)
    for sy in (-8.5, 8.5):
        for sx in (-1, 1):
            disc(1.4, 1.0, (sx * 3.9, sy, 1.4), dark, r, rot=(0, 90, 0), bv=0.2, verts=24)
    T.text("SCHOOL BUS", 0.9, (0, -13.2, 7.6), plastic("#1A1C22", 0.4, key="busink"), r, extrude=0.03)
    return r


def door(x, y, z, yaw=0):
    """A door panel hinged on its left edge (put it on a shop's door). Open it by turning rotation_euler.z."""
    h = T.empty("door", (x, y, z), yaw=yaw)
    rbox((3.6, 0.3, 6.6), (1.8, 0, 3.3), plastic("#2A2C38", 0.35), h, bv=0.08)
    rbox((2.6, 0.32, 3.2), (1.8, 0, 4.4), glow("#BFE9FA", 0.4), h, bv=0.05)
    rbox((0.2, 0.5, 0.2), (3.2, -0.3, 3.2), plastic("#D9A93A", 0.25), h, bv=0.03)
    return h


def hand_box(c, colour="#E23B3B", size=(1.2, 0.9, 0.8), side="R"):
    """A box held out in a hand (a lunch box, a gift, a parcel). Hide it with .scale when not in use."""
    r = T.empty(c["name"] + ".box", (0, -0.75, -2.05), c["arm" + side])
    rbox(size, (0, 0, 0), plastic(colour, 0.35), r, bv=0.12)
    rbox((size[0] * 0.4, 0.12, 0.3), (0, 0, size[2] * 0.62), plastic("#1A1C22", 0.4), r, bv=0.04)
    return r


def beam(colour=CYAN):
    """A glowing beam 1 stud long along +X: place it, aim it with rotation_euler.z, stretch it with scale.x."""
    r = T.empty("beam")
    rbox((1.0, 0.35, 0.35), (0.5, 0, 0), glow(colour, 4.0), r, bv=0.1)
    return r


def pigeon(x, y, z=None, yaw=0):
    r = T.empty("pigeon", (x, y, T.WALK if z is None else z), yaw=yaw)
    grey, dark = plastic("#8E95A3", 0.5), plastic("#4C5260", 0.5)
    blob((0.42, 0.62, 0.42), (0, 0.05, 0.62), grey, r)
    blob((0.24, 0.26, 0.26), (0, -0.48, 1.08), dark, r)
    blob((0.2, 0.2, 0.12), (0, -0.4, 0.86), plastic("#5BB98C", 0.3), r)
    cone(0.07, 0.3, (0, -0.68, 1.06), (0, -1, -0.2), plastic("#E8A23A", 0.4), r, verts=8)
    for sx in (-1, 1):
        blob((0.05, 0.05, 0.05), (sx * 0.18, -0.6, 1.16), plastic("#0C0C0E", 0.2), r)
        rbox((0.06, 0.06, 0.32), (sx * 0.14, 0.05, 0.16), plastic("#D46A5A", 0.4), r, bv=0)
        blob((0.1, 0.5, 0.26), (sx * 0.4, 0.15, 0.66), dark, r, rot=(14, 0, 0))
    return r


def wifi_tower(x, y, h=46):
    """Example landmark: a steel lattice tower with a glowing Wi-Fi sign on top, facing -Y."""
    r = T.empty("tower", (x, y, T.ROAD))
    steel, dark = plastic("#C9CED8", 0.35), plastic("#5E6675", 0.4)
    rbox((14, 14, 1.4), (0, 0, 0.7), plastic("#8D8F98", 0.7), r, bv=0.25)
    base, top = 5.6, 1.6
    for sx in (-1, 1):
        for sy in (-1, 1):
            dx, dy = (top - base) * sx, (top - base) * sy
            ln = math.sqrt(h * h + dx * dx + dy * dy)
            leg = rbox((0.7, 0.7, ln), (sx * (base + top) / 2, sy * (base + top) / 2, h / 2), steel, r, bv=0.12)
            leg.rotation_euler = (math.atan2(-dy, h), math.atan2(dx, h), 0)
    for i in range(1, 8):
        z = i * h / 8
        w = 2 * (base + (top - base) * z / h)
        for sx in (-1, 1):
            rbox((w, 0.35, 0.35), (0, sx * w / 2, z), dark, r, bv=0.05)
            rbox((0.35, w, 0.35), (sx * w / 2, 0, z), dark, r, bv=0.05)
    rbox((5.0, 5.0, 0.8), (0, 0, h + 0.4), steel, r, bv=0.15)
    rbox((0.6, 0.6, 8), (0, 0, h + 4.8), steel, r, bv=0.1)
    blob((0.9, 0.9, 0.9), (0, 0, h + 9.2), glow("#FF3B30", 4.0), r)
    sign = T.empty("wifi_sign", (0, -0.8, h + 6), r)
    g = glow(CYAN, 3.5)
    blob((1.1, 0.5, 1.1), (0, 0, 0), g, sign)
    for k, rad in enumerate((3.4, 6.0, 8.6)):
        n = 9 + 3 * k
        for i in range(n):
            a = math.radians(-46 + 92 * i / (n - 1))
            seg = 2 * rad * math.sin(math.radians(92 / (n - 1)) / 2) + 0.15
            rbox((seg, 0.5, 1.05), (math.sin(a) * rad, 0, math.cos(a) * rad), g, sign, rot=(0, math.degrees(a), 0),
                 bv=0.12)
    return r
