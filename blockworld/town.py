"""The block town and its people, built from plain boxes in code (no asset kits, no Roblox items).

Import this inside Blender (see anim.py). Importing it empties the scene and creates the materials, the recurring
cast, the sun, the sky and the camera. Call build_town(...) once to put up the street.

Units are studs. 1 stud = 1 foot in on-screen tags. A normal adult is 5.3 studs tall.
Map: the street runs along Y ("down the street" = +Y, toward the town hall at y = 190).
     road x = -12..12 (top z = 0.1) | sidewalks x = 12..21 both sides (top z = 0.5) | lawns 21..27 | house fronts at 27.
"""
import math, random, time
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

_T0 = time.perf_counter()
_TL = [_T0]


def tick(label):
    """Print how long the last build step took ("TJ time <label> <step s> (<total s>)"), for the render log."""
    now = time.perf_counter()
    print(f"TJ time {label} {now - _TL[0]:.1f}s ({now - _T0:.1f}s)", flush=True)
    _TL[0] = now


KIT = Path(__file__).resolve().parent
FONT = str(KIT / "fonts" / "DejaVuSans-Bold.ttf")
FACES = KIT / "faces"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
COL = scene.collection


# ---------------------------------------------------------------- materials
def lin(hexcol):
    """sRGB hex -> linear RGBA (without this everything renders washed out)."""
    h = hexcol.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


MATS = {}


def mat(hexcol, emit=0.0, key=None):
    """A flat matte colour. emit > 0 makes it glow (signs, windows, tags)."""
    key = key or (hexcol, emit)
    if key in MATS:
        return MATS[key]
    m = bpy.data.materials.new(str(key))
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(hexcol)
    b.inputs["Roughness"].default_value = 1.0
    b.inputs["Specular IOR Level"].default_value = 0.0
    if emit:
        b.inputs["Emission Color"].default_value = lin(hexcol)
        b.inputs["Emission Strength"].default_value = emit
    MATS[key] = m
    return m


def banded(hexcol, dark, freq=1.5, key=None):
    """Clapboard siding: thin darker lines every 1/freq studs of height (world space)."""
    key = key or ("band", hexcol)
    if key in MATS:
        return MATS[key]
    m = mat(hexcol, key=key)
    nt = m.node_tree
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = freq
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
    lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.13
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    mx.inputs["A"].default_value = lin(hexcol); mx.inputs["B"].default_value = lin(dark)
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mul.inputs[0])
    nt.links.new(mul.outputs[0], fr.inputs[0])
    nt.links.new(fr.outputs[0], lt.inputs[0])
    nt.links.new(lt.outputs[0], mx.inputs["Factor"])
    nt.links.new(mx.outputs["Result"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def brick(key="brick"):
    if key in MATS:
        return MATS[key]
    m = mat("#A8432F", key=key)
    nt = m.node_tree
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    bt = nt.nodes.new("ShaderNodeTexBrick")
    bt.inputs["Color1"].default_value = lin("#A8432F"); bt.inputs["Color2"].default_value = lin("#8E3526")
    bt.inputs["Mortar"].default_value = lin("#D9C7B4")
    bt.inputs["Scale"].default_value = 1.0; bt.inputs["Mortar Size"].default_value = 0.035
    bt.inputs["Brick Width"].default_value = 1.3; bt.inputs["Row Height"].default_value = 0.55
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nt.links.new(sep.outputs["X"], add.inputs[0]); nt.links.new(sep.outputs["Y"], add.inputs[1])
    nt.links.new(add.outputs[0], comb.inputs["X"]); nt.links.new(sep.outputs["Z"], comb.inputs["Y"])
    nt.links.new(comb.outputs[0], bt.inputs["Vector"])
    nt.links.new(bt.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def face_names():
    return sorted(p.stem for p in FACES.glob("*.png"))


def face_mat(skin, expr):
    key = ("face", skin, expr)
    if key in MATS:
        return MATS[key]
    png = FACES / f"{expr}.png"
    if not png.exists():
        raise ValueError(f"no face called {expr!r}. Faces: {', '.join(face_names())}. Add new ones in faces.py")
    m = mat(skin, key=key)
    nt = m.node_tree
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(png), check_existing=True)
    img.extension = "CLIP"
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    mx.inputs["A"].default_value = lin(skin)
    nt.links.new(img.outputs["Alpha"], mx.inputs["Factor"])
    nt.links.new(img.outputs["Color"], mx.inputs["B"])
    nt.links.new(mx.outputs["Result"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


# ---------------------------------------------------------------- geometry helpers
bpy.ops.mesh.primitive_cube_add(size=1)
CUBE = bpy.context.object.data
bpy.data.objects.remove(bpy.context.object)


def empty(name, loc=(0, 0, 0), parent=None, yaw=0):
    """An invisible parent, so a whole prop moves and turns as one. yaw in degrees."""
    e = bpy.data.objects.new(name, None)
    e.location = loc
    e.rotation_euler = (0, 0, math.radians(yaw))
    e.parent = parent
    COL.objects.link(e)
    return e


def box(size, loc, material, parent=None, rot=(0, 0, 0), name="part"):
    """One block: size (x, y, z), centre loc, rotation in degrees. Everything is made of these."""
    me = CUBE.copy()
    me.materials.append(material)
    o = bpy.data.objects.new(name, me)
    o.scale = size
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    o.parent = parent
    COL.objects.link(o)
    return o


_TEMPL = {}
_PRIM_NAME = {"uv_sphere": "Sphere", "cone": "Cone", "cylinder": "Cylinder", "ico_sphere": "Icosphere"}


def prim(kind, location=None, **kw):
    """A new object with a primitive mesh, like bpy.ops.mesh.primitive_<kind>_add(**kw) but fast: one unit-size template
    per shape is made with bpy.ops, and every object gets a scaled copy of its mesh. (bpy.ops gets slower with every
    object already in the scene: a 32-person crowd took 90 s next to the street.)"""
    kw = dict(kw)
    if kind in ("uv_sphere", "ico_sphere"):
        r = kw.pop("radius", 1.0)
        size = (r, r, r)
    elif kind == "cylinder":
        r, d = kw.pop("radius", 1.0), kw.pop("depth", 2.0)
        size, kw["depth"] = (r, r, d), 1.0
    elif kind == "cone":
        r1, r2, d = kw.pop("radius1", 1.0), kw.pop("radius2", 0.0), kw.pop("depth", 2.0)
        size, kw["depth"], kw["radius2"] = (r1, r1, d), 1.0, round(r2 / r1, 6) if r1 else 0.0
    else:
        raise ValueError(f"prim: unknown kind {kind!r}")
    key = (kind, tuple(sorted(kw.items())))
    me = _TEMPL.get(key)
    if me is None:
        getattr(bpy.ops.mesh, f"primitive_{kind}_add")(**kw)
        t = bpy.context.object
        me = t.data
        me.use_fake_user = True
        bpy.data.objects.remove(t)
        _TEMPL[key] = me
    m = me.copy()
    m.transform(Matrix.Diagonal((*size, 1.0)))
    o = bpy.data.objects.new(_PRIM_NAME[kind], m)
    if location is not None:
        o.location = location
    COL.objects.link(o)
    return o


def cylinder(radius, depth, loc, material, parent=None, rot=(0, 0, 0), vertices=14):
    """A cylinder along its own Z. Only for wheels and other things a box cannot be."""
    o = prim("cylinder", vertices=vertices, radius=radius, depth=depth)
    o.data.materials.append(material)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    o.parent = parent
    return o


def mesh_obj(name, verts, faces, material, parent=None, uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    if uvs:
        layer = me.uv_layers.new()
        for i, uv in enumerate(uvs):
            layer.data[i].uv = uv
    me.materials.append(material)
    o = bpy.data.objects.new(name, me)
    o.parent = parent
    COL.objects.link(o)
    return o


def text(body, size, loc, material, parent=None, rot=(90, 0, 0), extrude=0.03, name="text", max_w=None):
    """3D text, centred on loc. Default rotation stands it upright facing -Y. max_w shrinks it to fit a board."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    cu.extrude = extrude
    cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    cu.materials.append(material)
    o = bpy.data.objects.new(name, cu)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    o.parent = parent
    COL.objects.link(o)
    if max_w:
        bpy.context.view_layer.update()
        w = o.dimensions.x
        if w > max_w:
            cu.size = size * max_w / w
    return o


# ---------------------------------------------------------------- characters (6 blocks each)
HEAD = (1.34, 1.3, 1.26)  # w, depth, h
HAIR = {"black": "#1E1714", "brown": "#4A2A18", "dark": "#2E1C12", "ginger": "#C8621C", "blond": "#E2B755",
        "grey": "#B9BDC6", "red": "#8E2B1E"}
HAIR_STYLES = ("tuft", "side", "long", "bun", "pig", "curl", "cap", "beanie", "bald")
CHARACTERS = []
STYLE = "block"     # set by build_town(style=...)


def hair(head, style, col, rng):
    if style not in HAIR_STYLES:
        raise ValueError(f"no hair style {style!r}. Styles: {', '.join(HAIR_STYLES)}")
    m = mat(HAIR.get(col, col))
    w, d, h = HEAD
    top = h / 2
    if style in ("tuft", "long", "bun", "pig", "side"):
        box((w + 0.12, d + 0.12, 0.34), (0, 0.02, top + 0.05), m, head)             # cap
        box((w + 0.12, 0.3, h * 0.78), (0, d / 2 + 0.0, 0.2), m, head)               # back
        for sx in (-1, 1):
            box((0.2, d * 0.62, h * 0.5), (sx * (w / 2 + 0.0), 0.2, 0.36), m, head)   # sides
        box((w + 0.12, 0.2, 0.3), (0, -d / 2 - 0.02, top - 0.12), m, head)            # fringe
    if style == "tuft":
        for i in range(7):
            x = -w / 2 + 0.12 + (w - 0.24) * i / 6
            box((0.3, rng.uniform(0.5, 0.9), rng.uniform(0.28, 0.5)), (x, rng.uniform(-0.3, 0.2), top + 0.22), m, head,
                rot=(rng.uniform(-18, 18), rng.uniform(-22, 22), 0))
        box((0.5, 0.24, 0.42), (rng.choice((-0.3, 0.3)), -d / 2 - 0.04, top - 0.16), m, head, rot=(0, 14, 0))
    elif style == "side":
        box((w * 0.7, 0.26, 0.5), (-0.2, -d / 2 - 0.04, top - 0.2), m, head, rot=(0, -12, 0))
        box((w + 0.2, d + 0.2, 0.22), (0.06, 0, top + 0.26), m, head, rot=(0, 6, 0))
    elif style == "long":
        box((w + 0.2, 0.36, 1.9), (0, d / 2 + 0.04, -0.5), m, head)
        for sx in (-1, 1):
            box((0.24, d * 0.7, 1.5), (sx * (w / 2 + 0.03), 0.16, -0.25), m, head)
    elif style == "bun":
        box((0.62, 0.62, 0.56), (0, 0.25, top + 0.46), m, head, rot=(0, 0, 20))
    elif style == "pig":
        for sx in (-1, 1):
            box((0.56, 0.6, 0.6), (sx * (w / 2 + 0.3), 0.1, top - 0.02), m, head, rot=(0, sx * 14, 0))
            box((0.16, 0.2, 0.2), (sx * (w / 2 + 0.06), 0.1, top - 0.02), mat("#FF4FA0"), head)
    elif style == "curl":      # a baby: one curl on a bald head
        box((0.34, 0.3, 0.3), (0.05, -0.1, top + 0.12), m, head, rot=(0, 25, 20))
        box((0.26, 0.26, 0.24), (0.2, -0.16, top + 0.34), m, head, rot=(0, 50, 20))
    elif style == "cap":       # col is the cap colour
        c = mat(col)
        box((w + 0.14, d + 0.14, 0.42), (0, 0, top + 0.06), c, head)
        box((w * 0.9, 0.62, 0.1), (0, -d / 2 - 0.3, top - 0.1), c, head)
        box((w + 0.1, 0.24, h * 0.5), (0, d / 2 + 0.0, 0.2), mat(HAIR["dark"]), head)
    elif style == "beanie":    # col is the beanie colour
        c = mat(col)
        box((w + 0.16, d + 0.16, 0.6), (0, 0, top + 0.0), c, head)
        box((w * 0.7, d * 0.7, 0.3), (0, 0, top + 0.42), c, head)
        box((0.3, 0.3, 0.3), (0, 0, top + 0.7), mat("#FFFFFF"), head)


def character(name, skin, shirt, pants, hair_style, hair_col, sleeves="short", stripes=None, strings=False,
              tie=None, shoes="#F2F2F2", scale=1.0, seed=0, **look):
    """A block person. Returns a dict of its parts; pass it to pose(). The root (its location) is at the feet.

    sleeves "short" or "long" | stripes = a hex colour for 4 shirt stripes | strings = white hoodie strings |
    tie = a hex colour | scale = default size (1.0 = 5.3 studs tall).
    After build_town(style="roblox") this builds the Roblox-look person instead (roblox.rchar; extra keyword
    arguments such as top="jacket" or legs="jeans" are passed on).
    """
    if STYLE == "roblox":
        import roblox
        return roblox.rchar(name, skin, shirt, pants, hair_style, hair_col, sleeves=sleeves, stripes=stripes,
                            strings=strings, tie=tie, shoes=shoes, scale=scale, seed=seed, **look)
    if look:
        raise TypeError(f"{', '.join(look)} only work with build_town(style='roblox')")
    rng = random.Random(seed or name)
    ms, mt, mp = mat(skin), mat(shirt), mat(pants)
    root = empty(name)
    body = empty(name + ".body", (0, 0, 2.0), root)          # hip height
    torso = box((2, 1, 2), (0, 0, 1.0), mt, body)
    if stripes:
        for i in range(4):
            box((2.03, 1.03, 0.2), (0, 0, 0.32 + i * 0.44), mat(stripes), body)
    if strings:
        for sx in (-0.22, 0.22):
            box((0.07, 0.04, 0.62), (sx, -0.52, 1.6), mat("#FFFFFF"), body)
    if tie:
        box((0.22, 0.04, 1.1), (0, -0.52, 1.3), mat(tie), body)
        box((0.7, 0.04, 0.3), (0, -0.52, 1.86), mat("#FFFFFF"), body)
    parts = {"name": name, "root": root, "body": body, "torso": torso, "skin": skin, "scale": scale,
             "spec": dict(skin=skin, shirt=shirt, pants=pants, hair_style=hair_style, hair_col=hair_col, sleeves=sleeves,
                          stripes=stripes, strings=strings, tie=tie, shoes=shoes, scale=scale, seed=seed)}
    cut = 0.95 if sleeves == "short" else 1.62
    for side, sx in (("L", -1), ("R", 1)):
        sh = empty(f"{name}.arm{side}", (sx * 1.5, 0, 1.95), body)
        box((1, 1, cut), (0, 0, -cut / 2 + 0.05), mt, sh)
        box((0.98, 0.98, 2 - cut), (0, 0, -cut - (2 - cut) / 2 + 0.05), ms, sh)
        hip = empty(f"{name}.leg{side}", (sx * 0.5, 0, 0), body)
        box((0.99, 0.99, 1.64), (0, 0, -0.82), mp, hip)
        box((1.02, 1.08, 0.38), (0, -0.03, -1.81), mat(shoes), hip)
        parts["arm" + side], parts["leg" + side] = sh, hip
    neck = empty(name + ".neck", (0, 0, 2.0), body)
    head = empty(name + ".head", (0, 0, HEAD[2] / 2), neck)
    box(HEAD, (0, 0, 0), ms, head)
    w, d, h = HEAD
    parts["face"] = mesh_obj(name + ".face", [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)],
                             [(0, 1, 2, 3)], face_mat(skin, "smile"), head, uvs=[(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)])
    parts["face"].location = (0, -d / 2 - 0.006, -0.06)
    hair(head, hair_style, hair_col, rng)
    parts["neck"], parts["head"] = neck, head
    root.scale = (scale,) * 3
    CHARACTERS.append(parts)
    return parts


def pose(c, loc=None, yaw=0, face=None, armL=(0, 0), armR=(0, 0), legL=0, legR=0, head=(0, 0), lean=0, tilt=0):
    """Set a character's whole pose for this frame. All angles in degrees.

    loc   where the feet are (x, y, z): sidewalk z = 0.5, road z = 0.1
    yaw   which way the body faces: 0 = -Y, 180 = +Y, 90 = +X, -90 = -X
    armL / armR  (forward, outward). armL is the arm on the VIEWER'S LEFT when the character faces the camera.
          forward 90 = straight ahead, 180 = straight up. outward 90 = straight out to the side, negative = across the body
    legL / legR  forward swing, negative = back
    head  (turn, look_up): turn > 0 = toward the armR side; look_up > 0 = up, < 0 = down
    lean  < 0 leans FORWARD, > 0 leans back        tilt  sideways, > 0 toward the armR side
    face  a face name (see face_names())
    """
    if loc is not None:
        c["root"].location = loc
    c["root"].rotation_euler = (0, 0, math.radians(yaw))
    c["body"].rotation_euler = (math.radians(-lean), math.radians(tilt), 0)
    for side, sx, (fwd, out) in (("L", -1, armL), ("R", 1, armR)):
        c["arm" + side].rotation_euler = (math.radians(-fwd), math.radians(-sx * out), 0)
    c["legL"].rotation_euler = (math.radians(-legL), 0, 0)
    c["legR"].rotation_euler = (math.radians(-legR), 0, 0)
    c["neck"].rotation_euler = (math.radians(-head[1]), 0, math.radians(head[0]))
    if face:
        m = c.get("face_fn", face_mat)(c["skin"], face)
        if c["face"].data.materials[0] != m:    # only on a real change: a new material makes Blender rebuild the
            c["face"].data.materials[0] = m     # rounded head mesh (~15 ms a character per frame)
        c["face_now"] = face


# ---------------------------------------------------------------- the town
ROAD_W, WALK_W, WALK_H = 24, 9, 0.5
WALK = WALK_H                                     # z of the sidewalk top
ROAD = 0.1                                        # z of the road top
RX, LX = ROAD_W / 2 + 4.5, -(ROAD_W / 2 + 4.5)    # sidewalk centre lines (x = 16.5 and -16.5)
HOUSE_Y = tuple(range(-60, 170, 30))              # the house rows along the street
WIN = mat("#F7CE6E", emit=1.0, key="window")
LAMP_BULB = mat("#FFD08A", emit=1.0, key="bulb")
DARK = mat("#22232B")
SIGN_TEXT = ("#FFD84A", 2.5, "signtext")
LAMPS = []
PAL = [("#7C8C7A", "#657564"), ("#5F6F86", "#4C5A70"), ("#C9B98A", "#AD9D70"), ("#8D6F8F", "#745A76"),
       ("#6E9AA6", "#58808B"), ("#B9826A", "#9B6A55")]     # muted house walls: (wall, band)


def sign_mat():
    return mat(SIGN_TEXT[0], emit=SIGN_TEXT[1], key=SIGN_TEXT[2])


def ground():
    box((900, 900, 1), (0, 100, -0.5), mat("#4E9E3C"))
    box((ROAD_W, 520, 0.2), (0, 60, 0.0), mat("#26262C"))
    for i in range(44):
        box((0.7, 6.5, 0.04), (0, -190 + i * 12, 0.11), mat("#F5C52A"))
    for sx in (-1, 1):
        x = sx * (ROAD_W / 2 + WALK_W / 2)
        box((WALK_W, 520, WALK_H), (x, 60, WALK_H / 2), mat("#C3C6CE"))
        box((0.5, 520, WALK_H + 0.04), (sx * (ROAD_W / 2 + 0.25), 60, WALK_H / 2), mat("#9EA1AA"))
        for i in range(0, 520, 9):
            box((WALK_W - 0.5, 0.12, 0.02), (x + sx * 0.25, -200 + i, WALK_H + 0.005), mat("#A9ACB5"))


PAL2 = [("#F4D06F", "#DDB650"), ("#8CC7E8", "#72B0D4"), ("#F2A0A0", "#DC8686"), ("#A8DDB5", "#8EC89C"),
        ("#D4B5EC", "#BC9BD9"), ("#F7C59F", "#E1AB82"), ("#F1EEE4", "#D9D5C7")]      # world v2: bright house colours
ROOFS2 = ["#B5523B", "#3F5873", "#4E6B50", "#6B4A3A", "#34363F"]
HOUSES = []          # every house: {"x", "y", "win"} (its own window material, so its lights can go off alone)
WIN_K = 1.0          # the current mood's window glow


def house(x, y, colour, dark, w=24, d=18, h=15, roof_h=8, roof="#22232B", door="#3A1E14"):
    r = empty("house", (x, y, 0), yaw=-90 if x > 0 else 90)      # the door faces the road
    WIN = mat("#F7CE6E", emit=1.0, key=("window", x, y))           # this house's windows (window_light)
    HOUSES.append({"x": x, "y": y, "win": WIN, "root": r, "h": h, "roof_h": roof_h, "roof": roof})
    wall = banded(colour, dark)
    box((w, d, h), (0, 0, h / 2), wall, r)
    box((w + 0.6, d + 0.6, 0.7), (0, 0, 0.35), mat("#8A8D96"), r)                       # foundation
    o = 1.4
    v = [(-w / 2 - o, -d / 2 - o, h), (w / 2 + o, -d / 2 - o, h), (0, -d / 2 - o, h + roof_h),
         (-w / 2 - o, d / 2 + o, h), (w / 2 + o, d / 2 + o, h), (0, d / 2 + o, h + roof_h)]
    mesh_obj("roof", v, [(0, 1, 2), (4, 3, 5), (0, 2, 5, 3), (1, 4, 5, 2), (0, 3, 4, 1)], mat(roof), r)
    box((w + 2 * o + 0.2, d + 2 * o + 0.2, 0.5), (0, 0, h - 0.1), mat(roof), r)          # eave
    fy = -d / 2
    trim = mat("#9A9DA6")
    for row, z in enumerate((4.6, 11.0)):
        for col in (-1, 0, 1):
            if row == 0 and col == 0:
                continue
            box((4.4, 0.3, 4.2), (col * 7.4, fy - 0.05, z), WIN, r)
            box((5.0, 0.6, 0.35), (col * 7.4, fy - 0.2, z - 2.25), trim, r)
    box((4.0, 0.3, 2.2), (0, fy - 0.05, h + 2.6), WIN, r)                                # attic window
    box((3.6, 0.3, 6.4), (0, fy - 0.06, 3.9), mat(door), r)
    box((0.3, 0.2, 0.3), (1.2, fy - 0.26, 3.7), mat("#D8A93A"), r)
    box((6, 3, 0.7), (0, fy - 1.5, 0.35), mat("#8A8D96"), r)                             # step
    for sy in (-1, 1):                                                                    # side windows
        for z in (4.6, 11.0):
            box((0.3, 4.0, 4.2), (sy * (w / 2 + 0.05), 0, z), WIN, r)
    return r


SHOPS = []           # every shop's root (world2 dresses them)


def shop(x, y, sign, w=26, d=18, h=14):
    r = empty("shop", (x, y, 0), yaw=-90 if x > 0 else 90)
    r["bt_shop"] = [w, d, h]
    SHOPS.append(r)
    box((w, d, h), (0, 0, h / 2), brick(), r)
    box((w + 1.2, d + 1.2, 1.0), (0, 0, h + 0.5), DARK, r)
    fy = -d / 2
    box((w - 3, 0.5, 3.4), (0, fy - 0.5, h - 2.6), mat("#1B1F3A"), r)                    # sign board
    box((w - 2.6, 0.3, 3.8), (0, fy - 0.35, h - 2.6), mat("#F5C52A"), r)                 # gold frame
    if sign is not None:
        shop_sign(r, sign)
    for sx in (-1, 1):
        box((7.5, 0.3, 6.0), (sx * 7.2, fy - 0.05, 5.0), mat("#9FD8F2", emit=0.25, key="glass"), r)
        box((8.1, 0.5, 0.4), (sx * 7.2, fy - 0.15, 1.9), mat("#E9E2D6"), r)
    box((4.2, 0.3, 7.2), (0, fy - 0.06, 3.6), mat("#2A2C38"), r)
    for i in range(8):                                                                    # striped awning
        box((w / 8, 3.2, 0.25), (-w / 2 + w / 16 + i * w / 8, fy - 1.5, 8.8), mat("#E94B5B" if i % 2 else "#FFFFFF"), r,
            rot=(-18, 0, 0))
    return r


def shop_sign(r, sign):
    """The words on a shop's sign board (kept apart so a saved street can get new shop names per episode)."""
    w, d, h = r["bt_shop"]
    return text(sign, 2.0, (0, -d / 2 - 0.78, h - 2.7), sign_mat(), r, extrude=0.06, max_w=w - 5)


def billboard(x, y, z, title, big, yaw=0):
    """A lit billboard on two posts: a small title line, a big line, and a ruler strip. It faces its local -Y."""
    r = empty("billboard", (x, y, z), yaw=yaw)
    for sx in (-1, 1):
        box((0.7, 0.7, 12), (sx * 6, 0.4, 6), mat("#16171C"), r)
    box((19.6, 0.5, 10.6), (0, 0, 15), mat("#F5C52A"), r)
    box((18.8, 0.5, 9.8), (0, -0.12, 15), mat("#1B1F3A"), r)
    r["bt_billboard"] = True
    if big is not None:
        billboard_text(r, title, big)
    box((16, 0.2, 0.9), (0, -0.42, 11.4), mat("#FFFFFF", emit=1.0, key="bbruler"), r)
    for i in range(17):
        box((0.14, 0.24, 0.6 if i % 4 else 0.9), (-8 + i, -0.46, 11.4), mat("#E94B5B", emit=1.5, key="bbtick"), r)
    return r


def billboard_text(r, title, big):
    text(title, 1.5, (0, -0.42, 17.6), mat("#FFFFFF", emit=1.5, key="bbwhite"), r, extrude=0.05, max_w=17.6)
    text(big, 2.9, (0, -0.42, 14.2), sign_mat(), r, extrude=0.06, max_w=17.6)


def hall_text(r, sign, clock):
    """The town hall's name and its clock face."""
    h = 30
    text(sign, 3.4, (0, -9.2, h + 1.8), sign_mat(), r, extrude=0.1, max_w=70)
    text(clock, 3.2, (0, -0.6, h - 7), mat("#FF3B30", emit=4.0, key="clock"), r, extrude=0.05, max_w=11)


def town_hall(y, sign="TOWN HALL", clock="8:00"):
    r = empty("hall", (0, y, 0))
    w, d, h = 84, 30, 30
    box((w, d, h), (0, d / 2, h / 2), mat("#565C8E"), r)
    for i in range(4):
        box((w + 10 - i * 2, 12 - i * 2.6, 0.9), (0, -3 + i * 1.3, 0.45 + i * 0.9), mat("#D5D7DE"), r)
    for i in range(6):
        box((3.0, 3.0, h - 3.6), (-30 + i * 12, -4.2, 3.6 + (h - 3.6) / 2), mat("#F1F1F4"), r)
    box((w + 8, d + 12, 3.6), (0, d / 2 - 3, h + 1.8), mat("#C9B37C"), r)
    box((w - 6, d, 3), (0, d / 2, h + 5), mat("#B49E69"), r)
    r["bt_townhall"] = True
    box((13, 0.6, 5.2), (0, -0.2, h - 7), mat("#14151A"), r)
    box((11, 0.5, 15), (0, -0.1, 11.1), mat("#2A2C45"), r)
    if sign is not None:
        hall_text(r, sign, clock)
    return r


def tree(x, y, s=1.0, seed=0):
    rng = random.Random(seed)
    r = empty("tree", (x, y, 0))
    box((1.2 * s, 1.2 * s, 6 * s), (0, 0, 3 * s), mat("#5A3A22"), r)
    for i, (dx, dy, dz, rad) in enumerate(((0, 0, 8.4, 3.6), (1.9, 0.6, 7.2, 2.6), (-1.7, -0.8, 7.0, 2.7))):
        o = prim("ico_sphere", subdivisions=2, radius=rad * s)
        for vtx in o.data.vertices:
            vtx.co *= rng.uniform(0.86, 1.14)
        o.data.materials.append(mat(("#3FA338", "#4DB542", "#368E31")[i]))
        o.location = (dx * s, dy * s, dz * s)
        o.rotation_euler = (rng.random(), rng.random(), rng.random())
        o.parent = r
    return r


def lamp(x, y):
    sx = -1 if x > 0 else 1                                   # arm points to the road
    r = empty("lamp", (x, y, WALK_H))
    box((0.5, 0.5, 13.2), (0, 0, 6.6), mat("#15161B"), r)
    box((4.2, 0.4, 0.4), (sx * 2.0, 0, 13.0), mat("#15161B"), r)
    box((2.0, 1.0, 0.5), (sx * 3.6, 0, 12.6), LAMP_BULB, r)
    li = bpy.data.lights.new("lampL", "SPOT")
    li.color = lin("#FFBD6B")[:3]
    li.spot_size = math.radians(118)
    li.spot_blend = 0.5
    li.shadow_soft_size = 0.6
    li["bt_lamp"] = True
    lo = bpy.data.objects.new("lampL", li)
    lo.location = (sx * 3.6, 0, 12.2)
    lo.parent = r
    COL.objects.link(lo)
    LAMPS.append(li)
    return r


def clouds():
    m = mat("#FFFFFF", emit=1.0, key="cloud")
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
    rng = random.Random(4)
    for cx, cy, cz, s in ((-90, 330, 120, 1.0), (60, 360, 150, 1.3), (150, 300, 105, 0.9), (-170, 380, 165, 1.2),
                          (10, 420, 200, 1.5), (-40, 300, 90, 0.7)):
        for i in range(6):
            o = prim("uv_sphere", segments=16, ring_count=8, radius=rng.uniform(10, 17) * s)
            o.location = (cx + (i - 2.5) * 12 * s, cy, cz + rng.uniform(-3, 5) * s)
            o.scale = (1, 0.3, 0.8)
            o.data.materials.append(m)
            o.visible_shadow = False
            o["cloud"] = True


_BUILT = False
_LOOK = None


def use_look(style="roblox", detail=True):
    """Switch the episode's look on once: "roblox" (round heads, printed clothes, plastic; detail = world v2 prints) or
    "block". build_town() and place() call it, so an episode set only indoors still gets the Roblox look."""
    global STYLE, _LOOK
    if _LOOK is not None:
        if _LOOK != (style, bool(detail)):
            raise RuntimeError(f"the look is already {_LOOK}; call build_town(style=...) before any place(...)")
        return
    if style not in ("block", "roblox"):
        raise ValueError(f"style must be 'block' or 'roblox', not {style!r}")
    _LOOK = (style, bool(detail))
    STYLE = style
    if style == "roblox":
        import roblox
        roblox.apply(detail)
        tick("roblox.apply (cast restyle)")


def build_town(rule_big, shop_signs=("CORNER SHOP", "BAKERY"), rule_title="TOWN RULE", hall_sign="TOWN HALL",
               clock="8:00", shop_spots=((1, 30), (-1, 90)), style="block", detail=True):
    """Put up the street. Call once per episode, before any shot.

    rule_big    the rule in 3-5 words for the billboard, e.g. "1 LIE = 1 INCH"
    shop_signs  two shop names that joke about the rule (max about 12 letters each; longer text is shrunk to fit)
    shop_spots  where the two shops replace a house: (side, y) with side 1 = right (+X), -1 = left, y in HOUSE_Y
    The billboard stands on the roof of the first shop, angled toward a camera coming down the street.
    style       "block" (the original look) or "roblox" (round heads, printed clothes, plastic, fog and rain moods:
                see roblox.py and docs/ROBLOX_LOOK.md)
    detail      Roblox look only: the dressed town of world v2 (bright houses with frames, shutters, porches and
                chimneys, gardens and fences, street furniture, parked cars, hills, more trees and clouds: world2.py).
                detail=False gives the plain v1 street.
    """
    global _BUILT, TOD
    if _BUILT:
        raise RuntimeError("build_town() was already called")
    _BUILT = True
    tick("before build_town (episode start)")
    use_look(style, detail)
    import places                                   # the street is a saved place (places/street.py)
    places.place("street", shop_spots=[list(s) for s in shop_spots], style=style, detail=bool(detail and style == "roblox"),
                 rule_big=rule_big, shop_signs=tuple(shop_signs), rule_title=rule_title, hall_sign=hall_sign, clock=clock)
    TOD = None
    time_of_day("day")


# ---------------------------------------------------------------- the recurring cast (keep identical in every episode)
NIA = character("Nia", "#9A5B34", "#FFC533", "#3D4C8A", "pig", "black", sleeves="long", strings=True)
TEACH = character("Teacher", "#E4B58A", "#8A4FB5", "#2B2B3A", "bun", "brown", sleeves="long", stripes="#C9A6E3")
TALL = character("Tall", "#F0C8A0", "#2FB58A", "#2B3350", "tuft", "ginger")
BOY = character("Boy", "#C98A5A", "#E23B3B", "#1F1F27", "cap", "#2B62D9")
DAD = character("Dad", "#7A4A2C", "#2F6FE0", "#3A3A46", "side", "black", sleeves="long", tie="#E23B3B")
GRAN = character("Gran", "#EBC8A8", "#E88BA8", "#6A5A7A", "bun", "grey", sleeves="long", stripes="#FFFFFF")
KID = character("Kid", "#F0C8A0", "#F28A1E", "#31406B", "beanie", "#E2552B", scale=0.8)
MAN = character("Man", "#B97A4A", "#3E3E48", "#22222A", "tuft", "dark", sleeves="long")
ALL = [NIA, TEACH, TALL, BOY, DAD, GRAN, KID, MAN]

# ---------------------------------------------------------------- light, sky, camera
sun_d = bpy.data.lights.new("sun", "SUN")
sun = bpy.data.objects.new("sun", sun_d)
COL.objects.link(sun)
world = bpy.data.worlds.new("sky")
scene.world = world
world.use_nodes = True
wn = world.node_tree
bg = wn.nodes["Background"]
tc = wn.nodes.new("ShaderNodeTexCoord")
sepw = wn.nodes.new("ShaderNodeSeparateXYZ")
ramp = wn.nodes.new("ShaderNodeValToRGB")
wn.links.new(tc.outputs["Generated"], sepw.inputs[0])
wn.links.new(sepw.outputs["Z"], ramp.inputs[0])
wn.links.new(ramp.outputs[0], bg.inputs["Color"])
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[1].position = 0.45

cam_d = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_d)
COL.objects.link(cam)
scene.camera = cam
cam_d.sensor_fit = "VERTICAL"
cam_d.clip_start = 0.05
cam_d.clip_end = 2000
ELEV = 50
TOD = None
NOW = 0.0           # seconds since the video began, set by the runner each frame (moving rain uses it)
TOD_HOOKS = []      # functions called with the new mode after time_of_day() changes it (the roblox look)
PRE_RENDER = []     # functions called right before each render (the roblox look)
TIMES = {  # horizon, zenith, sky strength, sun strength, sun colour, sun elevation, windows, bulbs, lamp watts, clouds
    "day": ("#BDE4FA", "#5CB6F2", 1.3, 3.2, "#FFF6E6", 50, 1.0, 1.0, 0, 1.0),
    "dusk": ("#B3B1C2", "#868AA0", 1.15, 1.2, "#D6DCFF", 34, 2.0, 4.0, 2500, 0.62),
    "night": ("#2A3566", "#0A0E24", 1.6, 1.2, "#9EB8FF", 48, 3.2, 9.0, 14000, 0.05),
}


def emission(material, strength):
    material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = strength


def window_light(house, k):
    """Switch one house's windows: k = 1 lit (the mood's level), 0 dark, in between dimmed. house = an index into
    HOUSES or an (x, y) spot (the nearest house). Call it inside a shot; every frame starts with all windows lit."""
    if not isinstance(house, int):
        house = min(range(len(HOUSES)), key=lambda i: (HOUSES[i]["x"] - house[0]) ** 2 + (HOUSES[i]["y"] - house[1]) ** 2)
    emission(HOUSES[house]["win"], WIN_K * k)


def _windows_reset():
    for hs in HOUSES:
        emission(hs["win"], WIN_K)


def time_of_day(mode):
    """"day", "dusk" or "night". Call it inside a shot function BEFORE shot(); every frame starts as the episode default."""
    global ELEV, TOD, WIN_K
    if mode == TOD:
        _windows_reset()
        return
    if mode not in TIMES:
        raise ValueError(f"no time of day {mode!r}. Choose from: {', '.join(TIMES)}")
    horizon, zenith, sky, sun_e, sun_c, elev, win, bulb, lamps, cloud = TIMES[mode]
    TOD = mode
    ramp.color_ramp.elements[0].color = lin(horizon)
    ramp.color_ramp.elements[1].color = lin(zenith)
    bg.inputs["Strength"].default_value = sky
    sun_d.energy = sun_e
    sun_d.color = lin(sun_c)[:3]
    sun_d.angle = math.radians(6)
    ELEV = elev
    emission(WIN, win)
    WIN_K = win
    _windows_reset()
    emission(LAMP_BULB, bulb)
    if "cloud" in MATS:
        emission(MATS["cloud"], cloud)
    for li in LAMPS:
        li.energy = lamps
    for o in bpy.data.objects:
        if o.get("cloud"):
            o.hide_render = mode == "night"
    for h in TOD_HOOKS:
        h(mode)


key_d = bpy.data.lights.new("key", "POINT")
key_d.shadow_soft_size = 2.0
key = bpy.data.objects.new("key", key_d)
COL.objects.link(key)


DOF = None            # anim.dof(k) sets it for one frame: the background blur of the world v2 renderer


def shot(pos, target, fov, side=0.55, key_w=0, key_col="#FFC98A", roll=0):
    """Aim the camera from pos at target with a VERTICAL field of view of fov degrees.

    The sun is brought from behind the camera's left, so faces are lit from any angle.
    key_w > 0 switches on a lamp that rides with the camera (night: 420 for a close-up, 900 for a group).
    roll tilts the frame (degrees), for a dutch angle.
    """
    cam.location = pos
    look = Vector(target) - Vector(pos)
    q = look.to_track_quat("-Z", "Y")
    if roll:                                          # a tilted ("dutch") frame: roll degrees around the view axis
        from mathutils import Quaternion
        q = q @ Quaternion((0, 0, 1), math.radians(roll))
    cam.rotation_euler = q.to_euler()
    cam_d.angle = math.radians(fov)
    fwd = Vector((look.x, look.y, 0))
    fwd = fwd.normalized() if fwd.length > 1e-4 else Vector((0, 1, 0))      # looking straight down
    left = Vector((-fwd.y, fwd.x, 0))
    ray = fwd * 0.8 - left * -side - Vector((0, 0, math.tan(math.radians(ELEV))))
    sun.rotation_euler = ray.to_track_quat("-Z", "Y").to_euler()
    key.location = Vector(pos) + left * 2.5 + Vector((0, 0, 2.0))
    key_d.energy = key_w
    key_d.color = lin(key_col)[:3]


def park(*chars):
    """Move characters far out of sight."""
    for i, c in enumerate(chars):
        pose(c, loc=(300 + i * 12, -300, 0))


def setup_render(width, height, samples, quality=93):
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):      # the name differs between Blender 4.2-4.5 and 5.x
        try:
            scene.render.engine = engine
            break
        except TypeError:
            pass
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = quality
    scene.eevee.taa_render_samples = samples
    try:
        scene.eevee.use_raytracing = True
    except AttributeError:
        pass
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0


def render_still(path):
    for h in PRE_RENDER:
        h()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


tick("town import (8 characters, sky, camera)")
