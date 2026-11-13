"""World v2: dresses the Roblox-look street so it looks lived in. build_town(style="roblox") calls dress() unless
detail=False. Everything is code-built; nothing here moves (trees sway through the life layer because their roots are
named "tree...").

What it adds
    houses      window frames and mullions, shutters, flower boxes, a door frame with a porch roof, a chimney
    gardens     a picket fence with a gate gap, a path to the door, bushes, flowers, a mailbox
    street      zebra crossings, manholes, hydrants, benches, bins, parked cars (all off the lanes people walk in:
                the middle of the road and the sidewalk between x = 14 and 19 stay clear)
    shops       plant pots by the door, a wall lamp
    town hall   a pediment, tall windows, two flags
    far away    more trees between and behind the houses, a back row of roofs, hills all round, more clouds
"""
import math
import random

import bpy

import town as T

GREENS = ("#3FA338", "#4DB542", "#368E31", "#58BF4C")
FLOWERS = ("#FF5A8A", "#FFD23A", "#FFFFFF", "#B77BFF", "#FF8A3A")


# ---------------------------------------------------------------- builders
def multi(name, parts, material, parent=None):
    """Many plain boxes as ONE object (fences, frames, stripes): parts = [((sx, sy, sz), (x, y, z)), ...]."""
    verts, faces = [], []
    for (sx, sy, sz), (x, y, z) in parts:
        n = len(verts)
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        verts += [(x - hx, y - hy, z - hz), (x + hx, y - hy, z - hz), (x + hx, y + hy, z - hz), (x - hx, y + hy, z - hz),
                  (x - hx, y - hy, z + hz), (x + hx, y - hy, z + hz), (x + hx, y + hy, z + hz), (x - hx, y + hy, z + hz)]
        faces += [(n, n + 3, n + 2, n + 1), (n + 4, n + 5, n + 6, n + 7), (n, n + 1, n + 5, n + 4),
                  (n + 1, n + 2, n + 6, n + 5), (n + 2, n + 3, n + 7, n + 6), (n + 3, n, n + 4, n + 7)]
    return T.mesh_obj(name, verts, faces, material, parent)


def ico(radius, loc, material, parent=None, scale=(1, 1, 1), rng=None, sub=2):
    """A lumpy low-poly ball (bushes, tree crowns, hills)."""
    o = T.prim("ico_sphere", subdivisions=sub, radius=radius)
    if rng:
        for v in o.data.vertices:
            v.co *= rng.uniform(0.88, 1.12)
    o.data.materials.append(material)
    o.location, o.scale, o.parent = loc, scale, parent
    return o


def discs(name, spots, material, z=0.08, sides=9):
    """Flat patches on the ground as one object: spots = [(x, y, radius), ...]."""
    verts, faces = [], []
    for x, y, r in spots:
        n = len(verts)
        verts += [(x + r * math.cos(i * 2 * math.pi / sides) * (0.8 + 0.4 * ((i * 7) % 3) / 2),
                   y + r * math.sin(i * 2 * math.pi / sides), z) for i in range(sides)]
        faces.append(tuple(range(n, n + sides)))
    o = T.mesh_obj(name, verts, faces, material)
    o.visible_shadow = False
    return o


def prism(name, w, d, h, loc, material, parent=None):
    """A roof / pediment: a triangle of width w and height h, pulled d deep (along local Y)."""
    v = [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (0, -d / 2, h), (-w / 2, d / 2, 0), (w / 2, d / 2, 0), (0, d / 2, h)]
    o = T.mesh_obj(name, v, [(0, 1, 2), (4, 3, 5), (0, 2, 5, 3), (1, 4, 5, 2), (0, 3, 4, 1)], material, parent)
    o.location = loc
    return o


# ---------------------------------------------------------------- houses and gardens
def _house(h, k, rng):
    r, fy, hh = h["root"], -9.0, h["h"]
    white = T.mat("#F7F4EC")
    accent = T.mat(("#3F6FA8", "#B5523B", "#2F7A5B", "#7A4FA0", "#D98A2B", "#3A4A66")[k % 6])
    frames, shut = [], []
    for row, z in enumerate((4.6, 11.0)):
        for col in (-1, 0, 1):
            if row == 0 and col == 0:
                continue
            cx = col * 7.4
            frames += [((5.1, 0.3, 0.38), (cx, fy - 0.26, z + 2.28)), ((0.38, 0.3, 4.9), (cx - 2.36, fy - 0.26, z)),
                       ((0.38, 0.3, 4.9), (cx + 2.36, fy - 0.26, z)), ((0.2, 0.16, 4.2), (cx, fy - 0.2, z)),
                       ((4.4, 0.16, 0.2), (cx, fy - 0.2, z))]
            shut += [((1.05, 0.22, 4.5), (cx - 3.15, fy - 0.16, z)), ((1.05, 0.22, 4.5), (cx + 3.15, fy - 0.16, z))]
    frames += [((4.6, 0.3, 0.38), (0, fy - 0.26, hh + 3.9)), ((4.6, 0.3, 0.38), (0, fy - 0.26, hh + 1.3)),      # attic
               ((0.38, 0.3, 3.0), (-2.15, fy - 0.26, hh + 2.6)), ((0.38, 0.3, 3.0), (2.15, fy - 0.26, hh + 2.6)),
               ((4.6, 0.3, 0.45), (0, fy - 0.26, 7.35)), ((0.45, 0.3, 7.0), (-2.05, fy - 0.26, 3.85)),          # door frame
               ((0.45, 0.3, 7.0), (2.05, fy - 0.26, 3.85))]
    multi("house.trim", frames, white, r)
    multi("house.shutters", shut, accent, r)
    T.box((1.7, 0.12, 1.5), (0, fy - 0.26, 5.6), T.mat("#BFE9FA", emit=0.3, key="glass2"), r)              # door window
    roof = T.mat(h["roof"])
    porch = T.box((7.6, 3.8, 0.4), (0, fy - 1.7, 8.25), roof, r, rot=(-13, 0, 0))                           # porch roof
    multi("house.porch", [((0.45, 0.45, 7.3), (-3.3, fy - 3.0, 4.0)), ((0.45, 0.45, 7.3), (3.3, fy - 3.0, 4.0))], white, r)
    brick = T.mat("#A8513C")
    cx = 6.5 if k % 2 else -6.5
    multi("house.chimney", [((2.4, 2.4, 6.5), (cx, 2.5, hh + h["roof_h"] * 0.42 + 2.0)),
                            ((2.9, 2.9, 0.6), (cx, 2.5, hh + h["roof_h"] * 0.42 + 5.4))], brick, r)
    boxes, blooms = [], {c: [] for c in FLOWERS}
    for col in (-1, 1):                                             # flower boxes under the ground-floor windows
        cx = col * 7.4
        boxes.append(((4.8, 0.9, 0.7), (cx, fy - 0.62, 2.05)))
        for i in range(7):
            blooms[rng.choice(FLOWERS)].append(((0.42, 0.42, 0.42), (cx - 1.95 + i * 0.65, fy - 0.7 + rng.uniform(-0.15, 0.15),
                                                                 2.55 + rng.uniform(0, 0.25))))
    multi("house.flowerbox", boxes, T.mat("#7A4A2C"), r)
    for sx_ in (-1, 1):                                             # bushes against the wall
        ico(1.5, (sx_ * 7.4, fy - 1.6, 0.9), T.mat(rng.choice(GREENS)), r, scale=(1.5, 0.85, 0.75), rng=rng)
    for c, parts in blooms.items():
        if parts:
            multi("house.flowers", parts, T.mat(c, emit=0.25, key=("flower", c)), r)


def _garden(h, k, rng):
    """Fence, gate gap, path, mailbox and flower dots, in world coordinates (the house's door faces the road)."""
    x, y = h["x"], h["y"]
    sx = 1 if x > 0 else -1
    fx = sx * 21.7
    pick, white = [], T.mat("#FBFAF5")
    yy = y - 11.6
    while yy <= y + 11.6:
        if abs(yy - y) > 2.4:
            pick.append(((0.22, 0.5, 1.7), (fx, yy, 0.85)))
        yy += 0.95
    for ya, yb in ((y - 11.6, y - 2.4), (y + 2.4, y + 11.6)):
        for z in (0.55, 1.2):
            pick.append(((0.16, yb - ya, 0.2), (fx - sx * 0.02, (ya + yb) / 2, z)))
    for yy in (y - 2.4, y + 2.4):                                   # gate posts
        pick.append(((0.4, 0.4, 2.0), (fx, yy, 1.0)))
    multi("fence", pick, white)
    multi("path", [((3.2, 3.6, 0.14), (sx * 22.6, y, 0.07)), ((2.0, 3.0, 0.14), (sx * 25.2, y, 0.07))], T.mat("#D9D2C2"))
    my = y + 3.3
    multi("mailbox.post", [((0.25, 0.25, 2.2), (fx + sx * 0.9, my, 1.1))], T.mat("#6B4A33"))
    multi("mailbox", [((1.1, 0.75, 0.7), (fx + sx * 0.9, my, 2.45))], T.mat(("#D62B2B", "#2B62D9", "#F2F2F2")[k % 3]))
    dots = {c: [] for c in FLOWERS}
    for i in range(10):
        dots[rng.choice(FLOWERS)].append(((0.38, 0.38, 0.5), (fx + sx * rng.uniform(0.7, 2.0),
                                                             y + rng.choice((-1, 1)) * rng.uniform(5.0, 11.0), 0.25)))
    for c, parts in dots.items():
        if parts:
            multi("garden.flowers", parts, T.mat(c, emit=0.25, key=("flower", c)))


# ---------------------------------------------------------------- street furniture
def bench(x, y, yaw=0):
    r = T.empty("bench", (x, y, T.WALK), yaw=yaw)
    wood, iron = T.mat("#9A6A3C"), T.mat("#2B2D33")
    multi("bench.wood", [((4.4, 0.5, 0.2), (0, -0.45 + i * 0.55, 1.5)) for i in range(3)]
          + [((4.4, 0.2, 0.5), (0, 0.85, 2.0 + i * 0.65)) for i in range(2)], wood, r)
    multi("bench.iron", [((0.25, 1.6, 1.5), (sx * 1.9, 0.1, 0.75)) for sx in (-1, 1)]
          + [((0.25, 0.25, 1.6), (sx * 1.9, 0.85, 2.1)) for sx in (-1, 1)], iron, r)
    return r


def hydrant(x, y):
    red = T.mat("#E0352B")
    multi("hydrant", [((0.8, 0.8, 1.5), (x, y, T.WALK + 0.75)), ((1.0, 1.0, 0.25), (x, y, T.WALK + 0.13)),
                      ((0.6, 0.6, 0.4), (x, y, T.WALK + 1.7)), ((1.5, 0.35, 0.35), (x, y, T.WALK + 1.0)),
                      ((0.35, 1.2, 0.35), (x, y, T.WALK + 1.0))], red)


def bin_(x, y):
    multi("bin", [((1.3, 1.3, 2.0), (x, y, T.WALK + 1.0))], T.mat("#3E6B4A"))
    multi("bin.rim", [((1.5, 1.5, 0.25), (x, y, T.WALK + 2.05))], T.mat("#2B2D33"))


def _street(rng):
    white, dark = T.mat("#F2F2F2"), T.mat("#1B1B20")
    stripes = []
    for cy in (75.0, -15.0):                                        # zebra crossings
        for i in range(8):
            stripes.append(((1.6, 6.0, 0.03), (-9.8 + i * 2.8, cy, 0.125)))
    for sx in (-1, 1):                                              # a thin line along each kerb
        stripes.append(((0.25, 520, 0.03), (sx * 11.2, 60, 0.12)))
    multi("road.paint", stripes, white).visible_shadow = False
    discs("road.manholes", [(4.0, 30.0, 1.3), (-5.0, 118.0, 1.3), (5.5, -40.0, 1.3)], T.mat("#3A3A42"), z=0.125, sides=12)
    for x, y in ((13.3, 36.0), (-13.3, 112.0), (13.3, 160.0), (-13.3, -24.0)):
        hydrant(x, y)
    bench(20.1, 44.0, yaw=90)
    bench(-20.1, 104.0, yaw=-90)
    bench(20.1, 134.0, yaw=90)
    for x, y in ((20.3, 50.5), (-20.3, 97.5), (20.3, -6.0)):
        bin_(x, y)
    from props import car
    for x, y, col, yaw in ((-9.2, -52.0, "#2B62D9", 0), (9.2, -28.0, "#F2C230", 180), (-9.2, 6.0, "#3BB573", 0),
                           (9.2, 172.0, "#E8E8EC", 180)):
        car(x, y, col=col, yaw=yaw)


def _shops():
    pot, leaf = T.mat("#B5653A"), T.mat("#3FA338")
    for r in T.SHOPS:
        for sx in (-1, 1):
            multi("shop.pot", [((1.3, 1.3, 1.2), (sx * 3.6, -10.4, 0.6))], pot, r)
            ico(1.1, (sx * 3.6, -10.4, 2.1), leaf, r, scale=(1, 1, 1.25))
        multi("shop.frame", [((5.0, 0.3, 0.45), (0, -9.3, 7.45)), ((0.45, 0.3, 7.4), (-2.3, -9.3, 3.7)),
                             ((0.45, 0.3, 7.4), (2.3, -9.3, 3.7))], T.mat("#E9E2D6"), r)
        T.box((0.7, 0.5, 0.9), (6.0, -9.4, 9.9), T.LAMP_BULB, r)


def _town_hall():
    hall = next((o for o in bpy.data.objects if o.get("bt_townhall") and o.parent is None), None)
    if hall is None:
        return
    stone, glass = T.mat("#E9E6DC"), T.mat("#9FD8F2", emit=0.25, key="glass")
    prism("hall.pediment", 70, 6, 11, (0, -6.0, 33.6), stone, hall)
    wins = [((6.0, 0.4, 9.0), (x, -0.25, 19.5)) for x in (-24, -12, 12, 24)]
    multi("hall.windows", wins, glass, hall)
    multi("hall.winframes", [((6.8, 0.3, 0.5), (x, -0.3, 24.2)) for x in (-24, -12, 12, 24)]
          + [((6.8, 0.3, 0.5), (x, -0.3, 14.8)) for x in (-24, -12, 12, 24)], stone, hall)
    for sx, col in ((-1, "#E0352B"), (1, "#2B62D9")):
        multi("hall.flagpole", [((0.4, 0.4, 20), (sx * 40, -12, 10))], T.mat("#D5D7DE"), hall)
        T.box((5.0, 0.12, 3.0), (sx * 40 + 2.7, -12, 18.2), T.mat(col), hall)


# ---------------------------------------------------------------- trees, hills, clouds, the lawn
def tree2(x, y, s=1.0, kind="round", seed=0):
    """Extra trees: "round" (like the street trees), "pine" (three cones), "blossom" (pink)."""
    rng = random.Random(seed)
    r = T.empty("tree2", (x, y, 0))
    T.box((1.1 * s, 1.1 * s, 5.5 * s), (0, 0, 2.75 * s), T.mat("#5A3A22"), r)
    if kind == "pine":
        for i, (z, rad) in enumerate(((5.0, 3.6), (8.2, 2.8), (11.0, 1.9))):
            o = T.prim("cone", vertices=7, radius1=rad * s, radius2=0, depth=4.6 * s)
            o.data.materials.append(T.mat(("#2F7A46", "#35874E", "#3C9456")[i]))
            o.location, o.parent = (0, 0, z * s), r
    else:
        cols = ("#F29AC0", "#F7B3D0", "#EE86B2") if kind == "blossom" else GREENS
        for i, (dx, dy, dz, rad) in enumerate(((0, 0, 8.0, 3.4), (1.8, 0.6, 6.9, 2.5), (-1.6, -0.8, 6.7, 2.6))):
            ico(rad * s, (dx * s, dy * s, dz * s), T.mat(cols[i % len(cols)]), r, rng=rng)
    return r


def _nature(rng):
    k = 0
    for sx in (-1, 1):
        for y in T.HOUSE_Y:                                         # between the houses and behind them
            k += 1
            tree2(sx * 31.5, y + 15, 0.9 + 0.1 * (k % 3), ("pine", "blossom", "round")[k % 3], seed=200 + k)
            tree2(sx * rng.uniform(52, 60), y + rng.uniform(-8, 8), rng.uniform(1.1, 1.5), ("round", "pine")[k % 2],
                  seed=300 + k)
        for i, y in enumerate(range(-70, 200, 45)):                 # a back row of plain roofs: more town behind
            c = T.PAL2[(i + (sx > 0) * 3) % len(T.PAL2)][0]
            bx = sx * 78
            multi("backhouse", [((20, 24, 13), (bx, y, 6.5))], T.mat(c))
            o = prism("backroof", 24, 26, 7, (bx, y, 13), T.mat(T.ROOFS2[i % len(T.ROOFS2)]))
            o.rotation_euler = (0, 0, math.radians(90))
    hills = []
    for i in range(22):                                             # hills all round the town
        a = i / 22 * 2 * math.pi + rng.uniform(-0.08, 0.08)
        dist = rng.uniform(250, 330)
        hills.append((dist * math.cos(a), 60 + dist * math.sin(a), rng.uniform(70, 120), rng.uniform(0.28, 0.5)))
    for i, (hx, hy, rad, zk) in enumerate(hills):
        o = ico(rad, (hx, hy, -6), T.mat(("#4C9A4A", "#5AAE52", "#3F8A44", "#66B85A")[i % 4]), scale=(1.25, 1.25, zk),
                rng=rng, sub=2)
        o.visible_shadow = False
    light, dark, spots_l, spots_d = T.mat("#5CB548"), T.mat("#449236"), [], []
    for _ in range(90):                                             # lighter and darker patches in the grass
        x = rng.choice((-1, 1)) * rng.uniform(46, 140)
        (spots_l if rng.random() < 0.5 else spots_d).append((x, rng.uniform(-150, 260), rng.uniform(3, 9)))
    discs("lawn.light", spots_l, light)
    discs("lawn.dark", spots_d, dark)
    cm = T.MATS.get("cloud")
    if cm:                                                          # clouds in every direction, not only ahead
        for cx, cy, cz, s in ((-260, 120, 130, 1.2), (250, 40, 150, 1.0), (-230, -120, 170, 1.3), (220, 230, 120, 0.9),
                              (120, -260, 160, 1.4), (-90, -300, 140, 1.1), (300, -140, 180, 1.2), (-300, 300, 150, 1.0)):
            for i in range(5):
                o = T.prim("uv_sphere", segments=16, ring_count=8, radius=rng.uniform(10, 17) * s)
                o.location = (cx + (i - 2) * 12 * s * (0 if abs(cx) > abs(cy) else 1), cy + (i - 2) * 12 * s *
                              (1 if abs(cx) > abs(cy) else 0), cz + rng.uniform(-3, 5) * s)
                o.scale = (0.3, 1, 0.8) if abs(cx) > abs(cy) else (1, 0.3, 0.8)
                o.data.materials.append(cm)
                o.visible_shadow = False
                o["cloud"] = True


def dress(shop_spots=()):
    rng = random.Random(7)
    for k, h in enumerate(T.HOUSES):
        _house(h, k, rng)
        _garden(h, k, rng)
    _street(rng)
    _shops()
    _town_hall()
    _nature(rng)
