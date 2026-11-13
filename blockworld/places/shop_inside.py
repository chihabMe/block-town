"""Inside a corner shop: shelves of goods along the back wall, a double-sided shelf in the middle, a counter with a
till, a card reader and a candy jar on the left, glowing drink fridges on the right, a shop window and a glass door at
the front with an OPEN sign, price strips on every shelf, ceiling lights. Parked at (0, -860). The door is at -Y.

Episode arguments (never saved):
    sign     the shop's name on the board behind the counter (e.g. "PRICE SHOP"; max about 12 letters)
    special  words on the yellow offer card in the window (e.g. "2 FOR 1"), None for no card
Marks:  keeper (behind the counter, facing the customer), customer (at the counter, facing the keeper),
        aisle (between the shelves, facing the back), fridge (at the fridges, facing them), door (just inside the door),
        window (inside the shop window, looking out)
Cams:   entrance (from the door: the whole shop), over_counter (over the keeper's shoulder at the customer),
        customer_pov (over the customer's shoulder: the keeper, till and sign),
        fridge_side (from the fridges across the shop), wide (high in a front corner); aisle looks along the aisle
        from the fridge end
"""
import random

import town as T
from roblox import blob, plastic, rbox
from world2 import multi

from places import _room

GEO = ("x", "y")
W, D, H = 36, 28, 12
GOODS = ("#E23B3B", "#2F6FE0", "#FFC533", "#3BB54A", "#FF7FB0", "#F28A1E", "#8A4FB5", "#FFFFFF")


def _shelf(r, x0, y0, length, depth, levels, goods, rng, strips, facing=-1, wood="#E9E2D6"):
    """A shelf unit along x (from x0, centred at y0) with goods on each level; facing -1 = goods face -Y, +1 = +Y,
    0 = both sides (a middle shelf)."""
    m = plastic(wood, 0.5)
    rbox((length, depth, 0.3), (x0 + length / 2, y0, 0.15), m, r, bv=0.04)
    for side in (-1, 1):
        rbox((0.3, depth, levels * 2.0 + 0.6), (x0 + (0.15 if side < 0 else length - 0.15), y0, (levels * 2.0 + 0.6) / 2), m, r, bv=0.04)
    if facing != 0:
        rbox((length, 0.2, levels * 2.0 + 0.6), (x0 + length / 2, y0 - facing * (depth / 2 - 0.1), (levels * 2.0 + 0.6) / 2), m, r, bv=0.02)
    for lv in range(levels + 1):
        z = 0.6 + lv * 2.0
        rbox((length - 0.4, depth, 0.16), (x0 + length / 2, y0, z), m, r, bv=0.03)
        if lv == levels:
            break
        sides = (-1, 1) if facing == 0 else (facing,)
        for fs in sides:
            front = y0 + fs * (depth / 2 - 0.05)
            strips.append(((length - 0.6, 0.12, 0.32), (x0 + length / 2, front, z - 0.02)))     # price strip
            gx = x0 + 0.7
            while gx < x0 + length - 0.7:
                col = rng.choice(GOODS)
                kind = rng.random()
                if kind < 0.5:                                  # boxes
                    gw, gh = rng.uniform(0.8, 1.2), rng.uniform(1.0, 1.5)
                    goods[col].append(((gw, 0.7, gh), (gx + gw / 2, front - fs * 0.6, z + 0.08 + gh / 2)))
                elif kind < 0.8:                                # cans in a row of three
                    gw, gh = 0.55, 0.8
                    for k in range(3):
                        goods[col].append(((gw, 0.55, gh), (gx + 0.3 + k * 0.62, front - fs * 0.55, z + 0.08 + gh / 2)))
                    gw = 1.9
                else:                                           # bottles
                    gw, gh = 0.45, 1.5
                    for k in range(2):
                        goods[col].append(((gw, 0.45, gh), (gx + 0.25 + k * 0.6, front - fs * 0.5, z + 0.08 + gh / 2)))
                        goods["#FFFFFF"].append(((0.25, 0.25, 0.3), (gx + 0.25 + k * 0.6, front - fs * 0.5, z + 0.08 + gh + 0.15)))
                    gw = 1.3
                gx += gw + 0.15


def build(x=0, y=-860):
    rng = random.Random(5)
    rm = _room.room("shop_inside", x, y, W, D, H, floor="#E9E6DC", low="#D9434F", high="#FFD98F", ceiling="#E8E2D2",
                    planks=False)
    r = rm["root"]
    tiles = [((1.95, 1.95, 0.02), (-W / 2 + 1 + 2 * i, -D / 2 + 1 + 2 * j, 0.01)) for i in range(int(W / 2))
             for j in range(int(D / 2)) if (i + j) % 2 == 0]
    multi("shop_inside.tiles", tiles, plastic("#3A3F4A", 0.45), r)                      # a checked floor
    goods = {c: [] for c in GOODS}
    strips = []
    _shelf(r, -8, D / 2 - 1.6, 24, 2.6, 4, goods, rng, strips, facing=-1)             # back wall
    _shelf(r, -4, 0.5, 14, 2.6, 3, goods, rng, strips, facing=0)                       # middle, both sides
    _room.colour_boxes("shop_inside.goods", goods, r)
    multi("shop_inside.strips", strips, plastic("#FFD23A", 0.5), r)
    # the counter on the left, the till, the card reader, a candy jar, a stool behind it
    wood, top = plastic("#8A5A3C", 0.5), plastic("#C98A4A", 0.35)
    rbox((3.2, 12, 2.6), (-13.2, -2, 1.3), wood, r, bv=0.08)            # waist high
    rbox((3.8, 12.6, 0.3), (-13.2, -2, 2.75), top, r, bv=0.06)
    rbox((3.3, 12.1, 0.5), (-12.9, -2, 0.25), plastic("#2A2C33", 0.4), r, bv=0.04)    # kick plate
    till = T.empty("till", (-13.4, 0.6, 2.9), r, yaw=90)  # its screen faces the customer
    rbox((1.8, 1.6, 0.9), (0, 0, 0.45), plastic("#2A2C33", 0.35), till, bv=0.1)
    rbox((1.4, 0.2, 1.0), (0, 0.4, 1.4), plastic("#2A2C33", 0.35), till, bv=0.05, rot=(-20, 0, 0))
    rbox((1.2, 0.05, 0.8), (0.0, 0.29, 1.42), T.mat("#3BE37E", emit=1.2, key=("glow", "#3BE37E", 1.2)), till, bv=0,
         rot=(-20, 0, 0))
    rbox((0.6, 0.9, 0.15), (-13.0, -4.2, 2.98), plastic("#1B1D24", 0.3), r, bv=0.05)    # card reader
    rbox((0.45, 0.04, 0.3), (-13.0, -4.66, 3.15), T.mat("#2FD4FF", emit=1.0, key=("glow", "#2FD4FF", 1.0)), r, bv=0)
    import rprops
    rprops.candy_jar(-12.9, -6.6, 2.9, parent=r)
    rbox((1.6, 1.6, 0.3), (-16.4, 2.6, 2.0), plastic("#E23B3B", 0.4), r, bv=0.1)      # stool
    rbox((0.3, 0.3, 1.9), (-16.4, 2.6, 0.95), plastic("#5A606B", 0.35), r, bv=0.03)
    # the sign board behind the counter
    s, c = _room.on_wall(rm, "W", -2, 9.4, 11, 2.6, 0.3)
    board = rbox(s, c, plastic("#1B1F3A", 0.5), r, bv=0.08)
    board["bt_sign"] = True
    # drink fridges on the right wall: glowing glass, bottles behind
    fr = plastic("#D5D7DE", 0.3)
    glass = T.mat("#CDEFFF", emit=0.5, key="fridgeglass")
    glass.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.3
    glass.surface_render_method = "BLENDED"
    for k, fy in enumerate((-5.5, 0.5, 6.5)):
        s, c = _room.on_wall(rm, "E", fy, 4.6, 5.6, 9.2, 2.6)
        rbox(s, c, fr, r, bv=0.1)
        s2, c2 = _room.on_wall(rm, "E", fy, 4.8, 4.8, 7.8, 0.06, inset=2.62)
        rbox(s2, c2, glass, r, bv=0).visible_shadow = False
        s3, c3 = _room.on_wall(rm, "E", fy + 2.0, 4.8, 0.25, 2.2, 0.3, inset=2.62)
        rbox(s3, c3, plastic("#5A606B", 0.3), r, bv=0.04)                                  # handle
        drinks = {col: [] for col in ("#E23B3B", "#3BB54A", "#F28A1E", "#2F6FE0")}
        for lv in range(4):
            for i in range(6):
                col = list(drinks)[(i + lv + k) % 4]
                drinks[col].append(((0.5, 0.5, 1.3), (c[0] - 0.2, fy - 2.0 + i * 0.8, 1.6 + lv * 1.9)))
        _room.colour_boxes(f"shop_inside.drinks{k}", drinks, r, 0.3)
    # the front: a big shop window, a glass door, a doormat, a basket stack
    win = _room.window(rm, "S", -9, z=6.0, sw=13, sh=7.0)
    s, c = _room.on_wall(rm, "S", 8, 4.2, 4.6, 8.4, 0.12)
    rbox(s, c, T.mat("#BFE6FF", emit=0.5, key=("glow", "#BFE6FF", 0.5)), r, bv=0).visible_shadow = False
    for (ww, hh, oo, zz) in ((5.4, 0.4, 8, 8.6), (0.4, 8.4, 5.5, 4.2), (0.4, 8.4, 10.5, 4.2), (0.25, 1.5, 9.6, 4.2)):
        rm["frames"].append(_room.on_wall(rm, "S", oo, zz, ww, hh, 0.3))
    s, c = _room.on_wall(rm, "S", 8, 6.6, 2.6, 0.9, 0.14, inset=0.06)
    rbox(s, c, T.mat("#E23B3B", emit=1.4, key=("glow", "#E23B3B", 1.4)), r, bv=0.05)
    T.text("OPEN", 0.62, (c[0], c[1] + 0.09, c[2]), T.mat("#FFFFFF", emit=2.0, key="openink"), r, rot=(90, 0, 180),
           extrude=0.0)
    rbox((4.2, 2.6, 0.06), (8, -D / 2 + 1.9, 0.04), plastic("#5A3A2A", 0.9), r, bv=0)    # doormat
    for k in range(3):                                                                    # baskets
        rbox((1.8, 1.3, 0.9), (13.5, -D / 2 + 2.0, 0.45 + k * 0.5), plastic("#E23B3B", 0.4), r, bv=0.12)
    _room.ceiling_lights(rm, [(-8, 5), (8, 5), (-8, -6), (8, -6)], panel=(6.0, 1.2))
    _room.finish(rm, colour="#FFFFFF")
    marks = {"keeper": (x - 15.6, y - 2.0, 0.0, 90), "customer": (x - 9.8, y - 2.0, 0.0, -90),
             "aisle": (x + 3.0, y + 6.6, 0.0, 180), "fridge": (x + 12.0, y + 0.5, 0.0, 90),
             "door": (x + 8.0, y - 10.5, 0.0, 180), "window": (x - 9.0, y - 11.0, 0.0, 0)}
    cams = {"entrance": ((x + 9, y - 12.5, 8.0), (x - 4, y + 6, 3.6), 56),
            "over_counter": ((x - 17.2, y - 2.6, 7.4), (x - 9.8, y - 1.6, 4.4), 52),
            "customer_pov": ((x - 5.6, y - 6.0, 6.6), (x - 15.6, y - 1.0, 5.2), 44),
            "aisle": ((x + 14.0, y + 6.4, 4.8), (x - 6.0, y + 6.8, 4.0), 50),
            "fridge_side": ((x + 14.5, y - 9.5, 6.0), (x - 8, y + 2, 3.8), 50),
            "wide": ((x - 16.0, y - 12.0, 10.5), (x + 4, y + 6, 3.2), 58)}
    return {"marks": marks, "cams": cams}


def dress(p, sign="CORNER SHOP", special=None):
    _room.window_hook(p)
    b = p.one("bt_sign")
    bx, by, bz = b.location
    T.text(sign, 1.6, (bx + 0.2, by, bz), T.sign_mat(), p.root, rot=(90, 0, 90), extrude=0.05, max_w=10)
    if special:
        rm_y = -D / 2 + 0.55
        rbox((4.4, 0.08, 2.4), (-9, rm_y, 5.0), T.mat("#FFD23A", emit=0.6, key=("glow", "#FFD23A", 0.6)), p.root, bv=0.04)
        T.text(special, 0.9, (-9, rm_y + 0.06, 5.0), T.mat("#1B1D24", key="specialink"), p.root, rot=(90, 0, 180),
               extrude=0.0, max_w=4.0)
