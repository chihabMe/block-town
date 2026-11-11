"""Episode 1 intro: every lie makes you one inch shorter. Nine shots, about 11 seconds.

Run only through the kit (from the skill folder):

    blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep01-intro check
    blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep01-intro stills
    blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep01-intro render

This is the model for a new episode. Copy this folder, then replace the script, the props,
the extra characters and the shot functions. The street, the cast and the moves stay as they are.
"""
import math

from mathutils import Vector

from anim import *
from props import car, pole_sign, ruler_wall, shoebox

build_town("1 LIE = 1 INCH", ("TALL & SMALL", "HONEST PIES"))
ruler_wall(21.6, 60)
car(-9.4, 120, sticker="LIKE NEW!")
pole_sign(-20.2, 126.5, "HONEST AL'S", "CARS", yaw=90)
BOX_AT = Vector((-15.0, 123.2, WALK))
BOX_YAW = -26
shoebox(BOX_AT.x, BOX_AT.y, BOX_YAW)


def box_pt(x, y, z=0.0):
    """A point in the shoebox's own coordinates. Its door is on the -y side."""
    a = math.radians(BOX_YAW)
    return BOX_AT + Vector((x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z))


BABY = character("Baby", "#EDB78F", "#EDB78F", "#FFFFFF", "curl", "brown", shoes="#EDB78F")
SAL = character("Sal", "#E4B58A", "#3E6FD9", "#22222A", "side", "black", sleeves="long", tie="#FFD84A")

BUBBLE = card(["I NEVER", "LIE!"], 0.62, bubble=True)
MINUS = card(["−1 INCH"], 0.5, "#FF3B30")
LINE = [(TALL, 1.5, 69, "happy"), (GRAN, 0.42, 66, "smug"), (DAD, 1.0, 63, "smile"), (BOY, 0.5, 60, "angry"),
        (TEACH, 0.85, 57, "stern"), (KID, 1.25, 54, "happy"), (MAN, 0.88, 51, "smug")]
LINE_TAGS = [card([feet(s)], 0.62, "#5BE36B" if s >= 1 else "#FF4B40") for _, s, _, _ in LINE]
TAG_TALL = card([feet(1.4)], 0.85, "#5BE36B")
TAG_BOY = card([feet(0.5)], 0.7, "#FF4B40")
TAG_SAL = card(["7 in"], 0.09, "#FF4B40")
WX = 19.3


def wide(t, d, T):
    """In this town,"""
    for i, (c, s, x, y, way, face) in enumerate((
            (NIA, 0.3, RX, 20, 1, "smile"), (TEACH, 0.85, LX, 44, -1, "stern"), (TALL, 1.5, RX - 1, 56, -1, "happy"),
            (BOY, 0.5, LX + 2, 4, 1, "smug"), (DAD, 1.0, RX + 1, 98, 1, "smile"), (GRAN, 0.42, LX, 80, -1, "happy"),
            (KID, 1.25, LX - 1, 112, 1, "laugh"), (MAN, 0.88, RX, 130, -1, "smile"), (SAL, 0.2, LX + 3, 26, 1, "smug"))):
        size(c, s)
        walk(c, x, y, way, T, face, ph=i * 1.7)
    shot(mix((8, -52, 52), (6, -30, 40), smooth(t / d)), (0, 80, 6), 56)


def liar(t, d, T):
    """every lie you tell"""
    k = snap(t, WT[4] - cut(3))
    size(MAN, 1.0)
    size(TEACH, 0.85)
    stand(MAN, (WX, 60, WALK), -90, "smug", T, armR=mix((0, 6), (10, 138), k), armL=mix((0, 6), (20, 34), k),
          lean=mix(0, 5, k), head=(0, mix(0, 10, k)))
    stand(TEACH, (17.2, 57.6, WALK), 180 + 28, "glasses", T, ph=2, head=(mix(0, -12, k), 6), armL=(40, -24), armR=(40, -24))
    shot(mix((9.0, 59.3, 3.7), (9.8, 59.4, 3.8), smooth(t / d)), (WX, 59.5, 4.9), 50)
    put(BUBBLE, (WX - 0.6, 60.2, 7.75), k)


def shrink(t, d, T):
    """makes you one inch shorter."""
    t0 = cut(8)
    hit = WT[9] - t0
    up = smooth((t - 0.02) / max(hit - 0.02, 0.01)) if t < hit else 0.0
    k = snap(t, hit, 0.16)
    s = mix(1.0 + 0.05 * up, 0.86, k)
    size(MAN, s, squash=1 - 0.10 * math.sin(math.pi * clamp((t - hit) / 0.22)))
    wob = math.exp(-6 * max(t - hit, 0)) * math.sin(40 * max(t - hit, 0)) if t >= hit else 0
    stand(MAN, (WX, 60, WALK), -90, "shock" if t >= hit else "smug", T,
          armR=mix((10, 138), (10, 58), k), armL=mix((20, 34), (10, 58), k), lean=mix(5, -4, k), tilt=wob * 6)
    shot(Vector(mix((12.6, 60.7, 4.7), (12.2, 60.6, 4.3), k)) + Vector((0, wob * 0.16, wob * 0.12)),
         (WX, 60, mix(5.0, 4.5, k)), 42)
    put(MINUS, (WX - 0.4, 60, 6.25), snap(t, WT[10] - t0))


def lineup(t, d, T):
    """You see, everyone here is"""
    y = mix(67.5, 54.5, smooth(t / d))
    shot((7.2, y, 3.3), (WX, y - 0.6, 3.9), 56)
    for i, (c, s, cy, face) in enumerate(LINE):
        size(c, s)
        stand(c, (WX, cy, WALK + abs(osc(T, 1.0, 0.08, i)) * s), -90, face, T, ph=i * 1.3,
              armL=(10, 140 + osc(T, 2.5, 18)) if c in (GRAN, KID) else (osc(T, 0.5, 3, i), 6))
        put(LINE_TAGS[i], (WX, cy, WALK + s * 5.3 + 0.85), 1.0)


def pair(t, d, T):
    """exactly as tall as they are honest."""
    t0 = cut(17)
    k1, k2 = snap(t, WT[19] - t0), snap(t, WT[23] - t0)
    size(TALL, 1.4)
    size(BOY, 0.5)
    stand(TALL, (WX, 61.0, WALK), -90 - 22, "happy", T, armR=(10, 142 + osc(T, 2.2, 16)), head=(24, -18), lean=-5)
    stand(BOY, (WX - 0.8, 58.2, WALK + abs(osc(T, 2.0, 0.1))), -90 + 30, "stern" if k2 > 0 else "angry", T, ph=1,
          armL=(46, -30), armR=(46, -30), head=(mix(26, -34, k2), mix(26, 4, k2)))
    shot(mix((3.4, 59.4, 1.5), (4.6, 59.5, 1.6), smooth(t / d)), (WX, 59.7, 6.0), 54)
    put(TAG_TALL, (WX, 61.0, WALK + 1.4 * 5.3 + 0.8), k1)
    put(TAG_BOY, (WX - 1.2, 58.2, WALK + 0.5 * 5.3 + 0.9), k2)


def baby(t, d, T):
    """Babies are the tallest people in town."""
    step = math.sin(2 * math.pi * 1.3 * T)
    size(BABY, 9)
    pose(BABY, (0, 142 - 6 * t, 0.1), 0, "happy", armL=(20 + 14 * step, 52), armR=(20 - 14 * step, 52),
         legL=16 * step, legR=-16 * step, tilt=5 * step, head=(4 * step, 0))
    for i, (c, s, x, y) in enumerate(((DAD, 1.0, -3.2, 60), (TEACH, 0.85, 1.6, 62.5), (MAN, 0.88, 5.4, 59.5),
                                      (BOY, 0.5, -0.6, 57), (GRAN, 0.42, 3.2, 56.5), (KID, 1.25, -7.2, 63))):
        size(c, s)
        stand(c, (x, y, 0.1 + abs(osc(T, 1.3, 0.1, i))), 180, "shock", T, ph=i, head=(0, 30),
              armR=(128, 8) if i % 2 == 0 else (osc(T, 0.5, 3), 16), armL=(140, 30) if i == 3 else (0, 16), lean=6)
    k = smooth(t / d)
    shot(Vector(mix((3.5, 36, 2.4), (3.0, 43, 2.5), k)) + Vector((0, 0, abs(step) ** 6 * 0.25)),
         (0, 130, mix(19, 24, k)), 60)


def babyface(t, d, T):
    """They can't lie yet."""
    k = snap(t, WT[32] - cut(31))
    size(BABY, 9)
    clap = osc(T, 3.0, 10)
    pose(BABY, (0, 133, 0.1 + abs(osc(T, 1.5, 0.5))), 0, "happy" if k > 0 else "smile", armL=(58, -12 + clap),
         armR=(58, -12 + clap), tilt=osc(T, 1.5, 0.8), head=(mix(0, 9, k) + osc(T, 0.7, 4), mix(-4, 6, k)))
    shot(mix((3.5, 66, 43.5), (3.0, 73, 43.0), smooth(t / d)), (0.2, 133, 41.6), 30)


def carlot(t, d, T):
    """Car salesmen"""
    k = smooth(t / d)
    size(SAL, 0.11)
    pose(SAL, box_pt(-0.45, -0.5), BOX_YAW, "smug")
    shot(mix((5.5, 108.5, 3.4), (2.0, 111.5, 3.0), k), (-11.5, 122.0, mix(4.6, 3.6, k)), 54)


def shoebox_shot(t, d, T):
    """live in shoeboxes."""
    t0 = cut(37)
    out = smooth((t - 0.08) / 0.3)
    hop = math.sin(math.pi * out) * 0.12
    k = snap(t, WT[39] - t0)
    size(SAL, 0.11)
    pose(SAL, box_pt(-0.45, mix(-0.5, -1.25, out), hop), BOX_YAW, "happy" if k > 0 else "smug",
         armL=(10, mix(6, 142, out) + osc(T, 3.0, 16)), armR=(mix(0, 20, k), mix(6, 40, k)),
         legL=osc(T, 3.0, 20) * (1 - out), legR=-osc(T, 3.0, 20) * (1 - out), head=(0, 18), tilt=osc(T, 1.5, 3))
    kk = smooth(t / d)
    shot(mix(box_pt(-1.6, -7.2, 1.7), box_pt(-1.3, -4.3, 0.8), kk),
         Vector(mix(box_pt(0.1, -0.6, 0.45), box_pt(-0.4, -1.1, 0.36), kk)), 38)
    put(TAG_SAL, box_pt(-0.45, -1.25, 0.11 * 5.3 + 0.17), k)


SHOTS = [("wide", 0.0, wide), ("liar", cut(3), liar), ("shrink", cut(8), shrink), ("lineup", cut(12), lineup),
         ("pair", cut(17), pair), ("baby", cut(24), baby), ("babyface", cut(31), babyface),
         ("carlot", cut(35), carlot), ("shoebox", cut(37), shoebox_shot)]

run(SHOTS)
