"""Outside the school: a two-storey brick school with a columned entrance, steps, a name board and a clock, a paved
yard with hopscotch, a bike rack and a flagpole, a fence with a gate along the sidewalk, a road in front with a zebra
crossing, a bus stop with a shelter and the yellow school bus at the kerb. Parked on its own plot at (2000, 0).
The school faces -Y (toward the road).

Episode arguments (never saved):
    name     the words on the board over the door (default "MAPLE SCHOOL")
    clock    the time on the clock over the board (default "8:00")
    bus      False leaves the school bus out
Marks:  gate (in the gateway, facing the school), steps (on the top step, facing the road), yard (on the hopscotch),
        bus_stop (sitting in the shelter), bus_door (at the bus door, facing it), crossing (at the zebra crossing,
        facing the road), sidewalk (on the sidewalk, walking toward +X)
Cams:   wide (from across the road), gate (low at the gate, the school behind), steps (from the yard up at the door),
        bus_stop (the shelter and the bus), bus (along the bus from its nose), crossing, yard
"""
import town as T
from roblox import blob, disc, plastic, rbox
from world2 import bench, bin_, ico, multi, prism, tree2

from places import _outdoor

GEO = ("x", "y")
ROAD_Y = -34                      # the road runs along x


def build(x=2000, y=0):
    W = T.WALK
    _outdoor.backdrop(x, y, seed=21, ring="houses", clear=70, trees=22)
    r = T.empty("school_front", (x, y, 0))
    r["bt_root"] = True
    off = _outdoor.road(x, y + ROAD_Y, 200, along="x")
    _outdoor.zebra(x - 22, y + ROAD_Y, road="x")
    rbox((90, 19, W), (0, -3.5, W / 2), plastic("#D5D7DE", 0.7), r, bv=0.04)                    # the paved yard
    hop = []
    for k, (hx, hy) in enumerate(((0, 0), (0, 2.2), (-1.1, 4.4), (1.1, 4.4), (0, 6.6), (-1.1, 8.8), (1.1, 8.8))):
        hop.append(((2.0, 2.0, 0.03), (-14 + hx, -11 + hy, W + 0.02)))
    multi("yard.hopscotch", hop, plastic("#FFD23A", 0.8), r).visible_shadow = False
    # the fence and gate along the north edge of the sidewalk
    iron, brick = plastic("#2B2D33", 0.35), T.brick()
    bars = [((0.18, 0.18, 3.2), (bx, -12.9, W + 1.6)) for bx in [i * 1.1 - 44 for i in range(81)] if abs(bx) > 5.2]
    bars += [((39, 0.25, 0.25), (sx * 24.6, -12.9, W + 2.9)) for sx in (-1, 1)]
    bars += [((39, 0.25, 0.25), (sx * 24.6, -12.9, W + 0.6)) for sx in (-1, 1)]
    multi("school.fence", bars, iron, r)
    for sx in (-1, 1):
        rbox((1.6, 1.6, 4.6), (sx * 5.6, -12.9, W + 2.3), brick, r, bv=0.06)                   # gate pillars
        rbox((2.0, 2.0, 0.4), (sx * 5.6, -12.9, W + 4.8), plastic("#E9E6DC", 0.5), r, bv=0.06)
    # the school building
    bx0, bd, bh = 72, 24, 22
    rbox((bx0, bd, bh), (0, 6 + bd / 2, bh / 2), brick, r, bv=0.05)
    rbox((bx0 + 1.2, bd + 1.2, 1.4), (0, 6 + bd / 2, bh + 0.7), plastic("#E9E6DC", 0.5), r, bv=0.05)     # parapet
    rbox((bx0 + 0.4, bd + 0.4, 0.8), (0, 6 + bd / 2, 11.2), plastic("#E9E6DC", 0.5), r, bv=0.03)         # band
    wins, frames = [], []
    for z in (6.4, 15.6):
        for wx in [-32, -26, -20, -14, 14, 20, 26, 32]:
            wins.append(((4.0, 0.2, 5.0), (wx, 5.9, z)))
            frames += [((4.6, 0.5, 0.4), (wx, 5.75, z - 2.7)), ((4.6, 0.3, 0.3), (wx, 5.8, z + 2.6)),
                       ((0.25, 0.3, 5.0), (wx, 5.8, z))]
    multi("school.windows", wins, T.WIN, r)
    multi("school.winframes", frames, plastic("#FFFFFF", 0.4), r)
    for k in range(3):                                                                         # the steps
        rbox((14 - k * 1.2, 1.4, W + 0.6 * (k + 1)), (0, 2.9 + k * 1.2, (W + 0.6 * (k + 1)) / 2), plastic("#E9E6DC", 0.6),
             r, bv=0.04)
    top = W + 1.8
    rbox((16, 3.0, top), (0, 5.4, top / 2), plastic("#E9E6DC", 0.6), r, bv=0.04)               # landing (top 2.3)
    rbox((6.4, 0.3, 8.0), (0, 5.95, top + 4.0), plastic("#2A62B0", 0.4), r, bv=0.06)            # double doors
    rbox((0.15, 0.32, 8.0), (0, 5.8, top + 4.0), plastic("#1B3E73", 0.4), r, bv=0)
    for sx in (-0.5, 0.5):
        rbox((0.25, 0.4, 1.2), (sx, 5.7, top + 4.0), plastic("#D8A93A", 0.25), r, bv=0.04)
    cols = plastic("#F4F1EA", 0.45)
    for cx in (-7.5, -2.5 - 2.2, 2.5 + 2.2, 7.5):
        disc(0.7, 8.0, (cx, 4.4, top + 4.0), cols, r, rot=(0, 0, 0), bv=0.1, verts=16)
    rbox((18, 4.6, 0.8), (0, 4.0, top + 8.4), cols, r, bv=0.06)
    prism("school.pediment", 18, 4.6, 3.0, (0, 4.0, top + 8.8), cols, r)
    board = rbox((16, 0.4, 2.6), (0, 5.6, 16.0), plastic("#F7F2E6", 0.5), r, bv=0.08)
    board["bt_name"] = True
    rbox((5.0, 0.5, 2.4), (0, 5.6, 19.6), plastic("#14151A", 0.4), r, bv=0.06)
    board2 = rbox((5.0, 0.1, 2.4), (0, 5.3, 19.6), plastic("#14151A", 0.4), r, bv=0)
    board2["bt_clock"] = True
    for bxx in (-20, -11, 11, 20):                                                             # bushes along the front
        ico(1.8, (bxx, 4.5, W + 1.0), T.mat("#3FA338"), r, scale=(1.6, 0.8, 0.9))
    multi("flag.pole", [((0.35, 0.35, 16), (24, -1, 8))], plastic("#D5D7DE", 0.3), r)
    rbox((4.2, 0.12, 2.6), (26.2, -1, 14.4), plastic("#E0352B", 0.6), r, bv=0)
    import rprops
    for k, (bkx, col) in enumerate(((-24, "#2B62D9"), (-21.5, "#E23B3B"), (-19, "#3BB54A"))):   # bike rack
        rprops.bike(x + bkx, y - 7, W, yaw=0, colour=col)
    multi("bikerack", [((8.4, 0.25, 0.25), (-21.5, -5.6, W + 1.6))] +
          [((0.25, 0.25, 1.6), (sx, -5.6, W + 0.8)) for sx in (-25.6, -17.4)], plastic("#9EA1AA", 0.3), r)
    # the bus stop shelter on the sidewalk, the bus, lamps, bins, trees
    sy = ROAD_Y + off                                                                          # sidewalk centre line
    glass = T.mat("#BFE6FF", emit=0.25, key="shelterglass")
    glass.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.35
    glass.surface_render_method = "BLENDED"
    rbox((8.0, 0.2, 5.0), (31, sy + 3.6, W + 3.2), glass, r, bv=0.03)
    multi("shelter.posts", [((0.3, 0.3, 6.6), (31 + px, sy + 3.6, W + 3.3)) for px in (-4, 4)], plastic("#2F6FE0", 0.3), r)
    rbox((9.0, 4.2, 0.3), (31, sy + 2.0, W + 6.7), plastic("#2F6FE0", 0.3), r, bv=0.06)
    rbox((6.0, 1.6, 0.25), (31, sy + 2.6, W + 1.9), plastic("#9A6A3C", 0.5), r, bv=0.05)        # seat (top W + 2.0)
    multi("shelter.legs", [((0.25, 1.2, 1.8), (31 + px, sy + 2.6, W + 0.9)) for px in (-2.6, 2.6)], plastic("#2B2D33", 0.4), r)
    multi("busstop.pole", [((0.25, 0.25, 8.0), (25.0, sy - 2.5, W + 4.0))], plastic("#9EA1AA", 0.3), r)
    rbox((2.4, 0.2, 1.4), (25.0, sy - 2.5, W + 7.6), plastic("#2F6FE0", 0.4), r, bv=0.06)
    T.text("BUS", 0.8, (25.0, sy - 2.65, W + 7.6), T.mat("#FFFFFF", emit=0.8, key="busstopink"), r, extrude=0.0)
    T.text("BUS", 0.8, (25.0, sy - 2.35, W + 7.6), T.mat("#FFFFFF", emit=0.8, key="busstopink"), r, rot=(90, 0, 180),
           extrude=0.0)
    for lx in (-36, -6, 16, 46):                                                               # lamps at the kerb
        _outdoor.lamp(r, lx, ROAD_Y + 13.2, arm=(0, -1))
    bin_(x + 20.5, y + sy + 2.5)
    for k, (tx, ty) in enumerate(((-46, -2), (46, -2), (-40, 36), (40, 36))):
        tree2(x + tx, y + ty, 1.2, ("round", "blossom")[k % 2], seed=900 + k)
    from props import car
    car(x - 36, y + ROAD_Y - 6, col="#E8E8EC", yaw=90)
    marks = {"gate": (x, y - 11.5, W, 180), "steps": (x, y + 5.0, top, 0), "yard": (x - 14, y - 7.0, W, 180),
             "bus_stop": (x + 31, y + sy + 2.4, W, 0), "bus_door": (x + 36.6, y + sy - 3.0, W, 0),
             "crossing": (x - 22, y + sy - 1.0, W, 0), "sidewalk": (x + 6, y + sy, W, 90)}
    cams = {"wide": ((x + 8, y - 72, 15), (x, y + 8, 9), 50),
            "gate": ((x + 3, y - 26, 4.6), (x, y + 8, 8.5), 50),
            "steps": ((x + 3, y - 15, 5.6), (x, y + 5, 5.4), 46),
            "bus_stop": ((x + 18.5, y + sy - 2.5, 5.4), (x + 31, y + sy + 2.0, 3.8), 48),
            "bus": ((x + 54, y + ROAD_Y - 5, 7.0), (x + 28, y + ROAD_Y + 9, 4.0), 50),
            "crossing": ((x - 22, y + ROAD_Y - 9, 5.2), (x - 22, y + sy, 4.0), 46),
            "yard": ((x - 33, y - 19, 9.0), (x - 10, y + 2, 4.0), 50)}
    return {"marks": marks, "cams": cams, "bus_at": (26, ROAD_Y + 6)}


def dress(p, name="MAPLE SCHOOL", clock="8:00", bus=True):
    b = p.one("bt_name")
    bx, by, bz = b.location
    T.text(name, 1.5, (bx, by - 0.25, bz), T.mat("#1B3E73", key="schoolink"), p.root, extrude=0.04, max_w=14.5)
    c = p.one("bt_clock")
    cx, cy, cz = c.location
    T.text(clock, 1.5, (cx, cy - 0.1, cz), T.mat("#FF3B30", emit=4.0, key="clock"), p.root, extrude=0.03, max_w=4.4)
    if bus:
        import rprops
        bx_, by_ = p.info["bus_at"]
        o = rprops.bus(p.root.location.x + bx_, p.root.location.y + by_, yaw=90)
        p["bus"] = o
