"""Ready-made set pieces. Each one is boxes under one parent, built in the parent's own coordinates.
Use them as they are, or copy one as the pattern for a new prop (see docs/GUIDE.md, "Building a new prop")."""
from town import WALK, WIN, box, cylinder, empty, mat, sign_mat, text


def car(x, y, col="#E23B3B", sticker=None, yaw=0):
    """A boxy car on the road, nose toward +Y (yaw turns it). sticker = a few words on the roof, or None."""
    r = empty("car", (x, y, 0.1), yaw=yaw)
    m, glass, dark = mat(col), mat("#BFE9FA", emit=0.3, key="carglass"), mat("#1A1A1E")
    box((4.6, 10, 1.7), (0, 0, 1.75), m, r)
    box((4.2, 5.2, 1.6), (0, -0.7, 3.4), m, r)
    box((4.3, 4.3, 1.05), (0, -0.7, 3.45), glass, r)
    box((3.7, 5.3, 1.05), (0, -0.7, 3.45), glass, r)
    box((4.8, 0.5, 0.6), (0, 5.05, 1.2), mat("#C9CCD4"), r)
    box((4.8, 0.5, 0.6), (0, -5.05, 1.2), mat("#C9CCD4"), r)
    for sx in (-1, 1):
        box((0.9, 0.2, 0.5), (sx * 1.6, 5.02, 2.0), mat("#FFE9A0", emit=1.5, key="headlight"), r)
        for sy in (-1, 1):
            cylinder(1.0, 0.8, (sx * 2.1, sy * 3.1, 0.95), dark, r, rot=(0, 90, 0))
            box((0.1, 0.9, 0.9), (sx * 2.52, sy * 3.1, 0.95), mat("#C9CCD4"), r)
    if sticker:
        box((3.2, 0.1, 1.0), (0, 1.3, 4.72), mat("#FFE23B", emit=1.0, key="sticker"), r, rot=(-90, 0, 0))
        text(sticker, 0.5, (0, 1.3, 4.79), dark, r, rot=(0, 0, -90), extrude=0.0)
    return r


def pole_sign(x, y, small, big, yaw=90, board="#C62B3A", bunting=True, z=WALK):
    """A sign on a pole: a small white line over a big yellow line. It faces its local -Y:
    yaw 90 faces +X (toward the road from the left sidewalk), yaw -90 faces -X, yaw 0 faces -Y (up the street)."""
    r = empty("polesign", (x, y, z), yaw=yaw)
    box((0.7, 0.7, 12), (0, 0.3, 6), mat("#16171C"), r)
    box((10.4, 0.5, 5.4), (0, 0, 10), mat("#F5C52A"), r)
    box((9.8, 0.5, 4.8), (0, -0.1, 10), mat(board), r)
    text(small, 1.05, (0, -0.4, 11.0), mat("#FFFFFF", emit=1.5, key="bbwhite"), r, extrude=0.05, max_w=9.0)
    text(big, 1.9, (0, -0.4, 9.0), sign_mat(), r, extrude=0.06, max_w=9.0)
    if bunting:
        for i in range(9):
            box((0.9, 0.06, 0.9), (-6 + i * 1.5, -0.2, 6.6 + 0.25 * abs(i - 4)),
                mat(("#FF4FA0", "#39C2F5", "#FFE23B")[i % 3]), r, rot=(0, 45, 0))
    return r


def ruler_wall(x, y, title="HEIGHT CHECK", length=30, top=10, yaw=-90, z=WALK):
    """A pale wall with a line and a label every foot, and a title board on top. It faces its local -Y
    (yaw -90 faces -X: put it at x = 21.6 on the right sidewalk and stand people at x = 19.3 facing -X)."""
    r = empty("wall", (x, y, z), yaw=yaw)
    box((length, 0.5, top), (0, 0, top / 2), mat("#E6E1D2"), r)
    box((length + 0.8, 0.8, 1.7), (0, 0, top + 0.85), mat("#1B1F3A"), r)
    text(title, 1.1, (0, -0.46, top + 0.85), sign_mat(), r, extrude=0.05, max_w=length - 2)
    ln = mat("#2A2C38")
    for n in range(1, top):
        box((length, 0.06, 0.13), (0, -0.25, n), ln, r)
        box((length, 0.06, 0.05), (0, -0.25, n - 0.5), mat("#A9ACB5"), r)
        for i in range(int(length // 3)):
            text(f"{n} ft", 0.42, (-length / 2 + 1.5 + i * 3, -0.27, n + 0.36), ln, r, extrude=0.0)
    for sx in (-1, 1):
        box((0.8, 0.8, top + 1.7), (sx * (length / 2 + 0.4), 0, (top + 1.7) / 2), mat("#16171C"), r)
    return r


def shoebox(x, y, yaw=0):
    """A house the size of a shoebox, door on local -Y. A 0.11-scale person (about 7 inches) fits the door.
    Place the person in the box's own coordinates, not by guessing world coordinates around the yaw."""
    r = empty("shoebox", (x, y, WALK), yaw=yaw)
    box((2.0, 1.1, 0.74), (0, 0, 0.37), mat("#C99A5B"), r)
    box((2.12, 1.22, 0.18), (0.03, 0, 0.8), mat("#A8742F"), r, rot=(0, 5, 0))
    box((2.02, 0.02, 0.16), (0, -0.56, 0.52), mat("#E94B5B"), r)
    box((0.3, 0.03, 0.6), (-0.45, -0.56, 0.3), mat("#2A1A12"), r)
    box((0.34, 0.03, 0.26), (0.42, -0.56, 0.36), WIN, r)
    box((0.42, 0.3, 0.02), (-0.45, -0.75, 0.01), mat("#3FA338"), r)
    box((0.03, 0.03, 0.34), (0.95, -0.8, 0.17), mat("#16171C"), r)
    box((0.16, 0.1, 0.1), (0.95, -0.8, 0.36), mat("#2F6FE0"), r)
    return r
