"""Ready-made Roblox-look pieces, first built for the Wi-Fi episode (examples/ep05-wifi). Use after build_town(...,
style="roblox"). Everything is code-built from rounded boxes and drawn pictures; nothing is downloaded.

Tags over heads (shown with put(), hidden again every frame like any card):
    bars(n, x_mark)                      signal bars, n of 4 lit; x_mark adds a red X (a "zero" counter)
    bar_token(i)                         one loose bar (0-3) that can fly out of a bars tag (see examples s34)
Phones (pictures from blockworld/pictures.py; see pictures.json in the example):
    phone_in_hand(c)                     a phone in the right hand showing a lock screen; raise the arm ~72 to look
    big_phone(x, y, z, screen="search")  a giant phone for insert shots, held by Max's hand; park it far away (y=-380)
Pictures on any prop:
    lit_picture(name), paper_picture(name), picture_quad(name, w, h, y, material, parent)
    tablet_in_hand(c, picture)           a tablet held in front (kids); phone_on_ground(x, y, picture) lies lit
Costumes:
    sash(c, "MAYOR"), top_hat(c), hivis(c), flat_cap(c), moustache(c), apron(c), paper_hat(c), nurse_cap(c)
Props:
    poster(x, y, z, face, skin, lines)   a wanted-style poster with a character's face
    paper_map()                          a folded town map (pictures/map.png), three panels; hold it at chest height
    lantern(c)                           a glowing lantern hanging from a hand (night scenes)
    phone_bin(x, y)                      a steel bin full of glowing phones; buzzer() + buzz() make it shake
    ice_cream_truck(x, y, yaw)           a van with a glowing cone on the roof and a lit serving hatch
    bus(x, y), door(x, y, z, yaw), hand_box(c, colour), beam(), pigeon(x, y), wifi_tower(x, y)
Shaking (a phone buzzing, a bin rattling): buzzer(obj) once after building it, then buzz(obj, T, k) inside a shot.

Things the life layer (blockworld/life.py, BT_LIFE=1) moves by itself, set by the custom properties below:
    "spin" loading-spinner dots turn, "pulse" Wi-Fi rings ripple, "bar" lit signal bars bounce, "xmark" the X throbs.
Give a new prop the same properties and it moves too.
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
        b = rbox((0.4, 0.1, h), (-0.81 + i * 0.54, 0, h / 2), glow(GREEN, 2.2) if i < n else plastic(OFF, 0.5), e, bv=0.05)
        b["bar"] = (i, 1 if i < n else 0, h)
    if x_mark:
        for a in (45, -45):
            x = rbox((1.5, 0.12, 0.3), (0.5, -0.06, 0.7), glow("#FF3B30", 2.5), e, rot=(0, a, 0), bv=0.05)
            x["xmark"] = a
    anim.CARDS.append(e)
    return e


def bar_token(i):
    """One loose green signal bar (bar i of 4, 0 = shortest) that can fly out of a bars tag. Show it with put().
    A bar's place inside a tag shown at scale k: tag_loc + right * (-0.81 + i * 0.54) * k (right = camera right)."""
    e = T.empty("bartoken")
    e.rotation_mode = "QUATERNION"
    h = 0.35 + 0.27 * i
    rbox((0.4, 0.1, h), (0, 0, h / 2), glow(GREEN, 2.2), e, bv=0.05)
    anim.CARDS.append(e)
    return e


# ---------------------------------------------------------------- pictures on props
def picture_file(name):
    """EPISODE/pictures/<name>.png (pictures.py EPISODE) if it exists, else the kit's blockworld/pictures/<name>.png."""
    ep = getattr(anim, "EP", None)
    if ep is not None and not (ep / "pictures" / f"{name}.png").exists() and (ep / "pictures.json").exists():
        import json, subprocess                  # draw the episode's pictures (system Python has Pillow, Blender may not)
        if name in json.loads((ep / "pictures.json").read_text()):
            subprocess.run(["python3", "-I", str(T.KIT / "pictures.py"), str(ep)], check=True)
    if ep is not None and (ep / "pictures" / f"{name}.png").exists():
        return ep / "pictures" / f"{name}.png"
    p = T.KIT / "pictures" / f"{name}.png"
    if not p.exists():
        raise FileNotFoundError(f"no picture {name!r}: add it to EPISODE/pictures.json and run pictures.py EPISODE")
    return p


def _picture(name, lit, strength, rough):
    key = ("picture", name, lit, strength)
    if key in T.MATS:
        return T.MATS[key]
    m = bpy.data.materials.new(f"{'screen' if lit else 'print'}_{name}")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(picture_file(name)), check_existing=True)
    if lit:                                  # a lit display: the picture IS the colour (exact on screen)
        b.inputs["Base Color"].default_value = (0, 0, 0, 1)
        nt.links.new(img.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = strength
        b.inputs["Specular IOR Level"].default_value = 0.5
    else:                                    # printed paper
        nt.links.new(img.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Specular IOR Level"].default_value = 0.2
    b.inputs["Roughness"].default_value = rough
    m["plastic"] = True
    T.MATS[key] = m
    return m


def lit_picture(name, strength=1.0):
    """A self-lit picture (phone screens, TVs, billboards at night)."""
    return _picture(name, True, strength, 0.15)


def paper_picture(name):
    """A printed picture on matte paper (maps, flyers, letters)."""
    return _picture(name, False, 0.0, 0.85)


def picture_quad(name, w, h, y, material, parent, z=0.0, flip=False):
    """A w x h picture plane in the parent's x-z plane at depth y, facing -Y. flip turns the picture upside down."""
    uvs = [(0, 1), (1, 1), (1, 0), (0, 0)] if flip else [(0, 0), (1, 0), (1, 1), (0, 1)]
    return T.mesh_obj(name, [(-w / 2, y, z - h / 2), (w / 2, y, z - h / 2), (w / 2, y, z + h / 2), (-w / 2, y, z + h / 2)],
                      [(0, 1, 2, 3)], material, parent, uvs=uvs)


# ---------------------------------------------------------------- phones
def phone_in_hand(c, side="R", picture="lock", screen=None):
    """A phone held in a hand (it moves with the arm), showing a picture (default: the kit's lock screen).
    screen="#7FD7FF" gives the old flat glowing screen instead. Look at it with arm=(72, -8), head=(0, -10)."""
    r = T.empty(c["name"] + ".phone", (0, -0.25, -2.0), c["arm" + side])
    r.rotation_euler = (math.radians(-90), 0, 0)
    rbox((0.62, 0.12, 1.1), (0, 0, 0), plastic("#1A1C22", 0.25), r, bv=0.05)
    if screen:
        rbox((0.52, 0.02, 0.96), (0, 0.07, 0), glow(screen, 1.6), r, bv=0)
    else:
        picture_quad(c["name"] + ".screen", 0.52, 0.96, 0.072, lit_picture(picture), r, flip=True)
    return r


def big_phone(x, y, z, lines=("Searching...",), bars_on=0, yaw=0, spinner=True, size=0.62, ink="#1E2230",
              screen=None, hand="#C98A5A"):
    """A giant phone (12 studs tall) for insert shots. Faces local -Y. Film it with
    shot((x + 0.3, y - 18, z + 0.3), (x, y, z), 42). Each insert needs its own phone at its own spot.
    screen = a picture name (pictures.py: wifi_search, calling, hotspot, chat, notice): a real phone screen with a
    status bar, slim bezel and side buttons. Without it: the old white screen with 3D text `lines`.
    spinner = 8 dots that turn (life layer) at 37.8 % from the bottom; wifi_search and calling leave room for it.
    hand = skin colour of the blocky hand holding it (thumb, fingers, palm), or None."""
    r = T.empty("bigphone", (x, y, z), yaw=yaw)
    body = plastic("#15161B", 0.25)
    rbox((6.0, 0.6, 12.0), (0, 0, 0), body, r, bv=0.8)
    if screen:
        picture_quad("phonescreen", 5.6, 11.5, -0.32, lit_picture(screen), r)
        rbox((0.16, 0.34, 1.5), (3.04, 0, 3.0), body, r, bv=0.06)                     # power button
        for bz in (3.6, 2.1):                                                          # volume buttons
            rbox((0.16, 0.34, 1.0), (-3.04, 0, bz), body, r, bv=0.06)
    else:
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
        dot = blob((0.16, 0.06, 0.16), (math.sin(a) * 0.7, -0.38, -1.4 + math.cos(a) * 0.7),
                   glow("#2B62D9", 0.4 + 0.25 * i), r)
        dot["spin"] = (i, 0.0, -0.38, -1.4, 0.7)                 # life.py turns it: (slot, centre x, y, z, radius)
    if hand:
        skin = plastic(hand, 0.5)
        rbox((1.05, 0.9, 3.0), (2.85, -0.62, -4.3), skin, r, rot=(0, -18, 0), bv=0.35)      # thumb over the edge
        for fz in (-1.6, -3.0, -4.4):                                                   # fingers round the back
            rbox((1.0, 1.0, 1.2), (-3.2, 0.1, fz), skin, r, bv=0.3)
        rbox((7.0, 1.9, 4.6), (0.3, 0.95, -7.9), skin, r, bv=0.5)                       # palm under the phone
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


def paper_map(picture="map", w=3.9, h=2.75):
    """A folded paper map (three panels bent toward the camera). Faces local -Y. Held by a character: put it at chest
    height in front of them (about 1.8 studs out, 2.4 up), tilt it back ~30 degrees, scale ~0.85, arms (62, 12), so
    the face stays in view and the map stays above the captions."""
    r = T.empty("papermap")
    w3 = w / 3
    paper, ink = plastic("#EFE3C2", 0.8), paper_picture(picture)
    for i, ang in enumerate((16, 0, -16)):
        side = (-1, 0, 1)[i]
        hinge = T.empty(f"mappanel{i}", (side * w3 / 2, 0, 0), r)
        hinge.rotation_euler = (0, 0, math.radians(ang))
        cx = side * w3 / 2
        rbox((w3, 0.03, h), (cx, 0.02, 0), paper, hinge, bv=0)
        u0, u1 = i / 3, (i + 1) / 3
        T.mesh_obj("mapface", [(cx - w3 / 2, -0.01, -h / 2), (cx + w3 / 2, -0.01, -h / 2), (cx + w3 / 2, -0.01, h / 2),
                               (cx - w3 / 2, -0.01, h / 2)], [(0, 1, 2, 3)], ink, hinge,
                   uvs=[(u0, 0), (u1, 0), (u1, 1), (u0, 1)])
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
    """A glowing beam 1 stud long along +X: place it, aim it with rotation_euler.z, stretch it with scale.x.
    Use it for energy that is already explained on screen. A beam alone does not explain an idea to viewers (ep05's
    "giving every bar away" read as "a blue line"): show the thing itself moving instead (bar_token)."""
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
        ring = T.empty(f"wifi_ring{k}", (0, 0, 0), sign)        # one empty per ring: the life layer pulses it
        ring["pulse"] = k
        n = 9 + 3 * k
        for i in range(n):
            a = math.radians(-46 + 92 * i / (n - 1))
            seg = 2 * rad * math.sin(math.radians(92 / (n - 1)) / 2) + 0.15
            rbox((seg, 0.5, 1.05), (math.sin(a) * rad, 0, math.cos(a) * rad), g, ring, rot=(0, math.degrees(a), 0),
                 bv=0.12)
    return r


# ---------------------------------------------------------------- night pieces (first built for ep07, the 3 AM text)
def tablet_in_hand(c, picture="lock", side="R"):
    """A tablet held up in front of the chest (sized for a kid). Look at it with arm=(80, -20), head=(0, -14)."""
    r = T.empty(c["name"] + ".tablet", (-0.35 if side == "R" else 0.35, -0.55, -2.0), c["arm" + side])
    r.rotation_euler = (math.radians(-90), 0, 0)
    rbox((1.25, 0.12, 1.7), (0, 0, 0), plastic("#1A1C22", 0.25), r, bv=0.07)
    picture_quad(c["name"] + ".tabscreen", 1.1, 1.52, 0.072, lit_picture(picture), r, flip=True)
    return r


def phone_on_ground(x, y, picture="lock", yaw=0, z=None):
    """A phone lying screen-up on the ground, still glowing (someone dropped it)."""
    r = T.empty("droppedphone", (x, y, (T.WALK if z is None else z) + 0.07), yaw=yaw)
    flat = T.empty("droppedphone.flat", (0, 0, 0), r)
    flat.rotation_euler = (math.radians(-90), 0, 0)
    rbox((0.62, 0.12, 1.1), (0, 0, 0), plastic("#1A1C22", 0.25), flat, bv=0.05)
    picture_quad("droppedscreen", 0.52, 0.96, -0.072, lit_picture(picture, 1.4), flat)
    return r


def flat_cap(c, colour="#4A4F5C"):
    """A flat cap with a short peak (old men, watchmen)."""
    m = plastic(colour, 0.6)
    disc(0.74, 0.34, (0, 0.04, 0.66), m, c["head"], rot=(0, 0, 0), bv=0.12, verts=32)
    rbox((1.15, 0.62, 0.12), (0, -0.62, 0.55), m, c["head"], rot=(-8, 0, 0), bv=0.05)


def moustache(c, colour="#D8DCE3"):
    rbox((0.78, 0.14, 0.18), (0, -0.66, -0.12), plastic(colour, 0.6), c["head"], bv=0.06)


def apron(c, colour="#FFFFFF", trim="#FF7FB0"):
    """A shop apron over the shirt (the ice-cream man)."""
    rbox((1.7, 0.08, 1.9), (0, -0.53, 0.95), plastic(colour, 0.6), c["body"], bv=0.04)
    rbox((1.72, 0.1, 0.16), (0, -0.55, 0.12), plastic(trim, 0.5), c["body"], bv=0.03)


def paper_hat(c, colour="#FFFFFF", band="#FF7FB0"):
    rbox((1.1, 0.7, 0.42), (0, 0.04, 0.78), plastic(colour, 0.6), c["head"], bv=0.06)
    rbox((1.12, 0.72, 0.1), (0, 0.04, 0.62), plastic(band, 0.5), c["head"], bv=0.03)


def nurse_cap(c):
    rbox((0.95, 0.55, 0.36), (0, -0.08, 0.76), plastic("#FFFFFF", 0.6), c["head"], bv=0.06)
    red = plastic("#E23B3B", 0.4)
    rbox((0.34, 0.06, 0.1), (0, -0.37, 0.78), red, c["head"], bv=0.02)
    rbox((0.1, 0.06, 0.3), (0, -0.37, 0.78), red, c["head"], bv=0.02)


def lantern(c, side="R", colour="#FFC56B"):
    """A lantern hanging from the hand, glowing. Keep the arm low (arm=(10, 0)) so it swings by the knee."""
    r = T.empty(c["name"] + ".lantern", (0, 0, -2.05), c["arm" + side])
    metal = plastic("#2A2C33", 0.35)
    rbox((0.12, 0.12, 0.5), (0, 0, -0.25), metal, r, bv=0.03)                        # handle
    rbox((0.8, 0.8, 0.14), (0, 0, -0.55), metal, r, bv=0.05)                         # lid
    rbox((0.62, 0.62, 0.86), (0, 0, -1.05), glow(colour, 5.0), r, bv=0.08)           # the light
    for sx in (-1, 1):
        for sy in (-1, 1):
            rbox((0.1, 0.1, 0.9), (sx * 0.34, sy * 0.34, -1.05), metal, r, bv=0.02)
    rbox((0.86, 0.86, 0.14), (0, 0, -1.55), metal, r, bv=0.05)                        # base
    return r


_BUZZ = {}


def buzzer(o):
    """Let o shake with buzz(o, T): remembers where it rests and puts it back there at the start of every frame."""
    _BUZZ[o.name] = (tuple(o.location), tuple(o.rotation_euler))

    def reset(T, o=o):
        loc, rot = _BUZZ[o.name]
        o.location, o.rotation_euler = loc, rot
    anim.before_each_frame(reset)
    return o


def buzz(o, T, k=1.0):
    """Shake o like a buzzing phone: short bursts (0.4 s on, 0.25 s off). k scales it."""
    if (T % 0.65) > 0.4:
        return
    loc, rot = _BUZZ[o.name]
    j = math.sin(T * 2 * math.pi * 21)
    o.location = (loc[0] + 0.05 * k * j, loc[1], loc[2] + 0.02 * k * abs(j))
    o.rotation_euler = (rot[0], rot[1] + math.radians(1.6 * k * j), rot[2])


def phone_bin(x, y, yaw=0, label="PHONES"):
    """A big steel bin, lid open, full of glowing phones. Faces local -Y. buzzer(it) then buzz(it, T) to rattle."""
    r = T.empty("phonebin", (x, y, 0), yaw=yaw)
    steel, dark = plastic("#7D8796", 0.3), plastic("#3B414C", 0.4)
    rbox((10.0, 6.0, 5.5), (0, 0, 3.05), steel, r, bv=0.3)
    rbox((10.4, 6.4, 0.5), (0, 0, 5.8), dark, r, bv=0.15)                              # rim
    lid = T.empty("phonebin.lid", (0, 3.2, 5.9), r)
    lid.rotation_euler = (math.radians(-62), 0, 0)
    rbox((10.2, 6.2, 0.4), (0, -3.1, 0), dark, lid, bv=0.12)
    for sx in (-3.6, 3.6):
        for sy in (-2.2, 2.2):
            rbox((0.9, 0.9, 0.6), (sx, sy, 0.3), dark, r, bv=0.1)                     # feet
    for i in range(14):                                                                # phones poking out of the top
        px, py = -4.0 + (i % 7) * 1.33, -1.6 + (i // 7) * 2.2
        ph = T.empty("binphone", (px, py, 5.9), r)
        ph.rotation_euler = (math.radians(-90 + (i * 23) % 50 - 25), math.radians((i * 37) % 30 - 15), 0)
        rbox((0.62, 0.12, 1.1), (0, 0, 0.3), plastic("#1A1C22", 0.25), ph, bv=0.05)
        rbox((0.52, 0.02, 0.96), (0, -0.07, 0.3), glow(("#8FD3FF", "#B9A6FF", "#9DF5C0")[i % 3], 2.4), ph, bv=0)
    T.text(label, 1.3, (0, -3.12, 3.2), plastic("#F2F2F2", 0.4, key="binink"), r, extrude=0.03, max_w=8.6)
    rbox((9.0, 0.1, 0.22), (0, -3.06, 4.4), glow("#FFD23A", 1.2), r, bv=0.02)       # yellow warning stripes
    rbox((9.0, 0.1, 0.22), (0, -3.06, 2.0), glow("#FFD23A", 1.2), r, bv=0.02)
    return r


def ice_cream_truck(x, y, yaw=0, lit=True):
    """An ice-cream van, nose toward -Y, serving hatch on its +X side, a big cone on the roof (glows at night)."""
    r = T.empty("icecream", (x, y, T.ROAD), yaw=yaw)
    white, pink, dark = plastic("#F6F3EE", 0.35), plastic("#FF8FBF", 0.35), plastic("#1A1C22", 0.4)
    k = 1.0 if lit else 0.0
    rbox((7.6, 17.0, 7.4), (0, 1.0, 4.6), white, r, bv=0.6)                            # box body
    rbox((7.2, 5.0, 4.6), (0, -9.4, 3.2), white, r, bv=0.6)                            # cab
    rbox((6.6, 0.3, 2.4), (0, -11.95, 4.2), glow("#BFE9FA", 0.5), r, bv=0.2)           # windscreen
    rbox((7.7, 17.1, 1.0), (0, 1.0, 2.2), pink, r, bv=0.15)                            # pink stripe
    rbox((0.3, 9.0, 3.4), (3.85, 1.5, 5.4), glow("#FFC98A", 0.7 * k + 0.1), r, bv=0.1)  # serving hatch, lit inside
    rbox((0.9, 9.4, 0.3), (4.2, 1.5, 7.3), pink, r, bv=0.08)                           # awning
    for sy in (-8.0, 6.5):
        for sx in (-1, 1):
            disc(1.3, 1.0, (sx * 3.7, sy, 1.3), dark, r, rot=(0, 90, 0), bv=0.2, verts=24)
    cone(1.9, 5.0, (0, 1.0, 12.6), (0, 0, -1), glow("#E3A55A", 0.6 * k + 0.1), r, verts=16)  # cone, point down
    blob((2.2, 2.2, 1.8), (0, 1.0, 13.6), glow("#FF9EC8", 1.8 * k + 0.2), r)           # strawberry scoop
    blob((1.6, 1.6, 1.4), (0, 1.0, 15.7), glow("#FFF4E0", 1.8 * k + 0.2), r)           # vanilla scoop
    for sx in (-1, 1):
        T.text("ICE CREAM", 1.1, (sx * 3.83, 1.0, 3.3), plastic("#E0457B", 0.4, key="icink"), r,
               rot=(90, 0, 90 * sx), extrude=0.03, max_w=8)
    return r


# ---------------------------------------------------------------- a bedroom set and a dog (ep07)
def bedroom(x, y, wall="#5C6B94", blanket="#E8A33C"):
    """A small bedroom built far from the street (park it at y = -460, 60 studs apart). Faces -Y: film it from
    (x, y - 13, 5) or closer. Returns a dict:
        seat      where a character sits up in bed: stand(c, room["seat"], 0, face, T, legL=90, legR=90)
        tuck(k)   pulls the blanket up: 0 = at the waist, 1 = up to the nose (call it inside the shot)
        stand     the nightstand top, for phone_on_ground(..., z=room["stand"][2])
        lamp      the bedside light (its glow strength: T.emission(room["lamp"], k))"""
    r = T.empty("bedroom", (x, y, 0))
    floor_m, wall_m = plastic("#8A6A4F", 0.6), plastic(wall, 0.7)
    rbox((22, 16, 0.4), (0, 0, -0.2), floor_m, r, bv=0.05)
    rbox((22, 0.6, 14), (0, 8, 7), wall_m, r, bv=0.05)                                      # back wall
    rbox((0.6, 16, 14), (-11, 0, 7), wall_m, r, bv=0.05)                                    # left wall
    rbox((5.2, 0.4, 4.6), (5.5, 7.65, 8.4), glow("#1B2A5C", 1.0), r, bv=0.05)               # night window
    for fx, fz, sx, sz in ((5.5, 10.85, 5.8, 0.3), (5.5, 5.95, 5.8, 0.3), (2.75, 8.4, 0.3, 5.2), (8.25, 8.4, 0.3, 5.2),
                           (5.5, 8.4, 0.2, 4.6)):
        rbox((sx, 0.5, sz), (fx, 7.5, fz), plastic("#EDEDF0", 0.5), r, bv=0.03)
    blob((0.3, 0.3, 0.3), (3.6, 7.3, 9.8), glow("#FFF6D8", 2.0), r)                        # the moon in the window
    wood = plastic("#6B4A33", 0.5)
    rbox((6.4, 10.5, 1.4), (-4.5, 2.6, 0.9), wood, r, bv=0.15)                              # bed frame
    rbox((6.8, 0.5, 4.2), (-4.5, 7.75, 2.1), wood, r, bv=0.15)                              # headboard
    rbox((6.0, 10.0, 0.9), (-4.5, 2.6, 2.0), plastic("#F2F2F4", 0.6), r, bv=0.25)           # mattress
    rbox((3.6, 1.6, 0.9), (-4.5, 6.6, 2.75), plastic("#FFFFFF", 0.6), r, bv=0.35)           # pillow
    bl = plastic(blanket, 0.7)
    rbox((6.4, 6.8, 0.6), (-4.5, 0.8, 2.6), bl, r, bv=0.25)                                 # blanket over the legs
    flap = T.empty("bedroom.flap", (-4.5, 3.6, 2.6), r)                                     # the part pulled up
    rbox((5.2, 0.7, 1.0), (0, 0, 0.5), bl, flap, bv=0.25)
    rbox((2.6, 2.4, 2.8), (1.4, 6.4, 1.4), wood, r, bv=0.15)                                # nightstand
    lamp_m = T.mat("#FFC56B", emit=1.0, key=("bedlamp", x, y))
    rbox((0.3, 0.3, 1.2), (2.2, 6.9, 3.4), plastic("#2A2C33", 0.4), r, bv=0.03)
    rbox((1.2, 1.2, 0.9), (2.2, 6.9, 4.3), lamp_m, r, bv=0.2)
    rbox((8, 5, 0.06), (-2, -3.5, 0.02), plastic("#B5463E", 0.8), r, bv=0)                  # rug
    T.emission(lamp_m, 0.0)

    def tuck(k):
        """0 = blanket at the waist, 1 = pulled up to the nose (in front of a sitting character's face)."""
        flap.scale = (1, 1, 1 + 1.3 * k)
    tuck(0)
    anim.before_each_frame(lambda Tm: tuck(0))
    return {"root": r, "seat": (x - 4.5, y + 4.6, 0.5), "tuck": tuck, "stand": (x + 1.4, y + 6.4, 2.8), "lamp": lamp_m}


def dog(x, y, z=0.0, yaw=0, coat="#C9894B", ears="#7A4A2C"):
    """A small blocky dog, facing local -Y. Its tail is r["tail"] (wag it with rotation_euler.y)."""
    r = T.empty("dog", (x, y, z), yaw=yaw)
    fur, dark = plastic(coat, 0.6), plastic(ears, 0.6)
    rbox((1.4, 2.6, 1.3), (0, 0.3, 1.5), fur, r, bv=0.3)                                  # body
    for sx in (-0.45, 0.45):
        for sy in (-0.65, 1.2):
            rbox((0.45, 0.45, 1.0), (sx, sy, 0.5), fur, r, bv=0.1)                         # legs
    head = T.empty("dog.head", (0, -1.0, 2.4), r)
    rbox((1.3, 1.2, 1.2), (0, 0, 0), fur, head, bv=0.3)
    rbox((0.7, 0.8, 0.55), (0, -0.75, -0.25), plastic("#E8C9A0", 0.6), head, bv=0.15)    # snout
    blob((0.16, 0.12, 0.14), (0, -1.16, -0.05), plastic("#111114", 0.2), head)            # nose
    for sx in (-1, 1):
        blob((0.1, 0.06, 0.12), (sx * 0.3, -0.62, 0.22), plastic("#111114", 0.2), head)   # eyes
        rbox((0.32, 0.25, 0.85), (sx * 0.62, 0.05, 0.2), dark, head, rot=(0, sx * 12, 0), bv=0.1)   # floppy ears
    tail = T.empty("dog.tail", (0, 1.55, 1.9), r)
    rbox((0.25, 0.25, 1.0), (0, 0, 0.45), fur, tail, rot=(-30, 0, 0), bv=0.08)
    r["_tail"] = tail.name
    return r


# ---------------------------------------------------------------- price tags and everyday props (ep08 "Price Tags")
def price_tag(label, plate="#FFF1C9", ink="#1B1D24", sz=0.62, is_card=True, name="pricetag", text_k=1.25):
    """A shop price tag: a pointed plate with a dark rim, a punched hole and a string loop, the price in big letters.
    Faces -Y like card(); show it with put(tag, over(c, 1.5), k). is_card=False for a fixed prop (the giant tag).
    A white ink ("#FFFFFF") glows a little so it reads on a red plate."""
    e = T.empty(name)
    e.rotation_mode = "QUATERNION"
    w = len(label) * sz * text_k * 0.6 + sz * 1.6
    h = sz * 1.75
    face = T.mat(plate, emit=0.55, key=("tagplate", plate))
    rim = T.mat(ink, key=("tagrim", ink))
    rbox((w, 0.1, h), (sz * 0.25, 0.06, 0), face, e, bv=0.12)
    rbox((h * 0.72, 0.1, h * 0.72), (-w / 2 + sz * 0.25, 0.06, 0), face, e, rot=(0, 45, 0), bv=0.08)
    rbox((w + 0.2, 0.06, h + 0.2), (sz * 0.25, 0.14, 0), rim, e, bv=0.12)
    rbox((h * 0.72 + 0.2, 0.06, h * 0.72 + 0.2), (-w / 2 + sz * 0.25, 0.14, 0), rim, e, rot=(0, 45, 0), bv=0.08)
    hx = -w / 2 + sz * 0.55
    rbox((sz * 0.28, 0.14, sz * 0.28), (hx, 0.0, 0), rim, e, bv=0.06)                       # the punched hole
    for dx, dz, a in ((-0.35, 0.62, 28), (0.02, 0.72, -22)):                                # the string loop
        rbox((0.07, 0.07, sz * 1.3), (hx + sz * dx, -0.02, sz * dz), plastic("#E8E2D0", 0.6), e, rot=(0, a, 0), bv=0.02)
    T.text(label, sz * text_k, (sz * 0.5, -0.03, 0),
           T.mat(ink, emit=1.2 if ink.upper() == "#FFFFFF" else 0.0, key=("tagink", ink)), e, extrude=0.0)
    if is_card:
        anim.CARDS.append(e)
    return e


def _in_hand(c, side, name):
    return T.empty(c["name"] + "." + name, (0, 0, -2.1), c["arm" + side])


def crown(c, colour="#FFD23A"):
    """A gold paper crown on the head (the brother who 'eats like a king')."""
    r = T.empty(c["name"] + ".crown", (0, 0, 0.72), c["head"])
    gold = plastic(colour, 0.25)
    for i in range(10):
        a = math.radians(i * 36)
        rbox((0.42, 0.1, 0.42), (0.7 * math.cos(a), 0.7 * math.sin(a), 0), gold, r, rot=(0, 0, i * 36 + 90), bv=0.02)
        if i % 2 == 0:
            cone(0.16, 0.6, (0.7 * math.cos(a), 0.7 * math.sin(a), 0.2), (0, 0, 1), gold, r, verts=4)
    for a in (0, 120, 240):
        blob((0.09, 0.09, 0.09), (0.73 * math.cos(math.radians(a - 90)), 0.73 * math.sin(math.radians(a - 90)), 0.0),
             glow("#FF3B6B", 1.5), r)
    return r


def cookie(c=None, side="R", loc=(0, 0, 0)):
    """A chocolate-chip cookie, in a hand (c) or standing on its own at loc."""
    r = _in_hand(c, side, "cookie") if c else T.empty("cookie", loc)
    disc(0.55, 0.16, (0, -0.15, 0), plastic("#C98A45", 0.7), r, bv=0.05, verts=24)
    for x, z in ((-0.2, 0.15), (0.18, 0.2), (0.05, -0.2), (-0.25, -0.18), (0.28, -0.05)):
        blob((0.07, 0.05, 0.07), (x, -0.24, z), plastic("#3B2414", 0.6), r)
    return r


def scanner(c, side="R"):
    """The mayor's handheld tag scanner: a grey gun with a red glowing window. scan_on(sc, k) lights the red line."""
    r = _in_hand(c, side, "scanner")
    rbox((0.42, 0.45, 0.9), (0, 0, 0.1), plastic("#2A2C33", 0.4), r, bv=0.08)                 # handle
    rbox((0.6, 1.6, 0.6), (0, -0.55, 0.65), plastic("#F2C230", 0.35), r, bv=0.12)              # body
    rbox((0.5, 0.06, 0.4), (0, -1.36, 0.65), glow("#FF2A2A", 3.0), r, bv=0.04)                 # window
    line = rbox((0.05, 6.0, 0.05), (0, -4.4, 0.65), glow("#FF2A2A", 4.0), r, bv=0.0)
    line.scale = (1, 0.001, 1)
    r["scanline"] = line.name
    return r


def scan_on(sc, k):
    """k 0..1: the red scan line grows out of the scanner window (0 = off)."""
    o = bpy.data.objects[sc["scanline"]]
    o.scale = (1, max(0.001, k), 1)
    o.location.y = -1.4 - 3.0 * max(0.001, k)


def lawn_mower(x, y, z=0.0, yaw=0):
    """A red push mower with a grass bag; its handle points to local +Y (push it toward -Y)."""
    r = T.empty("mower", (x, y, z), yaw=yaw)
    rbox((2.2, 2.6, 0.7), (0, 0, 0.75), plastic("#E23B3B", 0.35), r, bv=0.15)
    rbox((1.2, 1.2, 0.8), (0, -0.2, 1.4), plastic("#2A2C33", 0.4), r, bv=0.12)                 # engine
    for sx in (-1, 1):
        for sy in (-1, 1):
            disc(0.42, 0.25, (sx * 1.15, sy * 0.95, 0.42), plastic("#1E1F24", 0.6), r, rot=(0, 90, 0), bv=0.06, verts=20)
        rbox((0.14, 0.14, 3.0), (sx * 0.85, 2.1, 2.0), plastic("#C9CDD4", 0.3), r, rot=(-38, 0, 0), bv=0.03)
    rbox((1.84, 0.16, 0.16), (0, 3.0, 3.15), plastic("#1E1F24", 0.5), r, bv=0.05)               # grip
    rbox((1.5, 1.3, 1.1), (0, 1.9, 1.0), plastic("#3E8E3A", 0.7), r, bv=0.2)                    # grass bag
    return r


def bike(x, y, z=0.0, yaw=0, colour="#2B62D9"):
    """A kid's bike along local Y (front wheel toward -Y)."""
    r = T.empty("bike", (x, y, z), yaw=yaw)
    frame, tyre = plastic(colour, 0.3), plastic("#1E1F24", 0.6)
    for sy in (-1.25, 1.25):
        disc(1.0, 0.18, (0, sy, 1.0), tyre, r, rot=(0, 90, 0), bv=0.05, verts=32)
        disc(0.62, 0.2, (0, sy, 1.0), plastic("#D9DCE2", 0.3), r, rot=(0, 90, 0), bv=0.03, verts=24)
    rbox((0.16, 2.5, 0.16), (0, 0, 1.75), frame, r, rot=(-8, 0, 0), bv=0.04)
    rbox((0.16, 0.16, 1.3), (0, 0.5, 1.45), frame, r, rot=(-20, 0, 0), bv=0.04)
    rbox((0.16, 0.16, 1.3), (0, -1.0, 1.6), frame, r, rot=(25, 0, 0), bv=0.04)
    rbox((0.5, 0.9, 0.18), (0, 0.75, 2.2), plastic("#1E1F24", 0.5), r, bv=0.08)                # seat
    rbox((1.4, 0.16, 0.16), (0, -1.3, 2.35), plastic("#1E1F24", 0.5), r, bv=0.05)              # handlebar
    return r


def cat(x, y, z=0.0, yaw=0, colour="#F2994A", wet=False):
    """An orange cat sitting, facing local -Y. wet=True adds water drops."""
    r = T.empty("cat", (x, y, z), yaw=yaw)
    fur, light = plastic(colour, 0.6), plastic("#FFF1DE", 0.6)
    blob((0.55, 0.75, 0.6), (0, 0.15, 0.6), fur, r)
    blob((0.5, 0.45, 0.45), (0, -0.45, 1.25), fur, r)
    blob((0.26, 0.16, 0.16), (0, -0.84, 1.12), light, r)
    for sx in (-1, 1):
        cone(0.18, 0.45, (sx * 0.28, -0.45, 1.55), (sx * 0.4, 0, 1), fur, r, verts=4)
        blob((0.07, 0.04, 0.09), (sx * 0.17, -0.86, 1.32), plastic("#1E1F24", 0.3), r)
    rbox((0.16, 0.16, 1.2), (0, 0.85, 0.75), fur, r, rot=(35, 0, 0), bv=0.07)
    if wet:
        for i in range(5):
            blob((0.06, 0.06, 0.1), (0.5 * math.sin(i * 2.1), -0.2 + 0.2 * i, 0.3 + 0.25 * i), glow("#7FD3FF", 1.2), r)
    return r


def moving_boxes(x, y, z=0.0, yaw=0, label="MAX"):
    """Three stacked cardboard boxes with tape, the top one labelled."""
    r = T.empty("boxes", (x, y, z), yaw=yaw)
    card_m, tape = plastic("#C99B62", 0.8), plastic("#E9D7B0", 0.6)
    for (bx, by, bz, s) in ((-0.9, 0, 0.8, 1.6), (0.9, 0.1, 0.75, 1.5), (0.0, 0.0, 2.35, 1.4)):
        rbox((s, s, s), (bx, by, bz), card_m, r, bv=0.05)
        rbox((s + 0.02, 0.3, s + 0.02), (bx, by, bz), tape, r, bv=0.02)
    T.text(label, 0.45, (0.0, -0.73, 2.25), plastic("#1E1F24", 0.5), r, extrude=0.0)
    return r


def desk(x, y, z=0.0, yaw=0, colour="#C98A45"):
    """A school desk with a chair behind it (the pupil sits at local +Y, facing -Y)."""
    r = T.empty("desk", (x, y, z), yaw=yaw)
    wood, metal = plastic(colour, 0.6), plastic("#5A606B", 0.4)
    rbox((2.6, 1.8, 0.2), (0, -0.4, 2.3), wood, r, bv=0.05)
    for sx in (-1.1, 1.1):
        for sy in (-1.1, 0.3):
            rbox((0.14, 0.14, 2.2), (sx, sy, 1.1), metal, r, bv=0.02)
    rbox((1.6, 1.4, 0.18), (0, 1.3, 1.4), wood, r, bv=0.05)                                    # chair seat
    rbox((1.6, 0.16, 1.4), (0, 2.0, 2.1), wood, r, bv=0.05)                                    # chair back
    return r


def candy_jar(x, y, z, colour="#FF5A8A", parent=None):
    """A glass jar of round candies (the glass is a light tint, the candies glow a little)."""
    r = T.empty("jar", (x, y, z), parent)
    rbox((1.0, 1.0, 1.3), (0, 0, 0.65), plastic("#DDF3FF", 0.05), r, bv=0.25)
    rbox((0.8, 0.8, 0.2), (0, 0, 1.4), plastic("#E23B3B", 0.4), r, bv=0.05)
    for i in range(9):
        blob((0.18, 0.18, 0.18), (0.25 * math.cos(i * 2.4), -0.42 + 0.02 * i, 0.3 + 0.11 * i),
             glow(("#FF5A8A", "#FFD23A", "#3BE37E", "#2FD4FF")[i % 4], 0.8), r)
    return r


def coin():
    """A gold coin card (show with put(); several make money flying)."""
    e = T.empty("coin")
    e.rotation_mode = "QUATERNION"
    disc(0.5, 0.12, (0, 0, 0), plastic("#FFD23A", 0.25), e, bv=0.04, verts=24)
    T.text("$", 0.6, (0, -0.08, 0), plastic("#C89412", 0.3), e, extrude=0.0)
    anim.CARDS.append(e)
    return e
