"""A small bedroom: bed with a blanket that can be pulled up, nightstand with a lamp, a night window with the moon, a
rug. Parked at y = -460 (a second bedroom 60 studs along x). It faces -Y: film it from (x, y - 13, 5) or closer.

Shape arguments: x, y, wall, blanket (colours).
Marks: seat (sitting up in bed: stand(c, p.spot("seat"), 0, face, T, legL=90, legR=90)), stand (the nightstand top),
       floor (standing beside the bed).
Cams:  front (the whole room), bed_close (a close-up of the bed), door (from the doorway, low).
Dict keys kept for older episodes: root, seat, tuck(k), stand, lamp (the lamp's material: T.emission(p["lamp"], k)).
"""
import town as T
from roblox import blob, plastic, rbox

GEO = ("x", "y", "wall", "blanket")


def _glow(hexcol, k):
    return T.mat(hexcol, emit=k, key=("glow", hexcol, k))


def build(x=0, y=-460, wall="#5C6B94", blanket="#E8A33C"):
    r = T.empty("bedroom", (x, y, 0))
    r["bt_root"] = True
    floor_m, wall_m = plastic("#8A6A4F", 0.6), plastic(wall, 0.7)
    rbox((22, 16, 0.4), (0, 0, -0.2), floor_m, r, bv=0.05)
    rbox((22, 0.6, 14), (0, 8, 7), wall_m, r, bv=0.05)                                      # back wall
    rbox((0.6, 16, 14), (-11, 0, 7), wall_m, r, bv=0.05)                                    # left wall
    rbox((5.2, 0.4, 4.6), (5.5, 7.65, 8.4), _glow("#1B2A5C", 1.0), r, bv=0.05)              # night window
    for fx, fz, sx, sz in ((5.5, 10.85, 5.8, 0.3), (5.5, 5.95, 5.8, 0.3), (2.75, 8.4, 0.3, 5.2), (8.25, 8.4, 0.3, 5.2),
                           (5.5, 8.4, 0.2, 4.6)):
        rbox((sx, 0.5, sz), (fx, 7.5, fz), plastic("#EDEDF0", 0.5), r, bv=0.03)
    blob((0.3, 0.3, 0.3), (3.6, 7.3, 9.8), _glow("#FFF6D8", 2.0), r)                       # the moon in the window
    wood = plastic("#6B4A33", 0.5)
    rbox((6.4, 10.5, 1.4), (-4.5, 2.6, 0.9), wood, r, bv=0.15)                              # bed frame
    rbox((6.8, 0.5, 4.2), (-4.5, 7.75, 2.1), wood, r, bv=0.15)                              # headboard
    rbox((6.0, 10.0, 0.9), (-4.5, 2.6, 2.0), plastic("#F2F2F4", 0.6), r, bv=0.25)           # mattress
    rbox((3.6, 1.6, 0.9), (-4.5, 6.6, 2.75), plastic("#FFFFFF", 0.6), r, bv=0.35)           # pillow
    bl = plastic(blanket, 0.7)
    rbox((6.4, 6.8, 0.6), (-4.5, 0.8, 2.6), bl, r, bv=0.25)                                 # blanket over the legs
    flap = T.empty("bedroom.flap", (-4.5, 3.6, 2.6), r)                                     # the part pulled up
    flap["bt_flap"] = True
    flap["bt_live"] = True                                                                  # it moves (tuck)
    rbox((5.2, 0.7, 1.0), (0, 0, 0.5), bl, flap, bv=0.25)
    rbox((2.6, 2.4, 2.8), (1.4, 6.4, 1.4), wood, r, bv=0.15)                                # nightstand
    lamp_m = T.mat("#FFC56B", emit=1.0, key=("bedlamp", x, y))
    rbox((0.3, 0.3, 1.2), (2.2, 6.9, 3.4), plastic("#2A2C33", 0.4), r, bv=0.03)
    rbox((1.2, 1.2, 0.9), (2.2, 6.9, 4.3), lamp_m, r, bv=0.2)
    rbox((8, 5, 0.06), (-2, -3.5, 0.02), plastic("#B5463E", 0.8), r, bv=0)                  # rug
    T.emission(lamp_m, 0.0)
    return {"marks": {"seat": (x - 4.5, y + 4.6, 0.5, 0), "stand": (x + 1.4, y + 6.4, 2.8), "floor": (x + 1.0, y + 1.0, 0.0, 0)},
            "cams": {"front": ((x, y - 13, 5.0), (x - 1, y + 3, 4.0), 50),
                     "bed_close": ((x - 1.5, y - 2.5, 4.6), (x - 4.5, y + 4.6, 4.5), 38),
                     "door": ((x + 8.5, y - 7, 3.2), (x - 3, y + 4, 3.5), 45)},
            "lamp_key": repr(("bedlamp", x, y))}


def dress(p):
    import ast

    import anim
    flap = p.one("bt_flap")
    x, y = p.root.location.x, p.root.location.y

    def tuck(k):
        """0 = blanket at the waist, 1 = pulled up to the nose (in front of a sitting character's face)."""
        flap.scale = (1, 1, 1 + 1.3 * k)
    tuck(0)
    anim.before_each_frame(lambda Tm: tuck(0))
    p.update({"root": p.root, "seat": (x - 4.5, y + 4.6, 0.5), "tuck": tuck, "stand": (x + 1.4, y + 6.4, 2.8),
              "lamp": T.MATS[ast.literal_eval(p.info["lamp_key"])]})
