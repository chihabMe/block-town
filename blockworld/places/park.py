"""The town park: two paths crossing at a fountain, a pond with ducks (north-west), a playground (north-east) with a
slide tower, a swing set, a seesaw and a sandbox, benches, street lamps, flower beds, trees, and a park sign at the
south gate. Parked on its own plot at (1000, 0) with hills and far-off houses all round.

Episode arguments (never saved):
    sign     the words on the park sign at the gate (default "TOWN PARK")
Helpers (call inside a shot): p["swing"](T, amp=25) swings both swings, p["seesaw"](T, amp=14) rocks the seesaw;
both rest still unless called.
Marks:  bench_1, bench_2 (sitting), swing_1, swing_2 (sitting on the swings, facing -Y; a sitter does not swing with
        the seat), slide_top (on the tower),
        slide_bottom (at the foot of the slide), sandbox, pond (at the pond's edge, looking at it), fountain (in front of
        it), path (on the south path, facing the fountain), gate (at the park sign, facing in)
Cams:   wide (high over the whole park), playground, swings, pond, bench, fountain, gate
"""
import math

import town as T
from roblox import blob, disc, plastic, rbox
from world2 import bench, bin_, ico, multi, prism, tree2

from places import _outdoor

GEO = ("x", "y")
PATH = "#D8CBB0"


def build(x=1000, y=0):
    W = T.WALK
    _outdoor.backdrop(x, y, seed=11, ring="houses", clear=66, trees=26)
    r = T.empty("park", (x, y, 0))
    r["bt_root"] = True
    path = plastic(PATH, 0.7)
    rbox((120, 5.0, W), (0, 0, W / 2), path, r, bv=0.05)                                     # the paths
    rbox((5.0, 120, W), (0, 0, W / 2), path, r, bv=0.05)
    for bx, by in ((-12, 4.9), (14, -4.9)):                                                    # bench pads
        rbox((6.0, 3.2, W), (bx, by, W / 2), path, r, bv=0.05)
    # the fountain where the paths cross
    stone, water = plastic("#C9C2B3", 0.6), plastic("#3FA9D9", 0.08)
    disc(5.2, 1.4, (0, 0, W + 0.7), stone, r, rot=(0, 0, 0), bv=0.2, verts=40)
    disc(4.5, 0.2, (0, 0, W + 1.35), water, r, rot=(0, 0, 0), bv=0, verts=40)
    disc(0.7, 4.0, (0, 0, W + 2.6), stone, r, rot=(0, 0, 0), bv=0.1, verts=20)
    disc(2.0, 0.5, (0, 0, W + 4.6), stone, r, rot=(0, 0, 0), bv=0.15, verts=28)
    blob((0.7, 0.7, 1.1), (0, 0, W + 5.4), T.mat("#BFE9FA", emit=0.6, key=("glow", "#BFE9FA", 0.6)), r)   # the spout
    # the pond with stones and two ducks
    disc(12, 0.2, (-24, 22, 0.08), water, r, rot=(0, 0, 0), bv=0, verts=48)
    for i in range(22):
        a = i / 22 * 2 * math.pi
        ico(0.9 + 0.3 * (i % 3), (-24 + 12.4 * math.cos(a), 22 + 12.4 * math.sin(a), 0.2),
            T.mat(("#9A9EA6", "#B5B9C1")[i % 2]), r, scale=(1, 1, 0.55))
    for dx, dy, yaw in ((-27, 25, 30), (-20, 19, -60)):
        d = T.empty("duck", (dx, dy, 0.25), r, yaw=yaw)
        blob((0.9, 0.6, 0.5), (0, 0, 0.3), plastic("#FFD23A", 0.4), d)
        blob((0.4, 0.4, 0.4), (0, -0.7, 0.85), plastic("#FFD23A", 0.4), d)
        rbox((0.3, 0.35, 0.12), (0, -1.15, 0.8), plastic("#F28A1E", 0.4), d, bv=0.04)
    # the playground: sand, slide tower, swings, seesaw, sandbox
    rbox((36, 32, 0.1), (24, 22, 0.05), plastic("#E8D39A", 0.9), r, bv=0)
    red, blue, yel = plastic("#E23B3B", 0.35), plastic("#2F6FE0", 0.35), plastic("#FFC533", 0.3)
    multi("slide.posts", [((0.5, 0.5, 9.0), (16 + sx, 28 + sy, 4.5)) for sx in (-2, 2) for sy in (-2, 2)], red, r)
    rbox((4.6, 4.6, 0.4), (16, 28, 5.0), plastic("#8A5A3C", 0.5), r, bv=0.05)                # platform (top 5.2)
    multi("slide.rail", [((4.4, 0.2, 1.2), (16, 28 + sy, 6.0)) for sy in (-2, 2)], blue, r)
    o = prism("slide.roof", 5.6, 5.6, 2.6, (16, 28, 9.0), blue, r)
    multi("slide.ladder", [((0.25, 0.25, 5.4), (16 + lx, 25.6 - 0.4, 2.6)) for lx in (-0.9, 0.9)]
          + [((2.0, 0.22, 0.22), (16, 25.2, 0.9 + k * 1.0)) for k in range(5)], yel, r)
    ang = math.radians(30)
    L = 5.0 / math.sin(ang)
    sx0 = 18.3 + L * math.cos(ang) / 2
    rbox((L, 2.0, 0.25), (sx0, 28, 5.0 / 2), yel, r, rot=(0, ang * 180 / math.pi, 0), bv=0.06)        # the slide
    for sy in (-1.05, 1.05):
        rbox((L, 0.2, 0.6), (sx0, 28 + sy, 5.0 / 2 + 0.35), yel, r, rot=(0, ang * 180 / math.pi, 0), bv=0.05)
    frame = plastic("#2F6FE0", 0.35)
    for fx in (25, 37):                                                                        # swing A-frames
        for sy in (-1, 1):
            rbox((0.45, 0.45, 8.6), (fx, 30 + sy * 1.6, 4.1), frame, r, rot=(sy * 11, 0, 0), bv=0.05)
    rbox((12.6, 0.5, 0.5), (31, 30, 8.2), frame, r, bv=0.05)
    for k, swx in enumerate((28.5, 33.5)):
        pv = T.empty("swing", (swx, 30, 8.0), r)
        pv["bt_swing"] = True
        pv["bt_live"] = True
        multi("swing.chains", [((0.1, 0.1, 6.1), (sx, 0, -3.05)) for sx in (-0.9, 0.9)], plastic("#9EA1AA", 0.25), pv)
        rbox((2.2, 1.1, 0.2), (0, 0, -6.1), plastic(("#E23B3B", "#3BB54A")[k], 0.4), pv, bv=0.05)   # seat top 2.0
    rbox((1.0, 1.4, 1.0), (24, 12, 0.5), plastic("#5A606B", 0.4), r, bv=0.1)                 # seesaw base
    sw = T.empty("seesaw", (24, 12, 1.1), r)
    sw["bt_seesaw"] = True
    sw["bt_live"] = True
    rbox((10, 1.2, 0.3), (0, 0, 0), plastic("#FF7FB0", 0.4), sw, bv=0.08)
    multi("seesaw.handles", [((0.2, 1.0, 1.0), (sx, 0, 0.6)) for sx in (-3.8, 3.8)], plastic("#5A606B", 0.3), sw)
    wood = plastic("#9A6A42", 0.6)
    multi("sandbox", [((6.6, 0.5, 0.8), (34, 12 + sy, 0.4)) for sy in (-3, 3)]
          + [((0.5, 6.6, 0.8), (34 + sx, 12, 0.4)) for sx in (-3, 3)], wood, r)
    rbox((5.6, 5.6, 0.5), (34, 12, 0.25), plastic("#F0DDA2", 0.9), r, bv=0.1)
    rbox((0.8, 0.8, 0.8), (35.2, 13.0, 0.9), red, r, bv=0.15)                                 # a bucket
    # benches, bins, lamps, flower beds, the park sign
    bench(x - 12, y + 4.4, yaw=0)
    bench(x + 14, y - 4.4, yaw=180)
    bin_(x - 7.5, y + 4.2)
    bin_(x + 19.5, y - 4.2)
    for lx, ly in ((-3.8, -24), (3.8, 24), (-24, 3.8), (24, -3.8), (3.8, -46)):
        T.lamp(x + lx, y + ly)
    flowers = {c: [] for c in ("#FF5A8A", "#FFD23A", "#FFFFFF", "#B77BFF")}
    for bx, by in ((-14, -14), (14, -16), (-40, -8)):
        disc(4.0, 0.3, (bx, by, 0.15), plastic("#5A3A22", 0.9), r, rot=(0, 0, 0), bv=0.05, verts=24)
        for i in range(14):
            a, d = i * 2.4, 0.8 + (i % 4) * 0.8
            list(flowers.values())[i % 4].append(((0.5, 0.5, 0.5), (bx + d * math.cos(a), by + d * math.sin(a), 0.6)))
    for col, parts in flowers.items():
        multi("park.flowers", parts, plastic(col, 0.5), r)
    for k, (tx, ty, kind) in enumerate(((-40, 30, "round"), (-44, -30, "pine"), (42, -26, "blossom"), (46, 44, "round"),
                                        (-8, 44, "blossom"), (10, -40, "round"), (-30, -44, "round"), (50, 4, "pine"))):
        tree2(x + tx, y + ty, 1.1 + 0.1 * (k % 3), kind, seed=700 + k)
    for sx in (-1.6, 1.6):                                                                    # park sign posts
        rbox((0.5, 0.5, 6.0), (sx * 3.6, -52, 3.0), plastic("#7A4A2C", 0.5), r, bv=0.05)
    board = rbox((9.0, 0.5, 2.6), (0, -52, 5.2), plastic("#2F5440", 0.6), r, bv=0.1)
    board["bt_sign"] = True
    marks = {"bench_1": (x - 12, y + 4.5, 0.1, 0), "bench_2": (x + 14, y - 4.5, 0.1, 180),
             "swing_1": (x + 28.5, y + 30, 0.0, 0), "swing_2": (x + 33.5, y + 30, 0.0, 0),
             "slide_top": (x + 16, y + 28, 5.2, 90), "slide_bottom": (x + 28.8, y + 26.5, 0.1, -90),
             "sandbox": (x + 34, y + 7.6, 0.1, 180), "pond": (x - 24, y + 7.4, 0.1, 180),
             "fountain": (x + 1.5, y - 7.5, W, 180), "path": (x, y - 30, W, 180), "gate": (x, y - 47, W, 180)}
    cams = {"wide": ((x - 38, y - 44, 24), (x + 6, y + 12, 2.0), 52),
            "playground": ((x + 6, y - 4, 7.5), (x + 26, y + 24, 3.5), 50),
            "swings": ((x + 31, y + 16.5, 4.6), (x + 31, y + 30, 3.4), 48),
            "pond": ((x - 13, y - 3, 6.5), (x - 24, y + 22, 1.2), 50),
            "bench": ((x - 13.5, y - 7.5, 4.6), (x - 12, y + 4.5, 3.4), 44),
            "fountain": ((x + 9, y - 17, 5.0), (x, y, 4.0), 48),
            "gate": ((x + 2, y - 68, 6.5), (x, y - 40, 4.5), 50)}
    return {"marks": marks, "cams": cams}


def dress(p, sign="TOWN PARK"):
    import anim
    b = p.one("bt_sign")
    bx, by, bz = b.location
    T.text(sign, 1.3, (bx, by - 0.3, bz), T.mat("#F4F4EE", emit=0.4, key="parksign"), p.root, extrude=0.04, max_w=8.2)
    swings, saw = p.tagged("bt_swing"), p.one("bt_seesaw")

    def rest(Tm):
        for s in swings:
            s.rotation_euler = (0, 0, 0)
        saw.rotation_euler = (0, 0, 0)
    anim.before_each_frame(rest)

    def swing(Tm, amp=25):
        for k, s in enumerate(swings):
            s.rotation_euler = (math.radians(amp * math.sin(Tm * 2 * math.pi * 0.55 + k * 1.3)), 0, 0)

    def seesaw(Tm, amp=14):
        saw.rotation_euler = (0, math.radians(amp * math.sin(Tm * 2 * math.pi * 0.5)), 0)
    p.update({"swing": swing, "seesaw": seesaw})
