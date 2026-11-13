"""Downtown: a wide avenue (along y) between rows of tall buildings (their glass is blue by day and lit at dusk and
night), shops on the ground floor (signs and striped awnings), a big screen on a building, a zebra crossing with
traffic lights, street lamps, cars and a taxi, benches, bins and hydrants, and a skyline of towers all round. Parked on
its own plot at (3000, 0).

Episode arguments (never saved):
    signs    shop names on the ground floors: a dict {index: "NAME"} replacing the default names (index 0-13: left side
             from -Y, then right side from -Y), e.g. {2: "TAG CAFE"}
    screen   a picture name for the big screen (EPISODE/pictures.json or the kit's); None = a plain blue glow
Helpers: p["lights"]("red" | "yellow" | "green") sets both traffic lights for this frame (they rest on red).
Marks:  crossing_L, crossing_R (waiting at the zebra crossing, facing the road), sidewalk_L, sidewalk_R (walking
        toward +Y), screen_watch (across from the big screen, looking at it), cafe_door (left side), bank_door (right
        side), taxi (at the taxi's kerb-side door)
Cams:   avenue (down the avenue), skyline (low on the right sidewalk, looking up at the towers opposite), crossing (the zebra and both kerbs),
        screen (up at the big screen), corner_wide (high over the street), sidewalk (along the left sidewalk),
        cafe (at the cafe front)
"""
import random

import town as T
from roblox import plastic, rbox
from world2 import bench, bin_, hydrant, multi

from places import _outdoor

GEO = ("x", "y")
ROAD_W, WALK_W = 28, 10
FRONT = ROAD_W / 2 + WALK_W                     # building fronts at x = +/-24
BLOCK_Y = (-78, -50, -22, 6, 34, 62, 90)
NAMES = ("BANK", "BOOKS", "CAFE", "PIZZA", "SHOES", "HOTEL", "TOYS",
         "BANK", "DINER", "PHONES", "FLOWERS", "GYM", "ARCADE", "BAKERY")
WALLS = ("#8FA3B8", "#C98A6A", "#B8A48F", "#9BB3A0", "#A89BB8", "#D9C7A0", "#7F8C99")
AWN = ("#E94B5B", "#2F6FE0", "#3BB54A", "#F28A1E", "#8A4FB5")


def build(x=3000, y=0):
    rng = random.Random(31)
    W = T.WALK
    _outdoor.backdrop(x, y, seed=31, ring="towers", ring_r=(125, 160), clear=200, trees=0)
    r = T.empty("downtown", (x, y, 0))
    r["bt_root"] = True
    _outdoor.road(x, y, 220, width=ROAD_W, along="y", walk=WALK_W)
    _outdoor.zebra(x, y + 10, road="y", road_w=ROAD_W, n=9)
    k = 0
    signs = []
    for side in (-1, 1):
        for i, by in enumerate(BLOCK_Y):
            h = rng.choice((34, 42, 52, 64, 78, 92))
            col = WALLS[(i * 3 + (side > 0)) % len(WALLS)]
            bx = side * (FRONT + 15)
            rbox((30, 26, h), (bx, by, h / 2), plastic(col, 0.6), r, bv=0.1)
            rbox((31, 27, 1.2), (bx, by, h + 0.6), plastic("#E9E6DC", 0.5), r, bv=0.05)          # cornice
            fx = side * (FRONT - 0.05)
            wins = [((0.2, 3.0, 3.8), (fx, by + wy, z)) for z in range(12, int(h) - 3, 6) for wy in (-9, -3, 3, 9)]
            multi("tower.windows", wins, _outdoor.tower_window(), r)
            frames = [((0.4, 25.6, 0.4), (side * (FRONT - 0.1), by, z - 2.3)) for z in range(12, int(h) - 3, 6)]
            multi("tower.ledges", frames, plastic("#E9E6DC", 0.5), r)
            glass = T.mat("#BFE6FF", emit=0.35, key=("glow", "#BFE6FF", 0.35))
            rbox((0.2, 22, 5.0), (side * (FRONT - 0.05), by, W + 2.9), glass, r, bv=0)               # shop window
            rbox((0.3, 4.0, 6.8), (side * (FRONT - 0.15), by + 9.5, W + 3.4), plastic("#2A2C38", 0.4), r, bv=0.05)   # door
            board = rbox((0.4, 18, 2.2), (side * (FRONT - 0.2), by - 1, W + 7.6), plastic("#1B1F3A", 0.5), r, bv=0.06)
            board["bt_sign"] = k
            signs.append(board)
            stripes = {AWN[k % len(AWN)]: [], "#FFFFFF": []}
            for j in range(8):
                stripes[AWN[k % len(AWN)] if j % 2 else "#FFFFFF"].append(
                    ((3.0, 22 / 8, 0.25), (side * (FRONT - 1.6), by - 11 + 22 / 16 + j * 22 / 8, W + 6.0)))
            for c_, parts in stripes.items():
                o = multi("awning", parts, plastic(c_, 0.5), r)
                o.rotation_euler = (0, 0, 0)
            if rng.random() < 0.6:                                                                  # rooftop boxes
                rbox((5, 5, 3), (bx + rng.uniform(-8, 8), by + rng.uniform(-6, 6), h + 2.7), plastic("#7A808C", 0.5), r, bv=0.1)
            k += 1
    # the big screen on the left building opposite the crossing
    rbox((0.8, 18, 11), (-(FRONT - 0.4), 6, 28), plastic("#16171C", 0.3), r, bv=0.12)
    scr = rbox((0.1, 16.6, 9.6), (-(FRONT - 0.85), 6, 28), T.mat("#2B4C9A", emit=1.2, key="bigscreen"), r, bv=0)
    scr["bt_screen"] = True
    # traffic lights at the crossing
    for side in (-1, 1):
        px, py = side * (ROAD_W / 2 + 1.2), 10 - side * 4.5
        multi("tl.pole", [((0.4, 0.4, 9.0), (px, py, W + 4.5))], plastic("#2B2D33", 0.35), r)
        rbox((1.5, 1.5, 4.2), (px, py, W + 9.6), plastic("#2B2D33", 0.35), r, bv=0.1)
        for j, colname in enumerate(("red", "yellow", "green")):
            m = T.MATS.get(("trafficlight", colname))
            if m is None:                                   # dark glass that glows in its colour when switched on
                m = T.mat("#1E2026", emit=0.2, key=("trafficlight", colname))
                m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = T.lin(
                    {"red": "#FF3B30", "yellow": "#FFC533", "green": "#3BE37E"}[colname])
            o = rbox((0.4, 0.95, 0.95), (px, py, W + 10.9 - j * 1.3), m, r, bv=0.12)
            o.location.x -= side * 0.62
            o.visible_shadow = False
    # lamps, benches, bins, hydrants, cars, a taxi
    for side in (-1, 1):
        for ly in (-64, -36, 20, 48, 76):
            _outdoor.lamp(r, side * (ROAD_W / 2 + 1.4), ly, arm=(-side, 0))
    bench(x - 21.5, y - 36 + 6, yaw=90)
    bench(x + 21.5, y + 48 - 6, yaw=-90)
    for bx_, by_ in ((-21.2, -16), (21.2, 26), (-21.2, 62)):
        bin_(x + bx_, y + by_)
    for hx, hy in ((-15.6, -30), (15.6, 40)):
        hydrant(x + hx, y + hy)
    from props import car
    for cx_, cy_, col, yaw in ((-7, -40, "#2B62D9", 180), (7, -58, "#E23B3B", 0), (-7, 46, "#3BB573", 180),
                               (7, 70, "#E8E8EC", 0)):
        car(x + cx_, y + cy_, col=col, yaw=yaw)
    car(x + 10.5, y - 18, col="#FFC533", sticker="TAXI", yaw=0)
    marks = {"crossing_L": (x - 16.5, y + 10, W, 90), "crossing_R": (x + 16.5, y + 10, W, -90),
             "sidewalk_L": (x - 19, y - 24, W, 180), "sidewalk_R": (x + 19, y - 24, W, 180),
             "screen_watch": (x + 18.5, y + 2, W, -90), "cafe_door": (x - 21.5, y - 22 + 9.5, W, -90),
             "bank_door": (x + 21.5, y - 78 + 9.5, W, 90), "taxi": (x + 15.5, y - 18, W, -90)}
    cams = {"avenue": ((x + 2, y - 74, 8.5), (x, y + 40, 16), 46),
            "skyline": ((x + 18, y - 32, 2.8), (x - 26, y + 2, 36), 60),
            "crossing": ((x + 9, y - 10, 6.5), (x - 10, y + 12, 3.6), 50),
            "screen": ((x + 17, y - 10, 4.6), (x - 24, y + 6, 26), 50),
            "corner_wide": ((x + 6, y - 102, 42), (x - 2, y + 10, 6), 50),
            "sidewalk": ((x - 19.5, y - 44, 5.6), (x - 19, y - 4, 4.6), 46),
            "cafe": ((x - 6, y - 2, 7.6), (x - 24, y - 19, 7.0), 48)}
    return {"marks": marks, "cams": cams}


def dress(p, signs=None, screen=None):
    import anim
    _outdoor.tower_hook()
    names = list(NAMES)
    for i, n in (signs or {}).items():
        names[int(i)] = n
    for b in p.tagged("bt_sign"):
        bx, by, bz = b.location
        side = 1 if bx > 0 else -1
        T.text(names[b["bt_sign"]], 1.5, (bx - side * 0.25, by, bz), T.sign_mat(), p.root,
               rot=(90, 0, 90 if side < 0 else -90), extrude=0.05, max_w=16)
    if screen:
        import rprops
        s = p.one("bt_screen")
        sx, sy, sz = s.location
        q = rprops.picture_quad(screen, 16.6, 9.6, 0.0, rprops.lit_picture(screen, 1.2), p.root, z=0.0)
        q.location = (sx + 0.06, sy, sz)
        q.rotation_euler = (0, 0, 1.5707963)
    lights = {c: T.MATS[("trafficlight", c)] for c in ("red", "yellow", "green")}

    def set_lights(state="red"):
        for c, m in lights.items():
            T.emission(m, 6.0 if c == state else 0.08)
    anim.before_each_frame(lambda Tm: set_lights("red"))
    set_lights("red")
    p["lights"] = set_lights
