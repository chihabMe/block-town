"""The Roblox look: round heads, layered hair, printed clothes, shiny plastic, fog and moving rain.

Turn it on for an episode with   build_town(..., style="roblox")   and pick the mood with   run(SHOTS, tod="rain").
Nothing here runs unless an episode asks for it, so block-style episodes render exactly as before.

What style="roblox" does (apply()):
  * every matte material becomes plastic (a soft highlight), including props made later in the episode
  * the eight recurring characters are rebuilt in this look with the SAME colours, hair style and clothes details,
    so NIA, MAN, ... keep working in shot code, and pose(c, face=...) uses the round-head faces of the same names
  * moods for time_of_day / run(tod=...): "sun" (= "day"), "fog", "rain", plus the old "dusk" and "night"

Extra people:  rchar(name, skin, shirt, pants, hair_style, hair_col, top="jacket", legs="jeans", ...)
Landmarks:     giant_clock(x, y, ...), rule_sign(x, y, big, small, ...), puddles([(x, y, r), ...])
Textures:      python3 -I blockworld/rlook_tex.py  (faces and clothes prints, see that file to add one)
"""
import math, random
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

import town as T

LOOK = Path(__file__).resolve().parent / "rlook"
FACES = LOOK / "faces"
CLOTHES = LOOK / "clothes"
ON = False


# ---------------------------------------------------------------- materials
def plastic(hexcol, rough=0.42, key=None):
    """Shiny toy plastic: the base material of the Roblox look."""
    m = T.mat(hexcol, key=key or ("plastic", hexcol, rough))
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.4
    m["plastic"] = True
    return m


# world v2: overlay prints (rlook_tex.draw_overlays) and the recurring cast's chest prints in the dressed town
OVERLAYS = ("tee_star", "tee_stripe", "tee_heart", "tee_number", "tee_bolt", "shirt", "cardigan", "jacket_open",
            "dungarees", "hoodie2")
OUTFITS2 = {"Boy": dict(top="tee_star"), "Tall": dict(top="tee_number"), "Nia": dict(top="hoodie2"),
            "Dad": dict(top="shirt"), "Gran": dict(top="cardigan", stripes=None), "Kid": dict(top="dungarees"),
            "Man": dict(top="jacket_open")}
DETAIL = False          # set by apply(detail=True): sleeve rims and collars on everyone


def shade(hexcol, k):
    """A darker (k < 1) or lighter (k > 1) version of a colour."""
    h = hexcol.lstrip("#")
    return "#" + "".join(f"{max(0, min(255, round(int(h[i:i + 2], 16) * k))):02X}" for i in (0, 2, 4))


def _image(path):
    return bpy.data.images.load(str(path), check_existing=True)


def print_mat(colour, tex, key=None):
    """A clothes print. tex "jacket" / "jeans" are full prints; "shade" / "legs" / "hoodie" are grey prints
    multiplied onto colour, so any shirt or trousers colour gets folds, a hem and a belt."""
    key = key or ("print", colour, tex)
    if key in T.MATS:
        return T.MATS[key]
    m = plastic(colour, 0.5, key=key)
    nt = m.node_tree
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = _image(CLOTHES / f"{tex}.png")
    b = nt.nodes["Principled BSDF"]
    if tex in ("jacket", "jeans"):
        nt.links.new(img.outputs["Color"], b.inputs["Base Color"])
    elif tex in OVERLAYS:                    # a see-through print laid over the shirt colour (white stars, collars)
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
        mx.inputs["A"].default_value = T.lin(colour)
        nt.links.new(img.outputs["Alpha"], mx.inputs["Factor"])
        nt.links.new(img.outputs["Color"], mx.inputs["B"])
        nt.links.new(mx.outputs["Result"], b.inputs["Base Color"])
    else:
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
        mx.inputs["Factor"].default_value = 1.0
        mx.inputs["A"].default_value = T.lin(colour)
        nt.links.new(img.outputs["Color"], mx.inputs["B"])
        nt.links.new(mx.outputs["Result"], b.inputs["Base Color"])
    return m


def face_names():
    return sorted(p.stem for p in FACES.glob("*.png"))


def head_mat(skin, face):
    """Skin with a face picture projected onto the front of the round head (object space, no UVs needed)."""
    key = ("rhead", skin, face)
    if key in T.MATS:
        return T.MATS[key]
    png = FACES / f"{face}.png"
    if not png.exists():
        raise ValueError(f"no round-head face {face!r}. Faces: {', '.join(face_names())}. Add one in rlook_tex.py")
    m = plastic(skin, 0.4, key=key)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])

    def op(kind, a, value):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = kind
        nt.links.new(a, n.inputs[0]); n.inputs[1].default_value = value
        return n.outputs[0]
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(op("ADD", op("MULTIPLY", sep.outputs["X"], 0.8), 0.5), comb.inputs["X"])
    nt.links.new(op("ADD", op("MULTIPLY", sep.outputs["Z"], 0.8), 0.5), comb.inputs["Y"])
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = _image(png)
    img.extension = "CLIP"
    nt.links.new(comb.outputs[0], img.inputs["Vector"])
    fac = nt.nodes.new("ShaderNodeMath"); fac.operation = "MULTIPLY"
    nt.links.new(img.outputs["Alpha"], fac.inputs[0])
    nt.links.new(op("LESS_THAN", sep.outputs["Y"], 0.0), fac.inputs[1])      # front half only
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    mx.inputs["A"].default_value = T.lin(skin)
    nt.links.new(fac.outputs[0], mx.inputs["Factor"])
    nt.links.new(img.outputs["Color"], mx.inputs["B"])
    nt.links.new(mx.outputs["Result"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


# ---------------------------------------------------------------- rounded parts
def bevel(o, width, seg=3):
    for p in o.data.polygons:
        p.use_smooth = True
    m = o.modifiers.new("bevel", "BEVEL")
    m.width, m.segments, m.limit_method = width, seg, "ANGLE"
    m.harden_normals = True
    return o


def rbox(size, loc, material, parent=None, rot=(0, 0, 0), bv=0.06, name="part"):
    """A box with rounded edges (bv = bevel width in studs, 0 = sharp)."""
    me = T.CUBE.copy()
    me.transform(Matrix.Diagonal((*size, 1.0)))
    me.materials.append(material)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    o.parent = parent
    T.COL.objects.link(o)
    return bevel(o, bv) if bv else o


def blob(scale, loc, material, parent=None, rot=(0, 0, 0)):
    """A smooth squashed sphere (hair volume, bells, buns)."""
    o = T.prim("uv_sphere", segments=24, ring_count=12, radius=1)
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.materials.append(material)
    o.scale, o.location = scale, loc
    o.rotation_euler = [math.radians(a) for a in rot]
    o.parent = parent
    return o


def cone(r, depth, base, direction, material, parent, verts=5):
    """A hair spike from base pointing along direction."""
    o = T.prim("cone", vertices=verts, radius1=r, radius2=0, depth=depth)
    o.data.materials.append(material)
    d = Vector(direction).normalized()
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    o.location = Vector(base) + d * depth * 0.32
    o.parent = parent
    return o


def disc(radius, depth, loc, material, parent=None, rot=(90, 0, 0), bv=0.3, verts=64):
    o = T.prim("cylinder", vertices=verts, radius=radius, depth=depth)
    o.data.materials.append(material)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    o.parent = parent
    return bevel(o, bv, 4) if bv else o


def decal(material, size, loc, parent, name="print"):
    """A flat print laid on the front (-Y side) of a part."""
    w, h = size
    o = T.mesh_obj(name, [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)],
                   [(0, 1, 2, 3)], material, parent, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    o.location = loc
    return o


# ---------------------------------------------------------------- hair (same style names as the block look)
def _cap(head, m, back=True):
    blob((0.7, 0.7, 0.48), (0, 0.06, 0.36), m, head)
    if back:
        blob((0.68, 0.45, 0.56), (0, 0.24, 0.05), m, head)


def _spiky(head, m, rng):
    _cap(head, m)
    for i in range(18):
        th = rng.uniform(-150, 150) if i > 3 else rng.uniform(-60, 60)
        el = rng.uniform(15, 70)
        d = Vector((math.sin(math.radians(th)) * math.cos(math.radians(el)),
                    math.cos(math.radians(th)) * math.cos(math.radians(el)) * 0.9 + 0.25, math.sin(math.radians(el))))
        cone(rng.uniform(0.22, 0.32), rng.uniform(0.7, 1.05), Vector((0, 0.08, 0.3)) + d.normalized() * 0.45, d, m, head)
    for x in (-0.42, -0.2, 0.02, 0.24, 0.44):
        cone(rng.uniform(0.17, 0.22), rng.uniform(0.55, 0.75), (x, -0.5, 0.5),
             (x * 0.6 + rng.uniform(-0.15, 0.15), -0.55, -1.0), m, head)


def _swept(head, m, rng):
    _cap(head, m)
    blob((0.74, 0.5, 0.24), (0.06, -0.22, 0.58), m, head, rot=(0, -10, 0))
    for i, x in enumerate((-0.46, -0.24, -0.02, 0.2)):
        cone(0.2, 0.8, (x, -0.52, 0.52), (1.0, -0.4, -0.55 + 0.05 * i), m, head)


def _long(head, m, rng):
    _cap(head, m)
    rbox((1.36, 0.36, 2.0), (0, 0.5, -0.55), m, head, bv=0.16)
    for sx in (-1, 1):
        rbox((0.26, 0.9, 1.6), (sx * 0.66, 0.12, -0.36), m, head, bv=0.11)
    blob((0.7, 0.3, 0.22), (0, -0.46, 0.5), m, head)


def _bun(head, m, rng):
    _cap(head, m)
    blob((0.36, 0.36, 0.34), (0, 0.32, 0.74), m, head)


def _pig(head, m, rng):
    _cap(head, m)
    tie = plastic("#FF4FA0", 0.35)
    for sx in (-1, 1):
        blob((0.32, 0.34, 0.42), (sx * 0.98, 0.12, 0.16), m, head, rot=(0, sx * 20, 0))
        blob((0.12, 0.12, 0.12), (sx * 0.72, 0.12, 0.3), tie, head)


def _curl(head, m, rng):
    blob((0.2, 0.18, 0.2), (0.05, -0.08, 0.66), m, head, rot=(0, 25, 20))
    blob((0.14, 0.14, 0.14), (0.18, -0.12, 0.84), m, head)


def _hatcap(head, m_cap, rng, hair_m):
    blob((0.68, 0.68, 0.44), (0, 0.04, 0.38), m_cap, head)
    rbox((1.1, 0.72, 0.08), (0, -0.74, 0.32), m_cap, head, rot=(-8, 0, 0), bv=0.03)
    blob((0.64, 0.42, 0.42), (0, 0.24, 0.06), hair_m, head)


def _beanie(head, m_hat, rng):
    blob((0.72, 0.72, 0.6), (0, 0.02, 0.4), m_hat, head)
    rbox((1.42, 1.42, 0.3), (0, 0.02, 0.36), m_hat, head, bv=0.12)
    blob((0.2, 0.2, 0.2), (0, 0, 1.0), plastic("#FFFFFF", 0.6), head)


HAIR_STYLES = ("tuft", "side", "long", "bun", "pig", "curl", "cap", "beanie", "bald", "spiky")


def hair(head, style, col, rng):
    if style not in HAIR_STYLES:
        raise ValueError(f"no hair style {style!r}. Styles: {', '.join(HAIR_STYLES)}")
    if style == "bald":
        return
    if style in ("cap", "beanie"):          # col is the hat colour
        hat = plastic(col, 0.5)
        return _hatcap(head, hat, rng, plastic(T.HAIR["dark"], 0.55)) if style == "cap" else _beanie(head, hat, rng)
    m = plastic(T.HAIR.get(col, col), 0.55)
    {"tuft": _spiky, "spiky": _spiky, "side": _swept, "long": _long, "bun": _bun, "pig": _pig, "curl": _curl}[style](
        head, m, rng)


# ---------------------------------------------------------------- people
def rchar(name, skin, shirt, pants, hair_style, hair_col, sleeves="short", stripes=None, strings=False, tie=None,
          shoes="#F2F2F2", scale=1.0, seed=0, top="shade", legs="legs", face="smile", cuff=None, register=True):
    """A Roblox-look person. Same joints and keys as town.character(), so pose(), walk(), stand(), size() all work.

    top   "shade" (folds on the shirt colour), "hoodie" (pocket + strings, on the shirt colour), "jacket" (varsity print),
          or a world v2 overlay print: "tee_star", "tee_stripe", "tee_heart", "tee_number", "tee_bolt", "shirt",
          "cardigan", "jacket_open", "dungarees", "hoodie2"
    legs  "legs" (belt + folds on the pants colour) or "jeans" (blue jeans print)
    cuff  a hex colour for a band at the end of long sleeves (the jacket uses gold)
    """
    rng = random.Random(seed or name)
    ms = plastic(skin, 0.4)
    root = T.empty(name)
    body = T.empty(name + ".body", (0, 0, 2.0), root)
    torso = rbox((2, 1, 2), (0, 0, 1.0), plastic(shirt, 0.5), body, bv=0.08)
    decal(print_mat(shirt, top), (1.9, 1.9), (0, -0.506, 1.0), body)
    if DETAIL:                                                       # world v2: a collar ring under the head
        rbox((1.16, 0.96, 0.14), (0, 0, 2.02), plastic(shade(shirt, 0.8), 0.5), body, bv=0.05)
    if stripes:
        for i in range(4):
            rbox((2.04, 1.04, 0.2), (0, 0, 0.32 + i * 0.44), plastic(stripes, 0.5), body, bv=0.03)
    if strings and top not in ("hoodie", "hoodie2"):
        for sx in (-0.22, 0.22):
            rbox((0.08, 0.05, 0.62), (sx, -0.53, 1.6), plastic("#FFFFFF"), body, bv=0.02)
    if tie:
        rbox((0.24, 0.06, 1.1), (0, -0.53, 1.3), plastic(tie, 0.35), body, bv=0.03)
        rbox((0.7, 0.06, 0.3), (0, -0.53, 1.86), plastic("#FFFFFF"), body, bv=0.03)
    parts = {"name": name, "root": root, "body": body, "torso": torso, "skin": skin, "scale": scale,
             "look": "roblox", "face_fn": head_mat,
             "spec": dict(skin=skin, shirt=shirt, pants=pants, hair_style=hair_style, hair_col=hair_col, sleeves=sleeves,
                          stripes=stripes, strings=strings, tie=tie, shoes=shoes, scale=scale, seed=seed,
                          top=top, legs=legs, cuff=cuff)}
    sleeve_m = plastic("#EDEDF0" if top == "jacket" else shirt, 0.5)
    cut = 0.95 if sleeves == "short" else 1.62
    for side, sx in (("L", -1), ("R", 1)):
        sh = T.empty(f"{name}.arm{side}", (sx * 1.5, 0, 1.95), body)
        rbox((1, 1, cut), (0, 0, -cut / 2 + 0.05), sleeve_m, sh, bv=0.08)
        if cuff or top == "jacket":
            rbox((1.02, 1.02, 0.14), (0, 0, -cut + 0.12), plastic(cuff or "#D6A83A", 0.4), sh, bv=0.03)
        elif DETAIL:                                                 # world v2: a darker rim at the end of the sleeve
            rbox((1.05, 1.05, 0.16), (0, 0, -cut + 0.13), plastic(shade(shirt, 0.8), 0.5), sh, bv=0.04)
        rbox((0.96, 0.96, 2 - cut), (0, 0, -cut - (2 - cut) / 2 + 0.05), ms, sh, bv=0.1)
        hip = T.empty(f"{name}.leg{side}", (sx * 0.5, 0, 0), body)
        rbox((0.99, 0.99, 1.66), (0, 0, -0.83), plastic(pants, 0.5), hip, bv=0.06)
        decal(print_mat(pants, legs), (0.95, 1.6), (0, -0.5, -0.82), hip)
        rbox((1.02, 1.12, 0.36), (0, -0.05, -1.82), plastic(shoes, 0.35), hip, bv=0.1)
        rbox((1.04, 1.14, 0.1), (0, -0.05, -1.95), plastic("#EDEDED", 0.5), hip, bv=0.03)
        parts["arm" + side], parts["leg" + side] = sh, hip
    neck = T.empty(name + ".neck", (0, 0, 2.0), body)
    head = T.empty(name + ".head", (0, 0, 0.62), neck)
    h = T.prim("cylinder", vertices=40, radius=0.64, depth=1.2)
    h.name = name + ".face"
    h.data.materials.append(head_mat(skin, face))
    bevel(h, 0.26, 6)
    h.parent = head
    parts["face"] = h
    hair(head, hair_style, hair_col, rng)
    parts["neck"], parts["head"] = neck, head
    root.scale = (scale,) * 3
    if register:
        T.CHARACTERS.append(parts)
    return parts


def restyle(c, **change):
    """Rebuild a block character in the Roblox look, in place: the same dict (so NIA, MAN ... keep working).
    change overrides its spec, e.g. restyle(MAN, top="jacket", legs="jeans")."""
    spec = dict(c["spec"]); spec.update(change)
    new = rchar(c["name"], register=False, **spec)
    for o in [c["root"], *c["root"].children_recursive]:
        bpy.data.objects.remove(o, do_unlink=True)
    c.clear()
    c.update(new)
    return c


# ---------------------------------------------------------------- landmarks
def rule_sign(x, y, big, small="BY ORDER OF THE MAYOR", yaw=0, z=None, lift=2.4):
    """The official rule sign: red frame, white board, big red line, small dark line. Faces its local -Y.
    Keep its text above the caption band: lift raises the board (studs) on longer posts."""
    r = T.empty("rulesign", (x, y, T.ROAD + lift if z is None else z), yaw=yaw)
    for sx in (-1, 1):
        rbox((0.4, 0.4, 7.6 + lift), (sx * 4.2, 0, 3.8 - lift / 2), plastic("#3A3D46", 0.4), r, bv=0.05)
    rbox((10.6, 0.4, 5.0), (0, 0, 6.0), plastic("#D62B2B", 0.35), r, bv=0.1)
    rbox((10.0, 0.42, 4.4), (0, -0.02, 6.0), plastic("#FAFAF7", 0.45), r, bv=0.05)
    T.text(big, 1.3, (0, -0.25, 6.9), plastic("#D62B2B", 0.35, key="signred"), r, extrude=0.04, max_w=9.0)
    T.text(small, 0.62, (0, -0.25, 5.25), plastic("#22232B", 0.4, key="signink"), r, extrude=0.03, max_w=9.0)
    rbox((9.0, 0.44, 0.12), (0, -0.04, 5.95), plastic("#D62B2B", 0.35), r, bv=0)
    return r


CLOCKS = {}


def set_clock(clock, hours, minutes):
    """Move a giant_clock's hands (call it inside a shot: 2:59 -> 3:00). minutes may be fractional (a sweeping hand)."""
    mh, hh = CLOCKS[clock.name]
    mh.rotation_euler = (0, math.radians(minutes * 6), 0)
    hh.rotation_euler = (0, math.radians((hours % 12) * 30 + minutes * 0.5), 0)


def giant_clock(x, y, hours=7, minutes=58, yaw=0, frame="#D9A93A", rim="#C8322E"):
    """A three-storey alarm clock on a stone plinth: an example rule landmark (curfews, deadlines, timers).
    Its hands move with set_clock(clock, h, m).
    Faces its local -Y. Make a new landmark the same way: big, simple, one strong colour, readable from far away."""
    r = T.empty("clock", (x, y, 0), yaw=yaw)
    stone = plastic("#8D8F98", 0.7)
    rbox((16, 12, 5), (0, 0, 2.5), stone, r, bv=0.3)
    rbox((13, 10, 2), (0, 0, 6), stone, r, bv=0.3)
    brass, red = plastic(frame, 0.25), plastic(rim, 0.3)
    for sx in (-1, 1):
        rbox((1.6, 1.6, 6), (sx * 6, 0, 9), brass, r, rot=(0, sx * 18, 0), bv=0.2)
    cz = 21
    disc(12, 6.4, (0, 0, cz), brass, r, bv=0.8)
    disc(11.2, 7.0, (0, 0, cz), red, r, bv=0.9)
    disc(9.6, 0.4, (0, -3.55, cz), plastic("#F4EEDC", 0.5), r, bv=0.1)
    ink = plastic("#1C1C22", 0.4)
    for i in range(12):
        a = math.radians(i * 30)
        rbox((0.5 if i % 3 == 0 else 0.3, 0.2, 1.6 if i % 3 == 0 else 0.9),
             (math.sin(a) * 8.2, -3.8, cz + math.cos(a) * 8.2), ink, r, rot=(0, math.degrees(a), 0), bv=0.05)
    hands = []
    for length, width, yy in ((7.2, 0.7, -3.9), (5.0, 0.9, -3.95)):                 # minute hand, hour hand
        pivot = T.empty("clockhand", (0, yy, cz), r)                                  # turns about the clock's centre
        rbox((width, 0.2, length), (0, 0, length / 2 - 0.3), ink, pivot, bv=0.1)
        hands.append(pivot)
    CLOCKS[r.name] = hands
    set_clock(r, hours, minutes)
    disc(0.8, 0.5, (0, -4.0, cz), brass, r, bv=0.1)
    for sx in (-1, 1):
        blob((4.4, 4.4, 3.2), (sx * 7.5, 0, cz + 11.5), brass, r)
        rbox((1.2, 1.2, 3.0), (sx * 5.2, 0, cz + 9.6), brass, r, rot=(0, sx * 40, 0), bv=0.2)
    rbox((0.6, 0.6, 5.0), (0, 0, cz + 13.6), brass, r, bv=0.1)
    blob((1.3, 1.3, 1.3), (0, 0, cz + 16.4), brass, r)
    return r


def puddles(spots):
    """Dark mirror puddles on the road: spots = [(x, y, radius), ...]. Show them in rain shots."""
    m = plastic("#3B4352", 0.02, key="puddle")
    out = []
    for i, (px, py, pr) in enumerate(spots):
        o = T.prim("cylinder", vertices=24, radius=pr, depth=0.02, location=(px, py, T.ROAD + 0.11))
        o.data.materials.append(m)
        o.scale = (1, 0.6 + 0.4 * ((i * 37) % 10) / 10, 1)
        out.append(o)
    return out


# ---------------------------------------------------------------- moods: fog and moving rain
FOG = {"fog": ("#B4BFCC", 0.022), "rain": ("#B4BFCC", 0.022)}      # colour, density per stud
FOG_START = 7.0                                                    # studs of clear air in front of the camera
_RAIN = []
RAIN_TILE, RAIN_H, RAIN_SPEED = 24.0, 36.0, 42.0


def _fog_group():
    """One shared node group, so changing the mood changes the fog in every material at once."""
    g = bpy.data.node_groups.get("bt_fog")
    if g:
        return g
    g = bpy.data.node_groups.new("bt_fog", "ShaderNodeTree")
    g.interface.new_socket("Shader", in_out="INPUT", socket_type="NodeSocketShader")
    g.interface.new_socket("Shader", in_out="OUTPUT", socket_type="NodeSocketShader")
    n, l = g.nodes, g.links
    gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    cd = n.new("ShaderNodeCameraData")
    start = n.new("ShaderNodeValue"); start.name = "start"; start.outputs[0].default_value = FOG_START
    dens = n.new("ShaderNodeValue"); dens.name = "density"; dens.outputs[0].default_value = 0.0

    def op(kind, a, b):
        m = n.new("ShaderNodeMath"); m.operation = kind
        for i, v in enumerate((a, b)):
            if isinstance(v, float):
                m.inputs[i].default_value = v
            else:
                l.new(v, m.inputs[i])
        return m.outputs[0]
    d = op("MAXIMUM", op("SUBTRACT", cd.outputs["View Distance"], start.outputs[0]), 0.0)
    fac = op("SUBTRACT", 1.0, op("EXPONENT", op("MULTIPLY", d, op("MULTIPLY", dens.outputs[0], -1.0)), 0.0))
    em = n.new("ShaderNodeEmission"); em.name = "colour"
    mix = n.new("ShaderNodeMixShader")
    l.new(fac, mix.inputs[0]); l.new(gi.outputs[0], mix.inputs[1]); l.new(em.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], go.inputs[0])
    return g


def _fog_all():
    g = _fog_group()
    for m in bpy.data.materials:
        if m.get("fogged") or not m.use_nodes:
            continue
        nt = m.node_tree
        out = next((x for x in nt.nodes if x.type == "OUTPUT_MATERIAL"), None)
        if not out or not out.inputs["Surface"].links:
            continue
        src = out.inputs["Surface"].links[0].from_socket
        node = nt.nodes.new("ShaderNodeGroup"); node.node_tree = g
        nt.links.new(src, node.inputs[0])
        nt.links.new(node.outputs[0], out.inputs["Surface"])
        m["fogged"] = True


def _plastic_all():
    for m in bpy.data.materials:
        if m.get("plastic") or m.get("fogged_skip") or not m.use_nodes or "Principled BSDF" not in m.node_tree.nodes:
            continue
        b = m.node_tree.nodes["Principled BSDF"]
        if b.inputs["Emission Strength"].default_value == 0 and b.inputs["Roughness"].default_value >= 0.99:
            b.inputs["Roughness"].default_value = 0.5
            b.inputs["Specular IOR Level"].default_value = 0.35
        m["plastic"] = True


def _rain_mesh():
    rng = random.Random(11)
    verts, faces = [], []
    for _ in range(300):
        x, y, z = rng.uniform(0, RAIN_TILE), rng.uniform(0, RAIN_TILE), rng.uniform(0, RAIN_H)
        h, w = rng.uniform(0.7, 1.2), 0.02
        for dx, dy in ((w, 0), (0, w)):             # two crossed slivers: visible from any side
            i = len(verts)
            verts += [(x - dx, y - dy, z), (x + dx, y + dy, z), (x + dx + 0.06, y + dy + 0.04, z + h),
                      (x - dx + 0.06, y - dy + 0.04, z + h)]
            faces.append((i, i + 1, i + 2, i + 3))
    me = bpy.data.meshes.new("rain")
    me.from_pydata(verts, [], faces)
    m = bpy.data.materials.new("rain")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (1, 1, 1, 1)
    b.inputs["Emission Color"].default_value = (0.9, 0.95, 1, 1)
    b.inputs["Emission Strength"].default_value = 0.4
    b.inputs["Alpha"].default_value = 0.22
    m["plastic"] = True
    me.materials.append(m)
    return me


def _rain_tiles():
    if not _RAIN:
        me = _rain_mesh()
        for k in range(18):
            o = bpy.data.objects.new("rain", me)
            o.visible_shadow = False
            T.COL.objects.link(o)
            _RAIN.append(o)
    return _RAIN


def _place_rain(show):
    tiles = _rain_tiles()
    cam = T.cam.location
    cx, cy = round(cam.x / RAIN_TILE) * RAIN_TILE, round(cam.y / RAIN_TILE) * RAIN_TILE
    z0 = -((getattr(T, "NOW", 0.0) * RAIN_SPEED) % RAIN_H)
    k = 0
    for layer in (0, 1):
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                o = tiles[k]; k += 1
                o.location = (cx + (i - 0.5) * RAIN_TILE, cy + (j - 0.5) * RAIN_TILE, z0 + layer * RAIN_H)
                o.hide_render = not show


def _on_mood(mode):
    g = _fog_group()
    col, dens = FOG.get(mode, ("#FFFFFF", 0.0))
    g.nodes["density"].outputs[0].default_value = dens
    g.nodes["colour"].inputs["Color"].default_value = T.lin(col)
    wet = mode == "rain"
    for key, dry in ((("#26262C", 0.0), 0.5), (("#C3C6CE", 0.0), 0.5)):
        if key in T.MATS:
            T.MATS[key].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = \
                (0.14 if key[0] == "#26262C" else 0.3) if wet else dry
    if mode in FOG:
        for o in bpy.data.objects:
            if o.get("cloud"):
                o.hide_render = True


def _before_render():
    _plastic_all()
    _fog_all()
    _place_rain(T.TOD == "rain")


def apply(detail=False):
    """Called by build_town(style="roblox"). Safe to call once. detail=True (world v2) gives everyone sleeve rims and
    collars, and the recurring cast their chest prints (OUTFITS2)."""
    global ON, DETAIL
    if ON:
        return
    ON = True
    DETAIL = detail
    # moods: horizon, zenith, sky strength, sun strength, sun colour, sun elevation, windows, bulbs, lamp watts, clouds
    T.TIMES["sun"] = T.TIMES["day"]
    T.TIMES["fog"] = ("#B4BFCC", "#9AA6B4", 1.0, 3.0, "#D9E2EE", 34, 1.2, 1.5, 600, 0.0)
    T.TIMES["rain"] = T.TIMES["fog"]
    for c in list(T.ALL):
        if detail and c["name"] in OUTFITS2:
            restyle(c, **OUTFITS2[c["name"]])
        else:
            restyle(c)
    T.TOD_HOOKS.append(_on_mood)
    T.PRE_RENDER.append(_before_render)
