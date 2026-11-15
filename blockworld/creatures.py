"""Creatures (viral pack, Nov 2026): a giant monster and blocky animals, in the same toy-plastic look as the town.
Giant monsters showed up in 4 of the 17 viral hits we studied (a stick creature with a big mouth, zombies, a shadow
giant); animals and swarms in 2 more. Build once at the top of the episode, pose every frame inside a shot.

    m = monster()                              a 3-storey dark stick creature: glowing eyes, a jaw that opens
    monster_walk(m, start, yaw, t)             heavy long strides (t = seconds since it set off)
    monster_reach(m, loc, yaw, k, T)           leans in and reaches one long arm toward the camera (k 0 -> 1)
    monster_roar(m, loc, yaw, k, T)            head back, jaw wide open, arms spread, shaking (k 0 -> 1)
    monster_stand(m, loc, yaw, T)              looming, breathing, the head tilting

    p = penguin();  waddle(p, start, yaw, t)   rocking side to side, flippers flapping
    f = frog();     hop(f, start, yaw, t)      hops forward in arcs
    l = lion();     trot(l, start, yaw, t)     a bouncy trot
    swarm(penguin, 40)                         many copies (pose each with its own offset and phase)

All face -Y at yaw 0 like the characters; start / loc is where the feet stand. `from anim import *` brings them in.
"""
import math

from mathutils import Vector

import town as T
from roblox import blob, plastic, rbox

__all__ = ["monster", "monster_walk", "monster_reach", "monster_roar", "monster_stand", "penguin", "waddle", "frog",
           "hop", "lion", "trot", "swarm"]

PARK = (500.0, -500.0, 0.0)        # where unused creatures wait, out of every shot
_ROOTS = []                         # every creature's root: each frame starts with them all parked


def _register(root):
    """Park this creature at the start of every frame, so it only shows in the shots that pose it."""
    if not _ROOTS:
        import anim

        def park_all(T_):
            for r in _ROOTS:
                r.location = PARK
        anim.before_each_frame(park_all)
    _ROOTS.append(root)


def _glow(hexcol, k):
    return T.mat(hexcol, emit=k, key=("glow", hexcol, k))


def _joint(name, loc, parent):
    return T.empty(name, loc, parent)


def _fwd(yaw):
    a = math.radians(yaw)
    return Vector((math.sin(a), -math.cos(a), 0.0))


def _sm(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def _rot(o, x=0.0, y=0.0, z=0.0):
    o.rotation_euler = (math.radians(x), math.radians(y), math.radians(z))


# ---------------------------------------------------------------- the giant monster
def monster(name="Monster", skin="#1E1E26", eyes="#FFE9A8", scale=1.0):
    """A 3-storey (about 20 studs) dark stick creature with long jointed limbs, two glowing eyes and a wide mouth of
    white teeth whose jaw opens. Parked out of sight until posed."""
    m = {"name": name}
    skin_m, dark = plastic(skin, 0.55), plastic("#0E0E12", 0.6)
    teeth, mouth = plastic("#F4F1E8", 0.35), plastic("#4A0F16", 0.7)
    root = T.empty(name, PARK)
    root.scale = (scale, scale, scale)
    _register(root)
    hips = _joint(name + ".hips", (0, 0, 10.5), root)
    rbox((2.6, 1.6, 1.4), (0, 0, 0.3), skin_m, hips, bv=0.35)
    chest = _joint(name + ".chest", (0, 0, 0.9), hips)
    rbox((3.0, 1.8, 5.0), (0, 0, 2.6), skin_m, chest, bv=0.6)            # long thin torso
    for k in range(4):                                                      # ribs showing through
        rbox((3.05, 0.2, 0.22), (0, -0.85, 1.6 + 0.8 * k), dark, chest, bv=0.06)
    neck = _joint(name + ".neck", (0, 0, 5.2), chest)
    rbox((0.9, 0.9, 1.6), (0, 0, 0.6), skin_m, neck, bv=0.3)
    head = _joint(name + ".head", (0, 0, 1.3), neck)
    blob((1.9, 1.6, 1.9), (0, 0, 1.5), skin_m, head)                         # big round head
    for sx in (-1, 1):                                                       # glowing eyes in dark sockets
        blob((0.55, 0.25, 0.42), (sx * 0.75, -1.4, 2.1), dark, head)
        blob((0.34, 0.16, 0.26), (sx * 0.75, -1.55, 2.1), _glow(eyes, 4.0), head)
    rbox((2.4, 0.3, 0.8), (0, -1.45, 1.05), mouth, head, bv=0.2)             # the open mouth (inside the jaw)
    for i in range(7):                                                       # upper teeth
        rbox((0.22, 0.2, 0.42), (-0.9 + 0.3 * i, -1.6, 1.3), teeth, head, bv=0.06)
    jaw = _joint(name + ".jaw", (0, -0.4, 0.95), head)
    rbox((2.5, 1.7, 0.55), (0, -0.55, -0.15), skin_m, jaw, bv=0.25)
    for i in range(7):                                                       # lower teeth
        rbox((0.22, 0.2, 0.38), (-0.9 + 0.3 * i, -1.25, 0.18), teeth, jaw, bv=0.06)
    m.update(root=root, hips=hips, chest=chest, neck=neck, head=head, jaw=jaw)
    for side, sx in (("L", 1), ("R", -1)):          # L = the monster's own left (+X when it faces -Y)
        blob((0.72, 0.72, 0.72), (sx * 1.6, 0, 4.6), skin_m, chest)          # a shoulder ball: no gap when it reaches
        sh = _joint(f"{name}.sh{side}", (sx * 1.75, 0, 4.6), chest)
        rbox((0.75, 0.75, 5.4), (0, 0, -2.6), skin_m, sh, bv=0.3)
        blob((0.46, 0.46, 0.46), (0, 0, -5.2), skin_m, sh)                   # elbow ball
        el = _joint(f"{name}.el{side}", (0, 0, -5.2), sh)
        rbox((0.65, 0.65, 5.2), (0, 0, -2.5), skin_m, el, bv=0.28)
        for fx in (-0.25, 0.0, 0.25):                                        # long fingers
            rbox((0.16, 0.16, 1.5), (fx, -0.1, -5.6), dark, el, rot=(10, fx * 40, 0), bv=0.05)
        hp = _joint(f"{name}.hip{side}", (sx * 0.8, 0, 0), hips)
        rbox((0.85, 0.85, 5.4), (0, 0, -2.6), skin_m, hp, bv=0.32)
        blob((0.52, 0.52, 0.52), (0, 0, -5.2), skin_m, hp)                   # knee ball
        kn = _joint(f"{name}.kn{side}", (0, 0, -5.2), hp)
        rbox((0.75, 0.75, 5.0), (0, 0, -2.5), skin_m, kn, bv=0.3)
        rbox((0.95, 1.8, 0.4), (0, -0.4, -5.05), dark, kn, bv=0.15)          # flat feet
        m.update({f"sh{side}": sh, f"el{side}": el, f"hip{side}": hp, f"kn{side}": kn})
    monster_pose(m, PARK, 0)
    return m


def monster_pose(m, loc, yaw, lean=0.0, head=(0.0, 0.0), jaw=0.0, shL=(0, 0), shR=(0, 0), elL=0.0, elR=0.0,
                 hipL=0.0, hipR=0.0, knL=0.0, knR=0.0, bob=0.0, tilt=0.0):
    """Set the monster's whole pose. Angles in degrees: shoulders (forward, outward), elbows and knees bend, hips
    swing forward, lean < 0 = forward, head = (turn, look up), jaw = how far the mouth opens (0-40)."""
    s = m["root"].scale[2]
    m["root"].location = Vector(loc) + Vector((0, 0, bob * s))
    _rot(m["root"], z=yaw)
    _rot(m["chest"], -lean, tilt, 0)
    _rot(m["neck"], -head[1] * 0.5, 0, head[0] * 0.5)
    _rot(m["head"], -head[1] * 0.5, 0, head[0] * 0.5)
    _rot(m["jaw"], jaw)                                 # the front of the jaw drops
    for side, sx, (fw, out), el in (("L", 1, shL, elL), ("R", -1, shR, elR)):
        _rot(m["sh" + side], -fw, -sx * out, 0)          # outward: away from the body on both sides
        _rot(m["el" + side], -el)
    for side, hp, kn in (("L", hipL, knL), ("R", hipR, knR)):
        _rot(m["hip" + side], -hp)
        _rot(m["kn" + side], kn)


def monster_stand(m, loc, yaw, T_, ph=0.0):
    """Looming: slow breathing, the head tilting, long arms hanging a little forward."""
    br = math.sin(2 * math.pi * 0.35 * T_ + ph)
    monster_pose(m, loc, yaw, lean=-12 + 2 * br, head=(10 * math.sin(2 * math.pi * 0.2 * T_ + ph), -8),
                 shL=(12 + 3 * br, 10), shR=(12 - 3 * br, 10), elL=18, elR=18, bob=0.1 * br, jaw=6 + 4 * br)


def monster_walk(m, start, yaw, t, speed=3.2, ph=0.0):
    """Heavy, long strides: knees lift, the long arms swing, the body dips on every step and the head bobs."""
    st = 2 * math.pi * 0.55 * t + ph                  # slow steps
    sw = math.sin(st)
    p = Vector(start) + _fwd(yaw) * speed * t * m["root"].scale[2]
    lift = lambda a: max(0.0, math.sin(a)) * 45      # noqa: E731  (the knee bends while that leg swings forward)
    monster_pose(m, tuple(p), yaw + 4 * sw, lean=-14, head=(6 * sw, -6 + 4 * abs(sw)),
                 shL=(-28 * sw, 12), shR=(28 * sw, 12), elL=25 + 10 * sw, elR=25 - 10 * sw,
                 hipL=30 * sw, hipR=-30 * sw, knL=lift(st + math.pi / 2), knR=lift(st - math.pi / 2),
                 bob=-0.45 * abs(math.sin(st)), tilt=5 * sw, jaw=10 + 6 * abs(sw))


def monster_reach(m, loc, yaw, k, T_):
    """Leans in and reaches one long arm out toward the camera (k 0 -> 1), fingers spread, jaw half open."""
    k = _sm(k)
    br = math.sin(2 * math.pi * 0.5 * T_)
    monster_pose(m, loc, yaw, lean=-14 - 26 * k, head=(0, -10 + 18 * k), shL=(10 + 95 * k, 12 - 6 * k),
                 shR=(10 + 8 * br, 14), elL=20 * (1 - k), elR=22, hipL=10 * k, hipR=-6 * k, knL=8 * k,
                 jaw=8 + 22 * k, bob=-0.3 * k)


def monster_roar(m, loc, yaw, k, T_):
    """The roar (k 0 -> 1): leans in, chin up a little, the jaw wide open, arms up and forward with the claws out,
    the whole body shaking."""
    k = _sm(k)
    shake = math.sin(T_ * 47) * 3 * k
    monster_pose(m, loc, yaw, lean=-10 * k + shake * 0.3, head=(shake, 12 * k), jaw=6 + 30 * k,
                 shL=(15 + 75 * k, 15 + 35 * k), shR=(15 + 75 * k, 15 + 35 * k), elL=20 + 55 * k, elR=20 + 55 * k,
                 tilt=shake * 0.5, hipL=-6 * k, hipR=8 * k, knL=6 * k, knR=10 * k, bob=-0.2 * k)


# ---------------------------------------------------------------- animals
def _eyes(parent, x, y, z, r=0.28, gap=0.42):
    white, black = plastic("#FFFFFF", 0.3), plastic("#111114", 0.3)
    for sx in (-1, 1):
        blob((r, r * 0.6, r), (x + sx * gap, y, z), white, parent)
        blob((r * 0.55, r * 0.4, r * 0.55), (x + sx * gap, y - r * 0.45, z - r * 0.1), black, parent)
        blob((r * 0.16, r * 0.1, r * 0.16), (x + sx * gap + r * 0.15, y - r * 0.75, z + r * 0.12),
             plastic("#FFFFFF", 0.2), parent)


def penguin(name="Penguin", scale=1.0):
    """A chubby blocky penguin (about 3 studs tall): black back, white belly, orange beak and feet, flippers."""
    blk, wht, org = plastic("#1C1F2A", 0.4), plastic("#F7F7F2", 0.45), plastic("#FF9A1F", 0.4)
    r = T.empty(name, PARK)
    r.scale = (scale, scale, scale)
    _register(r)
    body = T.empty(name + ".body", (0, 0, 0.35), r)
    rbox((1.9, 1.7, 2.4), (0, 0, 1.2), blk, body, bv=0.7)
    rbox((1.4, 0.3, 1.9), (0, -0.78, 1.05), wht, body, bv=0.5)
    _eyes(body, 0, -0.75, 2.0, r=0.24, gap=0.38)
    rbox((0.5, 0.6, 0.28), (0, -1.0, 1.6), org, body, bv=0.1)
    fl = []
    for sx in (-1, 1):
        f = T.empty(f"{name}.fl{sx}", (sx * 0.95, 0, 1.9), body)
        rbox((0.25, 0.9, 1.4), (0, 0, -0.65), blk, f, bv=0.12)
        fl.append(f)
        rbox((0.6, 0.9, 0.25), (sx * 0.4, -0.35, 0.12), org, r, bv=0.1)           # feet
    return {"name": name, "root": r, "body": body, "flippers": fl}


def waddle(p, start, yaw, t, speed=1.6, ph=0.0):
    """Waddles forward: rocks side to side on each step, flippers flapping."""
    st = 2 * math.pi * 2.0 * t + ph
    p["root"].location = Vector(start) + _fwd(yaw) * speed * t * p["root"].scale[2]
    _rot(p["root"], z=yaw)
    _rot(p["body"], 0, 14 * math.sin(st), 0)
    p["body"].location.z = 0.35 + 0.12 * abs(math.sin(st))
    for i, f in enumerate(p["flippers"]):
        _rot(f, 0, (-1 if i else 1) * (20 + 18 * math.sin(st * 1.5)), 0)   # out from the body


def frog(name="Frog", scale=1.0, colour="#4CC94A"):
    """A round blocky frog (about 2 studs): big eyes on top, a wide smile, folded back legs."""
    g, light = plastic(colour, 0.4), plastic("#BFF07A", 0.45)
    r = T.empty(name, PARK)
    r.scale = (scale, scale, scale)
    _register(r)
    body = T.empty(name + ".body", (0, 0, 0), r)
    rbox((2.2, 2.0, 1.3), (0, 0, 0.75), g, body, bv=0.55)
    rbox((1.6, 0.3, 0.8), (0, -0.9, 0.6), light, body, bv=0.3)
    for sx in (-1, 1):
        blob((0.42, 0.42, 0.42), (sx * 0.55, -0.45, 1.5), g, body)
    _eyes(body, 0, -0.75, 1.55, r=0.3, gap=0.55)
    rbox((1.1, 0.1, 0.09), (0, -1.02, 0.95), plastic("#1E5A22", 0.4), body, bv=0.03)   # the smile
    legs = []
    for sx in (-1, 1):
        lg = T.empty(f"{name}.leg{sx}", (sx * 1.0, 0.55, 0.55), body)          # big folded back legs
        blob((0.42, 0.75, 0.42), (sx * 0.12, 0.05, 0.0), g, lg)
        rbox((0.42, 1.1, 0.34), (sx * 0.12, -0.35, -0.38), g, lg, bv=0.15)
        rbox((0.75, 0.75, 0.16), (sx * 0.15, -0.95, -0.5), light, lg, bv=0.06)   # webbed feet
        legs.append(lg)
        rbox((0.3, 0.3, 0.7), (sx * 0.7, -0.75, 0.25), g, body, bv=0.12)       # front legs
        rbox((0.5, 0.45, 0.14), (sx * 0.75, -0.9, -0.05), light, body, bv=0.05)
    return {"name": name, "root": r, "body": body, "legs": legs}


def hop(f, start, yaw, t, every=0.7, dist=2.2, height=1.6, ph=0.0):
    """Hops forward: one arc every `every` seconds, legs stretching out in the air."""
    x = max(0.0, t / every + ph)
    n, u = math.floor(x), x - math.floor(x)
    s = f["root"].scale[2]
    air = u < 0.55
    a = u / 0.55 if air else 1.0
    f["root"].location = (Vector(start) + _fwd(yaw) * dist * s * (n + _sm(a)) +
                          Vector((0, 0, height * s * math.sin(math.pi * a) if air else 0.0)))
    _rot(f["root"], z=yaw)
    _rot(f["body"], -18 * math.sin(math.pi * a) if air else 0, 0, 0)
    sq = 1 + (0.18 * math.sin(math.pi * a) if air else -0.14 * math.sin(math.pi * min(1.0, (u - 0.55) / 0.45)))
    f["body"].scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq)                 # stretch in the air, squash on landing
    for lg in f["legs"]:
        _rot(lg, 55 * math.sin(math.pi * a) if air else 0, 0, 0)


def lion(name="Lion", scale=1.0):
    """A blocky lion (about 4 studs long): tan body on four legs, a big round brown mane, a tuft on the tail."""
    tan, mane, dark = plastic("#E8B04E", 0.45), plastic("#9A5323", 0.55), plastic("#3A2416", 0.4)
    r = T.empty(name, PARK)
    r.scale = (scale, scale, scale)
    _register(r)
    body = T.empty(name + ".body", (0, 0, 1.6), r)
    rbox((2.0, 3.6, 1.6), (0, 0.3, 0.2), tan, body, bv=0.5)
    head = T.empty(name + ".head", (0, -1.7, 0.9), body)
    for i in range(12):                                                          # a chunky mane, block by block
        a = i / 12 * 2 * math.pi
        rbox((0.75, 0.9, 0.75), (1.3 * math.cos(a), 0.3, 0.2 + 1.3 * math.sin(a)), mane, head,
             rot=(0, -math.degrees(a), 0), bv=0.2)
    blob((1.2, 0.6, 1.2), (0, 0.45, 0.25), mane, head)
    rbox((1.5, 1.2, 1.3), (0, -0.4, 0.2), tan, head, bv=0.45)
    rbox((0.8, 0.5, 0.55), (0, -1.05, -0.05), plastic("#F4D9A0", 0.5), head, bv=0.2)
    rbox((0.36, 0.2, 0.22), (0, -1.32, 0.12), dark, head, bv=0.08)
    _eyes(head, 0, -1.0, 0.6, r=0.2, gap=0.36)
    for sx in (-1, 1):
        blob((0.25, 0.2, 0.25), (sx * 0.65, -0.1, 0.95), tan, head)                 # ears
    legs = []
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        lg = T.empty(f"{name}.leg", (sx * 0.65, 0.3 + sy * 1.2, -0.4), body)
        rbox((0.55, 0.6, 1.4), (0, 0, -0.55), tan, lg, bv=0.18)
        rbox((0.62, 0.75, 0.3), (0, -0.08, -1.15), plastic("#F4D9A0", 0.5), lg, bv=0.1)
        legs.append(lg)
    tail = T.empty(name + ".tail", (0, 2.1, 0.5), body)
    rbox((0.2, 0.2, 1.6), (0, 0.3, 0.6), tan, tail, rot=(-30, 0, 0), bv=0.06)
    blob((0.3, 0.3, 0.3), (0, 0.7, 1.35), mane, tail)
    return {"name": name, "root": r, "body": body, "head": head, "legs": legs, "tail": tail}


def trot(l, start, yaw, t, speed=4.0, ph=0.0):
    """A bouncy trot: diagonal legs together, the body bobbing, the head nodding, the tail swishing."""
    st = 2 * math.pi * 2.4 * t + ph
    s = l["root"].scale[2]
    l["root"].location = Vector(start) + _fwd(yaw) * speed * t * s
    _rot(l["root"], z=yaw)
    l["body"].location.z = 1.6 + 0.18 * abs(math.sin(st))
    _rot(l["body"], 3 * math.sin(st), 0, 0)
    _rot(l["head"], 6 * math.sin(st + 0.6), 0, 0)
    for i, lg in enumerate(l["legs"]):
        side = 1 if i in (0, 3) else -1                                           # diagonal pairs
        _rot(lg, 30 * side * math.sin(st), 0, 0)
    _rot(l["tail"], 0, 25 * math.sin(st * 0.5), 0)


def swarm(make, n, **kw):
    """n copies of an animal (e.g. swarm(penguin, 40)), each its own object, parked until posed."""
    return [make(name=f"{make.__name__.title()}{i}", **kw) for i in range(n)]
