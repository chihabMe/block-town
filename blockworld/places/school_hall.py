"""The school hall: stage, red curtains, a banner, a spotlight, rows of seats with an aisle. Parked at y = -560, far
from the street. The audience faces +Y, toward the stage at the back.

Episode arguments (never saved): banner (the words on the banner), crowd (True fills every seat with a random audience
member; p["crowd"] lists them and p["fill"](T, mood) seats them each frame).

Marks: stage (the middle of the stage floor, facing the audience), aisle, door, seat_1 .. seat_N (front row first,
       facing the stage). Yaw 0 faces -Y (toward the seats and the back of the hall).
Cams:  back (a wide from the back of the hall), crowd_pov (from the 3rd row to the stage), stage_front (from the front row,
       a little to the side), side (from the side wall across the seats).
Dict keys kept for older episodes: root, stage, light(on), seats, cam_back, crowd, fill.
"""
import random

import bpy

import town as T
from roblox import blob, disc, plastic, rbox

GEO = ("x", "y", "rows", "per_row")


def _glow(hexcol, k):
    return T.mat(hexcol, emit=k, key=("glow", hexcol, k))


def build(x=0, y=-560, rows=4, per_row=8):
    r = T.empty("hall", (x, y, 0))
    r["bt_root"] = True
    floor_m, wall_m = plastic("#B07A4A", 0.55), plastic("#3B3F70", 0.75)
    rbox((64, 80, 0.4), (0, 10, -0.2), floor_m, r, bv=0.05)
    for sx in (-1, 1):
        rbox((0.8, 80, 26), (sx * 32, 10, 13), wall_m, r, bv=0.05)                               # side walls
        for wy in (-14, 6, 26):
            rbox((0.2, 6, 10), (sx * 31.5, wy, 14), _glow("#9FD8FF", 0.6), r, bv=0.05)          # tall windows
    rbox((64, 0.8, 26), (0, 50, 13), wall_m, r, bv=0.05)                                         # back wall
    ceil = rbox((64, 80, 0.6), (0, 10, 26.3), plastic("#2A2E52", 0.8), r, bv=0.05)                # ceiling (no shadow:
    ceil.visible_shadow = False                                                                   # the sun still lights
    for cy in (-20, 0, 20):                                                                       # the room)
        rbox((50, 1.2, 0.4), (0, cy, 25.8), _glow("#FFF1D0", 1.4), r, bv=0.1)                   # strip lights
    wood, red, gold = plastic("#7A4A2C", 0.45), plastic("#B0182A", 0.65), plastic("#E8B23A", 0.3)
    rbox((40, 14, 3.0), (0, 42, 1.5), wood, r, bv=0.1)                                           # the stage
    rbox((40.4, 0.4, 0.5), (0, 35, 3.0), gold, r, bv=0.05)                                       # stage lip
    for i in range(3):                                                                            # steps
        rbox((6, 1.2, 1.0 * (i + 1)), (-14, 34.4 - 1.2 * (2 - i), 0.5 * (i + 1)), wood, r, bv=0.05)
    for sx in (-1, 1):                                                                            # curtains in folds
        for k in range(7):
            rbox((1.3, 1.0, 21), (sx * (19.5 - k * 1.2), 36.5 + (k % 2) * 0.5, 13.5), red, r, bv=0.3)
    for k in range(32):                                                                           # the valance on top
        rbox((1.3, 1.0, 4.0), (-19.4 + k * 1.25, 36.0 + (k % 2) * 0.4, 22.5), red, r, bv=0.3)
    rbox((41, 0.6, 0.6), (0, 35.6, 20.5), gold, r, bv=0.05)
    rbox((40, 0.4, 20), (0, 48.5, 13), plastic("#5A1420", 0.7), r, bv=0.05)                     # back curtain
    rbox((22, 0.3, 3.6), (0, 47.9, 17.5), plastic("#FFF4D6", 0.5), r, bv=0.1)                   # the banner
    for bx in (-11, 11):                                                                          # paper stars
        blob((0.9, 0.2, 0.9), (bx + 1.5, 47.7, 17.5), _glow("#FFD23A", 1.2), r)
    spot_m = T.mat("#FFF3C4", emit=1.0, key=("spot", x, y))
    spot = disc(4.6, 0.06, (0, 42, 3.05), spot_m, r, rot=(0, 0, 0), bv=0, verts=48)            # the light pool
    spot["bt_spot"] = True
    beam_m = T.mat("#FFF3C4", emit=0.6, key=("spotbeam", x, y))
    beam_m.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.07
    beam_m.surface_render_method = "BLENDED"
    bm = T.prim("cone", vertices=40, radius1=4.6, radius2=0.8, depth=22)
    bm.data.materials.append(beam_m)
    bm.location = (0, 42, 14)
    bm.parent = r
    bm.visible_shadow = False
    bm["no_shadow"] = True
    bm["bt_beam"] = True
    rbox((1.6, 2.4, 1.6), (0, 42, 25.5), plastic("#2A2C33", 0.4), r, bv=0.2)                    # the spotlight lamp
    seats = []
    chair = plastic("#2F3348", 0.5)
    for row in range(rows):
        sy = 22 - row * 6.5
        for k in range(per_row):
            sx = (k - (per_row - 1) / 2) * 5.0 + (2.5 if k >= per_row / 2 else -2.5)          # an aisle in the middle
            rbox((3.0, 2.6, 0.5), (sx, sy, 1.9), chair, r, bv=0.1)
            rbox((3.0, 0.5, 3.0), (sx, sy - 1.4, 3.2), chair, r, bv=0.1)              # the back (behind them)
            for lx in (-1.2, 1.2):
                rbox((0.25, 0.25, 1.7), (sx + lx, sy, 0.85), chair, r, bv=0.03)
            seats.append((x + sx, y + sy - 0.5, 0.0))
    marks = {"stage": (x, y + 42, 3.0, 0), "aisle": (x, y + 10, 0.0, 180), "door": (x, y - 26, 0.0, 180)}
    for i, s in enumerate(seats):
        marks[f"seat_{i + 1}"] = (*s, 180)
    third = 22 - min(2, rows - 1) * 6.5
    cams = {"back": ((x, y - 26, 12.0), (x, y + 40, 7.0), 50),
            "crowd_pov": ((x - 2.5, y + third - 1.5, 5.2), (x, y + 42, 7.5), 40),
            "stage_front": ((x + 5, y + 25, 5.0), (x, y + 42, 7.5), 45),
            "side": ((x + 29, y - 6, 9.0), (x - 6, y + 22, 3.5), 48)}
    return {"marks": marks, "cams": cams, "seats": seats}


def crowd_people(seats, seed=9):
    """A random audience, one per seat (the same people every time for the same seed)."""
    rng = random.Random(seed)
    shirts = ["#2FB5A8", "#F28A1E", "#8A4FB5", "#E23B3B", "#2F6FE0", "#3BB54A", "#FFC533", "#E88BA8", "#5A606B",
              "#00A3C4", "#C24E8A", "#7A9A2C"]
    skins = ["#F0C8A0", "#C98A5A", "#9A5B34", "#E4B58A", "#7A4A2C", "#EBC8A8", "#B97A4A"]
    hairs = ["black", "brown", "dark", "ginger", "blond"]
    styles = ["tuft", "side", "long", "bun", "pig", "curl"]
    people = []
    for i, s in enumerate(seats):
        p = T.character(f"Crowd{i}", rng.choice(skins), rng.choice(shirts), rng.choice(["#2B3350", "#3A3A46", "#31406B", "#22222A"]),
                        rng.choice(styles), rng.choice(hairs), seed=100 + i, scale=rng.choice([0.8, 0.9, 1.0]))
        people.append(p)
    return people


def dress(p, banner="TALENT SHOW", crowd=True):
    import anim
    r = p.root
    x, y = r.location.x, r.location.y
    T.text(banner, 2.2, (0, 47.7, 17.5), plastic("#D62B2B", 0.4, key="hallink"), r, extrude=0.03, max_w=20)
    spot, bm = p.one("bt_spot"), p.one("bt_beam")

    def light(on=True):
        spot.hide_render = bm.hide_render = not on
    seats = [tuple(s) for s in p.info["seats"]]
    p.update({"root": r, "stage": tuple(p.marks["stage"][:3]), "light": light, "seats": seats,
              "cam_back": ((x, y - 26, 12.0), (x, y + 40, 7.0))})
    if not crowd:
        return
    people = crowd_people(seats)
    p["crowd"] = people

    def fill(Tm, mood="sit", k=1.0, skip=(), turn=0.0):
        """Seat the whole audience for this frame (they face the stage). mood: "sit", "clap", "cheer", "gasp".
        turn > 0 turns every head toward +X by that many degrees (a crowd looking at someone in the aisle)."""
        for i, (c, st) in enumerate(zip(people, seats)):
            if i in skip:
                continue
            ph = i * 0.7
            if mood == "clap":
                anim.clap(c, st, 180, "happy", Tm, ph, seated=True)
            elif mood == "cheer":
                anim.cheer(c, st, 180, "laugh" if i % 3 else "happy", Tm, ph, seated=True)
            elif mood == "gasp":
                anim.gasp(c, st, 180, k, Tm, ph, seated=True)
            else:
                anim.sit(c, st, 180, "smile" if i % 4 else "sleepy", Tm, ph,
                         head=(turn + anim.osc(Tm, 0.33, 4, ph), anim.osc(Tm, 0.5, 2, ph)))
    p["fill"] = fill
