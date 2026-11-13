"""A family home, open plan: the kitchen on the left (counter with sink, stove and fridge, wall cupboards, a window over
the sink, a dining table with four chairs and a hanging lamp) and the living room on the right (a sofa facing a TV,
coffee table, rug, floor lamp, bookshelf, pictures). Front door in the middle of the front wall. Parked at (0, -960).

Episode arguments (never saved):
    tv       a picture name to show on the TV (EPISODE/pictures.json or the kit's, e.g. "notice"); None = a blue screen
Marks:  sofa_1 .. sofa_3 (sitting, facing the TV), table_1 .. table_4 (sitting at the dining table), stove, sink,
        fridge (at each, facing it), tv (in front of the TV, facing the room), door (just inside the front door),
        window (at the kitchen-side window on the left wall, looking out)
Cams:   wide (the whole home from the front corner), tv_pov (from the TV at the sofa), sofa_back (behind the sofa at the
        TV), kitchen (across the table to the counter), table (low at the table), door (from the front door)
"""
import town as T
from roblox import blob, disc, plastic, rbox
from world2 import multi

from places import _room

GEO = ("x", "y")
W, D, H = 44, 30, 12


def _chair(r, cx, cy, yaw, wood):
    """A dining chair, seat top at z 2.0; the sitter faces yaw (0 = -Y)."""
    e = T.empty("chair", (cx, cy, 0), r, yaw=yaw)
    rbox((1.9, 1.8, 0.25), (0, 0, 1.88), wood, e, bv=0.06)
    multi("chair.legs", [((0.2, 0.2, 1.8), (sx, sy, 0.9)) for sx in (-0.75, 0.75) for sy in (-0.7, 0.7)], wood, e)
    rbox((1.9, 0.22, 2.2), (0, 0.85, 3.1), wood, e, bv=0.06)                                  # back (behind the sitter)


def build(x=0, y=-960):
    rm = _room.room("home", x, y, W, D, H, floor="#B07A4A", low="#E8D2B0", high="#9CC9C2", ceiling="#F1ECE2")
    r = rm["root"]
    # ---------------------------------------------------------------- kitchen (x < 0)
    cab, top, handle = plastic("#F4F1EA", 0.45), plastic("#3A3F4A", 0.3), plastic("#A9ACB5", 0.25)
    ny = D / 2 - 0.3 - 1.4
    rbox((13.6, 2.8, 3.0), (-10.8, ny, 1.5), cab, r, bv=0.06)                                # base cupboards
    rbox((14.2, 3.2, 0.3), (-10.8, ny - 0.1, 3.15), top, r, bv=0.05)
    rbox((13.6, 2.4, 0.5), (-10.8, ny + 0.2, 0.25), plastic("#2A2C33", 0.4), r, bv=0.02)      # kick plate
    fronts = []
    for i in range(6):
        cx = -16.4 + i * 2.25
        fronts += [((2.0, 0.08, 2.2), (cx, ny - 1.42, 1.65))]
    multi("home.fronts", fronts, plastic("#E6E1D6", 0.45), r)
    multi("home.handles", [((0.9, 0.18, 0.18), (-16.4 + i * 2.25, ny - 1.52, 2.45)) for i in range(6)], handle, r)
    for ux in (-15.5, -6.2):                                                                  # wall cupboards
        rbox((5.0, 1.8, 3.2), (ux, D / 2 - 1.2, 9.0), cab, r, bv=0.06)
        multi("home.uhandles", [((0.18, 0.18, 0.9), (ux + dx, D / 2 - 2.2, 8.2)) for dx in (-0.4, 0.4)], handle, r)
    _room.window(rm, "N", -11, z=8.0, sw=5.0, sh=4.4)                                         # over the sink
    rbox((3.2, 2.0, 0.4), (-11, ny - 0.1, 3.2), plastic("#7A808C", 0.2), r, bv=0.05)          # sink
    multi("home.tap", [((0.25, 0.25, 1.4), (-11, ny + 0.9, 3.9)), ((0.25, 1.1, 0.25), (-11, ny + 0.45, 4.55))],
          plastic("#C9CCD4", 0.15), r)
    burner = plastic("#1B1D24", 0.4)
    for bx_ in (-6.9, -5.3):                                                                  # the stove top
        for by_ in (ny - 0.6, ny + 0.6):
            disc(0.55, 0.08, (bx_, by_, 3.34), burner, r, rot=(0, 0, 0), bv=0, verts=20)
    rbox((3.6, 0.1, 2.3), (-6.1, ny - 1.45, 1.6), plastic("#2A2C33", 0.3), r, bv=0.04)        # oven door
    rbox((2.0, 0.06, 0.9), (-6.1, ny - 1.52, 1.8), T.mat("#F28A1E", emit=0.6, key=("glow", "#F28A1E", 0.6)), r, bv=0)
    rbox((1.6, 1.6, 1.0), (-6.9, ny - 0.6, 3.9), plastic("#E23B3B", 0.3), r, bv=0.25)         # a pot
    # the fridge (left end of the counter)
    fr = plastic("#F7F7F9", 0.25)
    rbox((3.6, 3.0, 9.0), (-19.6, D / 2 - 1.9, 4.5), fr, r, bv=0.18)
    multi("home.fhandles", [((0.25, 0.3, 2.0), (-18.2, D / 2 - 3.5, 6.8)), ((0.25, 0.3, 2.6), (-18.2, D / 2 - 3.5, 3.2))],
          handle, r)
    rbox((3.5, 0.06, 0.1), (-19.6, D / 2 - 3.42, 5.4), plastic("#C9CCD4", 0.3), r, bv=0)
    for k, col in enumerate(("#E23B3B", "#FFC533", "#3BB54A")):                               # magnets
        rbox((0.4, 0.1, 0.4), (-20.6 + k * 0.7, D / 2 - 3.45, 7.2 - (k % 2) * 0.5), plastic(col, 0.4), r, bv=0.05)
    # the dining table, four chairs, a fruit bowl, a hanging lamp
    oak = plastic("#C98A4A", 0.45)
    rbox((8.0, 5.0, 0.3), (-11, -3, 3.2), oak, r, bv=0.08)
    multi("home.tlegs", [((0.35, 0.35, 3.1), (-11 + sx, -3 + sy, 1.55)) for sx in (-3.5, 3.5) for sy in (-2.0, 2.0)], oak, r)
    chairs = []
    for cx in (-13, -9):
        _chair(r, cx, -7.0, 180, plastic("#8A5A3C", 0.5))
        _chair(r, cx, 1.0, 0, plastic("#8A5A3C", 0.5))
        chairs += [(cx, -7.0, 180), (cx, 1.0, 0)]
    disc(1.2, 0.5, (-11, -3, 3.6), plastic("#FFFFFF", 0.3), r, rot=(0, 0, 0), bv=0.15, verts=24)
    for k, (dx, dy, col) in enumerate(((-0.4, 0, "#E8202A"), (0.4, 0.2, "#FFC533"), (0, -0.4, "#3BB54A"))):
        blob((0.4, 0.4, 0.4), (-11 + dx, -3 + dy, 4.1), plastic(col, 0.35), r)
    rbox((0.08, 0.08, 3.6), (-11, -3, H - 1.8), plastic("#1B1D24", 0.4), r, bv=0)
    blob((1.4, 1.4, 0.8), (-11, -3, H - 3.8), plastic("#2F5440", 0.4), r)
    blob((0.5, 0.5, 0.3), (-11, -3, H - 4.5), T.mat("#FFE2A8", emit=2.0, key=("glow", "#FFE2A8", 2.0)), r)
    _room.window(rm, "W", -3, z=7.0, sw=6.0, sh=5.6)
    # ---------------------------------------------------------------- living room (x > 0)
    rbox((16, 12, 0.06), (12, -1.5, 0.03), plastic("#D96B5A", 0.8), r, bv=0)                 # rug
    multi("home.rugline", [((15, 0.3, 0.02), (12, -1.5 + k * 4, 0.07)) for k in (-1, 0, 1)], plastic("#F2C14E", 0.8), r)
    sofa, cush = plastic("#3F5873", 0.6), plastic("#5374A0", 0.6)
    rbox((13, 3.8, 1.6), (12, -5.4, 0.8), sofa, r, bv=0.2)                                   # base
    for k in range(3):
        rbox((3.9, 3.2, 0.5), (8 + k * 4, -5.0, 1.82), cush, r, bv=0.22)                      # seat cushions (top 2.07)
        rbox((3.9, 1.0, 2.6), (8 + k * 4, -6.8, 3.2), cush, r, bv=0.25)                       # back cushions
    rbox((13, 1.2, 3.8), (12, -7.6, 1.9), sofa, r, bv=0.2)                                   # back
    for sx in (5.2, 18.8):
        rbox((1.4, 3.8, 2.8), (sx, -5.4, 1.4), sofa, r, bv=0.25)                              # arms
    rbox((1.5, 1.5, 0.5), (6.6, -5.6, 2.4), plastic("#F2C14E", 0.6), r, bv=0.3, rot=(0, 0, 20))      # a throw cushion
    ct = plastic("#7A4A2C", 0.45)
    rbox((6.4, 3.0, 0.3), (12, 0.6, 1.8), ct, r, bv=0.06)                                    # coffee table
    multi("home.ctlegs", [((0.3, 0.3, 1.7), (12 + sx, 0.6 + sy, 0.85)) for sx in (-2.8, 2.8) for sy in (-1.2, 1.2)], ct, r)
    rbox((0.6, 1.4, 0.2), (13.4, 0.4, 2.05), plastic("#1B1D24", 0.4), r, bv=0.06)            # remote
    rbox((0.6, 0.6, 0.7), (10.6, 0.8, 2.3), plastic("#FFFFFF", 0.3), r, bv=0.1)              # mug
    # the TV on its stand against the back wall
    rbox((11, 2.4, 2.0), (12, D / 2 - 1.6, 1.0), plastic("#2A2C33", 0.4), r, bv=0.08)       # stand
    rbox((10.2, 0.5, 5.8), (12, D / 2 - 1.2, 6.2), plastic("#16171C", 0.3), r, bv=0.12)     # TV frame
    scr = rbox((9.4, 0.06, 5.1), (12, D / 2 - 1.48, 6.2), T.mat("#2B4C9A", emit=0.9, key="tvscreen"), r, bv=0)
    scr["bt_tv"] = True
    rbox((1.2, 1.6, 0.4), (16, D / 2 - 1.6, 2.2), plastic("#E9E2D6", 0.5), r, bv=0.1)       # a games console
    # floor lamp, plant, bookshelf, pictures
    rbox((0.25, 0.25, 7.4), (20.2, -10.6, 3.7), plastic("#1B1D24", 0.4), r, bv=0.03)
    blob((1.1, 1.1, 1.0), (20.2, -10.6, 7.8), T.mat("#FFE9C2", emit=1.6, key=("glow", "#FFE9C2", 1.6)), r)
    rbox((1.6, 1.6, 1.5), (2.4, D / 2 - 2.0, 0.75), plastic("#B5653A", 0.6), r, bv=0.15)
    for k, (dx, dz, s_) in enumerate(((0, 2.6, 1.3), (0.6, 3.6, 1.0), (-0.5, 3.4, 0.9))):
        blob((s_, s_, s_ * 1.2), (2.4 + dx, D / 2 - 2.0, dz), plastic(("#3FA338", "#4DB542", "#368E31")[k], 0.6), r)
    s, c = _room.on_wall(rm, "E", 6, 4.0, 7.0, 8.0, 2.0)
    rbox(s, c, plastic("#8A5A3C", 0.5), r, bv=0.06)                                           # bookshelf
    books = {"#E23B3B": [], "#2F6FE0": [], "#FFC533": [], "#3BB54A": [], "#8A4FB5": []}
    cols = list(books)
    for lv in range(3):
        for i in range(8):
            bz = 1.3 + lv * 2.5
            books[cols[(i * 2 + lv) % 5]].append(((1.4, 0.6, 1.6 + 0.2 * (i % 3)), (c[0] - 0.4, 3.0 + i * 0.75, bz)))
    _room.colour_boxes("home.books", books, r, 0.6)
    for k, (py, col) in enumerate(((-4.0, "#F2C14E"), (-9.0, "#E88BA8"))):
        s, c = _room.on_wall(rm, "E", py, 8.0, 3.4, 2.6, 0.2)
        rbox(s, c, plastic("#2A2C33", 0.5), r, bv=0.05)
        s, c = _room.on_wall(rm, "E", py, 8.0, 2.8, 2.0, 0.24)
        rbox(s, c, plastic(col, 0.6), r, bv=0.02)
    dx_, dy_ = _room.door(rm, "S", 2.0, colour="#C8322E")
    _room.ceiling_lights(rm, [(-11, 8), (12, -2), (12, 9)], panel=(3.0, 3.0))
    _room.finish(rm)
    marks = {}
    for k in range(3):
        marks[f"sofa_{k + 1}"] = (x + 8 + k * 4, y - 4.6, 0.0, 180)
    for k, (cx, cy, yaw) in enumerate(chairs):
        marks[f"table_{k + 1}"] = (x + cx, y + cy, 0.0, yaw)
    marks.update({"stove": (x - 6.1, y + ny - 3.4, 0.0, 180), "sink": (x - 11, y + ny - 3.4, 0.0, 180),
                  "fridge": (x - 19.4, y + D / 2 - 6.4, 0.0, 180), "tv": (x + 7.0, y + 10.0, 0.0, 0),
                  "door": (x + dx_, y + dy_, 0.0, 180), "window": (x - 19.8, y - 3, 0.0, -90)})
    cams = {"wide": ((x + 20.5, y - 13.5, 10.0), (x - 5, y + 5, 3.2), 58),
            "tv_pov": ((x + 12, y + 12.2, 6.2), (x + 12, y - 5, 3.4), 46),
            "sofa_back": ((x + 13.5, y - 13.0, 7.4), (x + 12, y + 13, 5.6), 48),
            "kitchen": ((x - 2.0, y - 9.0, 7.0), (x - 12, y + 11, 4.0), 50),
            "table": ((x - 1.5, y - 13.5, 7.8), (x - 11, y - 2.0, 3.4), 46),
            "door": ((x + 2.0, y - 12.6, 7.6), (x - 6, y + 6, 3.4), 52)}
    return {"marks": marks, "cams": cams}


def dress(p, tv=None):
    import rprops
    _room.window_hook(p)
    if tv:
        s = p.one("bt_tv")
        sx, sy, sz = s.location
        q = rprops.picture_quad(tv, 9.4, 5.1, sy - 0.05, rprops.lit_picture(tv, 1.0), p.root, z=sz)
        q.location.x = sx
