"""A classroom: a green chalkboard on the front wall, the teacher's desk, nine pupil desks in three rows facing the
board, windows down the right wall, a door at the front left, cubbies and posters at the back, a wall clock, ceiling
lights. Parked at (0, -760). The board is at +Y; pupils face +Y.

Episode arguments (never saved):
    board         lines of chalk writing on the board, e.g. ("RULE 1:", "NEVER ASK WHY")  (None = a blank board)
    board_picture a picture name (EPISODE/pictures.json or the kit's) pinned to the board instead, e.g. "class_photo"
Marks:  teacher (at the desk, facing the class), board (at the board, facing the class), door (just inside the door),
        window (at the window, looking out), desk_1 .. desk_9 (sit(c, p.spot("desk_5"), p.yaw("desk_5"), ...);
        desk_1-3 is the front row and desk_7-9 the back row, each from x -10 to +10; desk_5 is the middle)
Cams:   back (a wide from the back corner), teacher_pov (from the board over the class), pupil_pov (from a back desk to
        the board), window_side (along the windows across the desks), board_close (the board and whoever stands at it),
        door (from the doorway)
"""
import town as T
from roblox import blob, disc, plastic, rbox
from world2 import multi

from places import _room

GEO = ("x", "y")
W, D, H = 40, 34, 13


def _pupil_desk(r, x, y, wood, metal, tops):
    """A desk sized for sit(): seat top at z 2.0 (the chair is behind the desk, toward -Y), desk top at z 3.3."""
    rbox((3.4, 2.4, 0.22), (x, y + 0.2, 3.3), tops, r, bv=0.06)                       # desk top
    legs = [((0.16, 0.16, 3.2), (x + sx, y + 0.2 + sy, 1.6)) for sx in (-1.5, 1.5) for sy in (-1.0, 1.0)]
    legs += [((0.16, 0.16, 1.9), (x + sx, y - 1.9 + sy, 0.95)) for sx in (-0.75, 0.75) for sy in (-0.6, 0.6)]
    multi("desk.legs", legs, metal, r)
    rbox((1.8, 1.6, 0.2), (x, y - 1.9, 1.95), wood, r, bv=0.05)                        # chair seat
    rbox((1.8, 0.18, 1.7), (x, y - 2.75, 2.9), wood, r, bv=0.05)                       # chair back


def build(x=0, y=-760):
    rm = _room.room("classroom", x, y, W, D, H, floor="#B98A55", low="#4E9C88", high="#F0D9A8")
    r = rm["root"]
    # front wall: the board, its frame and chalk tray, the clock, a flag of letters
    s, c = _room.on_wall(rm, "N", 2, 7.2, 20, 7.4, 0.2)
    board = rbox(s, c, plastic("#2F5440", 0.85), r, bv=0.04)
    board["bt_board"] = True
    for (ww, hh, oo, zz) in ((21, 0.5, 2, 11.15), (21, 0.5, 2, 3.25), (0.5, 7.9, -8.25, 7.2), (0.5, 7.9, 12.25, 7.2)):
        rm["frames"].append(_room.on_wall(rm, "N", oo, zz, ww, hh, 0.45))
    s, c = _room.on_wall(rm, "N", 2, 3.05, 20, 0.2, 1.0)
    rbox(s, c, plastic("#8A5A3C", 0.5), r, bv=0.04)                                    # chalk tray
    for k, col in enumerate(("#FFFFFF", "#FFD23A", "#FF7FB0")):
        s, c = _room.on_wall(rm, "N", -4 + k * 0.9, 3.25, 0.7, 0.18, 0.18, inset=0.5)
        rbox(s, c, plastic(col, 0.8), r, bv=0.04)
    s, c = _room.on_wall(rm, "N", 16, 10.4, 1, 1, 0.3)
    clock = disc(1.3, 0.3, c, plastic("#FFFFFF", 0.4), r, rot=(90, 0, 0), bv=0.1, verts=32)
    disc(1.45, 0.2, (c[0], c[1] + 0.06, c[2]), plastic("#E23B3B", 0.4), r, rot=(90, 0, 0), bv=0.06, verts=32)
    rbox((0.12, 0.05, 0.9), (c[0], c[1] - 0.2, c[2] + 0.35), plastic("#1B1D24", 0.5), r, bv=0)          # hands at 3
    rbox((0.7, 0.05, 0.12), (c[0] + 0.3, c[1] - 0.2, c[2]), plastic("#1B1D24", 0.5), r, bv=0)
    letters = {"#E23B3B": [], "#2F6FE0": [], "#FFC533": [], "#3BB54A": []}            # an alphabet strip over the board
    for i in range(12):
        s, c = _room.on_wall(rm, "N", -15 + i * 2.7, 12.2, 2.0, 1.2, 0.08)
        list(letters.values())[i % 4].append((s, c))
    _room.colour_boxes("classroom.letters", letters, r, 0.7)
    # teacher's desk, chair, apple, books
    oak = plastic("#9A6A42", 0.5)
    rbox((8, 3.6, 3.2), (-4, 11.2, 1.6), oak, r, bv=0.1)
    rbox((8.6, 4.0, 0.3), (-4, 11.2, 3.35), plastic("#B07A4A", 0.45), r, bv=0.08)
    blob((0.42, 0.42, 0.4), (-6.5, 10.6, 3.9), plastic("#E8202A", 0.3), r)
    rbox((0.08, 0.08, 0.35), (-6.5, 10.6, 4.4), plastic("#5A3A22", 0.6), r, bv=0)
    _room.colour_boxes("classroom.books", {"#2F6FE0": [((1.6, 1.1, 0.3), (-1.5, 11.0, 3.65))],
                                           "#FFC533": [((1.5, 1.0, 0.28), (-1.5, 11.0, 3.95))],
                                           "#3BB54A": [((1.4, 1.0, 0.26), (-1.4, 11.0, 4.22))]}, r)
    rbox((2.2, 2.0, 0.3), (-4, 14.2, 2.0), plastic("#2F3348", 0.5), r, bv=0.06)          # teacher's chair
    rbox((2.2, 0.3, 2.4), (-4, 15.2, 3.3), plastic("#2F3348", 0.5), r, bv=0.06)
    # pupil desks: 3 x 3, facing the board
    wood, metal, tops = plastic("#D9A86A", 0.55), plastic("#5A606B", 0.35), plastic("#E8C08A", 0.5)
    desks = []
    for row, dy in enumerate((3.5, -3.5, -10.5)):
        for col, dx in enumerate((-10, 0, 10)):
            _pupil_desk(r, dx, dy, wood, metal, tops)
            desks.append((dx, dy - 1.9))
    # windows down the right wall, a door at the front of the left wall
    for wy in (-9, 0, 9):
        _room.window(rm, "E", wy, z=7.4, sw=6.0, sh=6.4)
        s, c = _room.on_wall(rm, "E", wy + 1.8, 4.1, 1.0, 1.0, 1.0, inset=0.1)
        rbox((0.9, 0.9, 0.9), (c[0], c[1], 3.75), plastic("#B5653A", 0.6), r, bv=0.1)          # a pot on the sill
        blob((0.75, 0.75, 0.75), (c[0], c[1], 4.6), plastic("#3FA338", 0.6), r)
    dx_, dy_ = _room.door(rm, "W", 11, colour="#2F6FE0")
    # back wall: cubbies with bags, posters
    cub = plastic("#E9D3B0", 0.6)
    s, c = _room.on_wall(rm, "S", -6, 2.6, 16, 5.2, 1.6)
    rbox(s, c, cub, r, bv=0.05)
    bags = {"#E23B3B": [], "#2F6FE0": [], "#FFC533": [], "#8A4FB5": [], "#3BB54A": []}
    cols = list(bags)
    for i in range(10):
        bx, bz = -13 + (i % 5) * 3.5, 1.3 + (i // 5) * 2.6
        s, c = _room.on_wall(rm, "S", bx, bz, 2.4, 1.8, 0.5, inset=1.4)
        bags[cols[(i * 3) % 5]].append((s, c))
    _room.colour_boxes("classroom.bags", bags, r, 0.6)
    for k, (px, col) in enumerate(((8, "#FFC533"), (14, "#7FD3F5"))):
        s, c = _room.on_wall(rm, "S", px, 7.6, 4.6, 5.6, 0.08)
        rbox(s, c, plastic(col, 0.8), r, bv=0.02)
        s, c = _room.on_wall(rm, "S", px, 7.6 + 1.2, 3.2, 0.5, 0.12)
        rbox(s, c, plastic("#1B1D24", 0.8), r, bv=0)
        for j in range(3):
            s, c = _room.on_wall(rm, "S", px - 1.2 + j * 1.2, 6.6, 0.8, 0.8, 0.12)
            rbox(s, c, plastic(("#E23B3B", "#2F6FE0", "#3BB54A")[j], 0.6), r, bv=0.05)
    _room.ceiling_lights(rm, [(-10, 5), (10, 5), (-10, -8), (10, -8)])
    _room.finish(rm)
    marks = {"teacher": (x - 4, y + 8.6, 0.0, 0), "board": (x + 9, y + 14.2, 0.0, 0),
             "door": (x + dx_ + 1.2, y + dy_, 0.0, 90), "window": (x + 16.8, y, 0.0, 90)}
    for i, (sx, sy) in enumerate(desks):
        marks[f"desk_{i + 1}"] = (x + sx, y + sy, 0.0, 180)
    cams = {"back": ((x + 15, y - 14.5, 10.5), (x - 2, y + 8, 4.5), 55),
            "teacher_pov": ((x - 1, y + 14.2, 7.5), (x + 1, y - 8, 3.2), 52),
            "pupil_pov": ((x + 2.5, y - 12.5, 5.6), (x + 2, y + 16, 6.4), 46),
            "window_side": ((x + 17.5, y - 14, 6.5), (x - 4, y + 4, 3.6), 48),
            "board_close": ((x + 6, y + 3.5, 6.0), (x + 7, y + 16, 6.4), 46),
            "door": ((x - 17.5, y + 14.5, 8.5), (x + 4, y - 4, 3.0), 52)}
    return {"marks": marks, "cams": cams}


def dress(p, board=None, board_picture=None):
    import rprops
    _room.window_hook(p)
    b = p.one("bt_board")
    bx, by, bz = b.location
    if board_picture:
        q = rprops.picture_quad(board_picture, 7.6, 5.5, by - 0.18, rprops.paper_picture(board_picture), p.root, z=bz)
        q.location.x = bx
    elif board:
        chalk = T.mat("#F4F4EE", emit=0.25, key="chalk")
        lines = [board] if isinstance(board, str) else list(board)
        n = len(lines)
        for i, line in enumerate(lines):
            z = bz + (n - 1) * 0.75 - i * 1.5
            T.text(line, 1.15, (bx, by - 0.16, z), chalk, p.root, extrude=0.0, max_w=18)
