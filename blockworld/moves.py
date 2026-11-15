"""The movement pack (viral pack, Nov 2026): big, clear, cartoon moves for our blocky characters, in the same
pose-to-pose style as walk / sprint / cheer (the user preferred these over motion capture: they read at phone size).

Every move takes the shot's time and poses one character for this frame; call it inside a shot function.
`from anim import *` brings them all in.

    dance(c, loc, yaw, face, T, style="bop")    looping dances: "bop", "robot", "disco"; bpm sets the tempo
    big_jump(c, loc, yaw, face, t)              crouch, leap with arms up, land (t = seconds since the jump began)
    panic(c, loc, yaw, face, T)                 hands on the head, head whipping left-right, running on the spot
    knock(c, loc, yaw, face, T)                 knocks on a door in front of them
    point(c, loc, face, at, T)                  turns to and points at a world point `at` (x, y, z)
    hug(a, b, mid, yaw, k, T)                   a side hug: step in, inner arms round each other (k 0 -> 1)
    float_up(c, loc, yaw, face, k, T)           rises into the sky, legs dangling, arms flapping (k 0 -> 1)
    sink(c, loc, yaw, face, k, T)               sinks through the ground, arms up (k 0 -> 1)
    tumble(c, centre, face, T)                  spins head over heels around a point (falling through a void)
    run_pose(c, loc, yaw, face, T)              the sprint's arms and legs without moving (for crowds, chases)
    crowd_run(people, start, yaw, t)            a crowd sprinting together in a loose pack
"""
import math
import random

from mathutils import Euler, Vector

import town
from town import pose

# NOTE on pose() arms: "out" (the second number) spreads a HANGING arm away from the body, but once the arm is raised
# past the shoulder (forward > 90) the same angle swings it in, over the head. Raised arms use a negative out to stay
# clear of the head (found Nov 14 after agy kept seeing hands inside heads).
__all__ = ["dance", "big_jump", "panic", "knock", "point", "hug", "float_up", "sink", "tumble", "run_pose",
           "crowd_run"]


def _osc(T, hz, amp, ph=0.0):
    return amp * math.sin(2 * math.pi * hz * T + ph)


def _clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def _smooth(x):
    x = _clamp(x)
    return x * x * (3 - 2 * x)


def _fwd(yaw):
    a = math.radians(yaw)
    return Vector((math.sin(a), -math.cos(a), 0.0))


def _right(yaw):
    f = _fwd(yaw)
    return Vector((f.y, -f.x, 0.0))          # the character's own right (the armL side)


def _s(c):
    return c["root"].scale[2]


# ---------------------------------------------------------------- dances
def dance(c, loc, yaw, face, T, style="bop", bpm=120, ph=0.0):
    """A looping dance on the spot. style: "bop" (side steps, arms pumping up in turn), "robot" (stiff poses that snap
    on each beat), "disco" (one arm points up high, then down across the body). No floss: with straight arms it
    crosses through the body (agy review, Nov 14).
    Give each dancer a different ph so a group doesn't move like clones."""
    b = T * bpm / 60.0 + ph                      # beats
    s = _s(c)
    r = _right(yaw)
    if style == "bop":
        sw = math.sin(math.pi * b)               # one side step per beat
        up = abs(sw)
        p = Vector(loc) + r * (0.35 * sw * s) + Vector((0, 0, 0.3 * up * s))
        pose(c, tuple(p), yaw + 8 * sw, face,
             armL=(20 + 150 * max(0.0, sw), 35 - 60 * max(0.0, sw)), armR=(20 + 150 * max(0.0, -sw), 35 - 60 * max(0.0, -sw)),
             legL=35 * max(0.0, sw), legR=35 * max(0.0, -sw), head=(14 * sw, 10 * math.sin(2 * math.pi * b)),
             tilt=-14 * sw, lean=-4)
    elif style == "robot":
        n = int(math.floor(b)) % 4               # four stiff poses, snapping on each beat
        u = _smooth((b % 1.0) / 0.18)
        # side-on shapes read from the front: one arm up and one out, both out flat, one up one down...
        poses = (((175, -18), (15, 85), 25, 0), ((15, 85), (175, -18), -25, 0), ((40, 88), (40, 88), 0, 8),
                 ((172, -28), (172, -28), 0, -8))
        cur, prv = poses[n], poses[(n - 1) % 4]
        lerp = lambda p0, p1: (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)   # noqa: E731
        p = Vector(loc) + Vector((0, 0, 0.08 * abs(math.sin(math.pi * b)) * s))
        pose(c, tuple(p), yaw, face, armL=lerp(prv[0], cur[0]), armR=lerp(prv[1], cur[1]),
             head=(prv[2] + (cur[2] - prv[2]) * u, prv[3] + (cur[3] - prv[3]) * u), legL=6 * (n % 2), legR=6 * (1 - n % 2))
    elif style == "disco":
        k = (math.floor(b) % 2 == 0)             # up on one beat, down across on the next
        u = _smooth((b % 1.0) / 0.35)            # snap into each pose
        aim = lambda a0, a1: a0 + (a1 - a0) * u   # noqa: E731
        armR = (aim(30, 168), aim(10, -32)) if k else (aim(168, 30), aim(-32, 10))
        sway = math.sin(math.pi * b)
        p = Vector(loc) + Vector((0, 0, 0.15 * abs(sway) * s))
        pose(c, tuple(p), yaw - 10, face, armL=(10, 55), armR=armR,
             legL=18 * max(0.0, sway), legR=18 * max(0.0, -sway),
             head=(18 if k else -10, 14 if k else -6), tilt=12 if k else -6, lean=-3)
    else:
        raise ValueError(f"no dance {style!r}: bop, robot, disco")


# ---------------------------------------------------------------- body moves
def big_jump(c, loc, yaw, face, t, height=4.6, dur=1.3):
    """A big cartoon jump: a deep crouch with the arms swung back (anticipation), a high leap with both arms straight
    up and a hang at the top, then a landing squash. t = seconds since it began; after dur it stands still."""
    u = t / dur
    p = Vector(loc)
    if u < 0.3:                                   # crouch: lean far forward, arms swung back
        k = _smooth(u / 0.3)
        pose(c, tuple(p), yaw, face, armL=(-60 * k, 15), armR=(-60 * k, 15), lean=-34 * k, head=(0, 14 * k),
             legL=28 * k, legR=28 * k)
    elif u < 0.82:                                # air: fast up, a hang at the top, down
        a = (u - 0.3) / 0.52
        z = height * math.sin(math.pi * a) ** 0.7 * _s(c)
        pose(c, tuple(p + Vector((0, 0, z))), yaw, face, armL=(168, -32), armR=(168, -32),
             legL=40 * math.sin(math.pi * a), legR=-25 * math.sin(math.pi * a), lean=10, head=(0, 22))
    else:                                         # land and settle
        k = 1 - _smooth(min(1.0, (u - 0.82) / 0.18))
        pose(c, tuple(p), yaw, face, armL=(70 * k, 45 * k + 8), armR=(70 * k, 45 * k + 8), lean=-22 * k,
             legL=18 * k, legR=18 * k)


def panic(c, loc, yaw, face, T, ph=0.0):
    """Total panic: both hands clamped on the head, the head whipping left and right, running on the spot."""
    s = _s(c)
    run = math.sin(2 * math.pi * 4.5 * T + ph)
    p = Vector(loc) + Vector((0, 0, 0.18 * abs(run) * s))
    pose(c, tuple(p), yaw + _osc(T, 1.3, 12, ph), face, armL=(160, -8), armR=(160, -8),     # straight up from the shoulders: beside the head, not in it
         legL=30 * run, legR=-30 * run, head=(_osc(T, 3.0, 32, ph), 6), tilt=_osc(T, 4.5, 6, ph), lean=-6)


def knock(c, loc, yaw, face, T, hz=2.6, ph=0.0, hand="R"):
    """Knock on a door in front of them: a fist jabs forward on each knock, the body leans in a little. Stand them
    about 2.4 studs from the door face (the fist reaches it, the cap brim doesn't). hand="L" knocks with armL; film
    from that side so the knocking arm is in view."""
    j = max(0.0, math.sin(2 * math.pi * hz * T + ph)) ** 2
    knock_arm, other = (92 + 14 * j, 6), (6, 8)
    arms = dict(armR=knock_arm, armL=other) if hand == "R" else dict(armL=knock_arm, armR=other)
    pose(c, loc, yaw, face, lean=-5 - 4 * j, head=(0, -4 + 3 * j), **arms)


def point(c, loc, face, at, T, ph=0.0, other=None):
    """Turn toward a world point and point at it with a straight right arm (up or down as needed). other: the free
    arm's (fwd, out); default hand on the hip."""
    d = Vector(at) - (Vector(loc) + Vector((0, 0, 4.2 * _s(c))))
    yaw = math.degrees(math.atan2(d.x, -d.y))
    elev = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    pose(c, loc, yaw - 8, face, armR=(90 + elev + _osc(T, 1.2, 2, ph), 12), armL=other or (12, 35),
         head=(8, 0.6 * elev), lean=-4)


def hug(a, b, mid, yaw, k, T):
    """A side hug (k 0 -> 1): a and b step in side by side facing yaw (usually the camera), each puts the inner arm
    round the other's back and waves the outer one. A face-to-face hug can't look clean with elbow-less block arms
    (agy review, Nov 14): the arms go through bodies and cap brims hit faces."""
    k = _smooth(k)
    r = _right(yaw)
    gap = (3.8 - 1.05 * k) * _s(a)
    pa = Vector(mid) + r * (gap / 2)                  # a on the right side (the armL side), b on the left
    pb = Vector(mid) - r * (gap / 2)
    wave = _osc(T, 2.6, 20 * k)
    lean = 7 * k
    # a's inner arm is armR (toward b), b's inner arm is armL; inner arms go out and slightly back, behind the other
    pose(a, tuple(pa), yaw - 6 * k, "laugh", armR=(-38 * k, 8 + 72 * k), armL=(40 + 125 * k, 30 - 58 * k + wave),
         tilt=lean, head=(14 * k, 4))
    pose(b, tuple(pb), yaw + 6 * k, "happy", armL=(-30 * k, 8 + 52 * k), armR=(40 + 125 * k, 30 - 58 * k - wave),
         tilt=-lean, head=(-14 * k, 4))


def float_up(c, loc, yaw, face, k, T, height=14.0, spin=60.0):
    """Lifted into the sky (k 0 -> 1): rises with a slow turn, legs dangling, arms flapping for balance."""
    s = _s(c)
    z = height * _smooth(k) * s + _osc(T, 0.8, 0.15 * s) * k
    flap = _osc(T, 2.2, 32)
    pose(c, tuple(Vector(loc) + Vector((0, 0, z))), yaw + spin * k, face, armL=(25 + 25 * k, 70 + flap),
         armR=(25 + 25 * k, 70 - flap), legL=_osc(T, 1.6, 32) * k, legR=_osc(T, 1.6, -28) * k, head=(0, -20 * k),
         lean=6 * k)


def sink(c, loc, yaw, face, k, T, depth=6.5):
    """Sinking through the ground (k 0 -> 1): arms thrown up and flailing, leaning back. The ground hides what's
    below it, so stand them on a solid floor."""
    s = _s(c)
    z = -depth * _smooth(k) * s
    pose(c, tuple(Vector(loc) + Vector((0, 0, z))), yaw, face, armL=(170, -30 + _osc(T, 4, 8)),
         armR=(170, -30 - _osc(T, 4, 8)), lean=10, head=(_osc(T, 2.5, 15), 22), legL=_osc(T, 5, 15),
         legR=_osc(T, 5, -15))


def tumble(c, centre, face, T, rate=0.9, yaw=0.0):
    """Head over heels around a point in the air (falling through a void, thrown by a blast): arms and legs
    flailing. rate = turns per second."""
    s = _s(c)
    pose(c, None, yaw, face, armL=(110 + _osc(T, 3.5, 55), 55 + _osc(T, 2.1, 25)),
         armR=(110 - _osc(T, 3.5, 55), 55 - _osc(T, 2.1, 25)), legL=_osc(T, 2.8, 55), legR=_osc(T, 2.8, -55),
         head=(_osc(T, 1.7, 20), 15))
    rot = Euler((2 * math.pi * rate * T, 0.6 * math.sin(2 * math.pi * 0.4 * T), math.radians(yaw)))
    c["root"].rotation_euler = rot
    c["root"].location = Vector(centre) - rot.to_matrix() @ Vector((0, 0, 2.6 * s))


# ---------------------------------------------------------------- running, crowds
def run_pose(c, loc, yaw, face, T, ph=0.0, hz=3.2):
    """The sprint's limbs at a fixed spot: big arm pumps, a deep lean and a hop. Move loc yourself."""
    sw = math.sin(2 * math.pi * hz * T + ph)
    s = _s(c)
    pose(c, tuple(Vector(loc) + Vector((0, 0, abs(sw) * 0.55 * s))), yaw, face, armL=(80 * sw, 12),
         armR=(-80 * sw, 12), legL=-62 * sw, legR=62 * sw, lean=-20, tilt=5 * sw)


def crowd_run(people, start, yaw, t, face="scared", speed=10.0, width=10.0, depth=12.0, seed=3):
    """A crowd sprinting together in a loose pack: the front row starts at `start`, spread `width` studs across and
    `depth` studs back, each with their own pace and stride (same people, same places every frame)."""
    rng = random.Random(seed)
    f, r = _fwd(yaw), _right(yaw)
    for i, c in enumerate(people):
        ox, oy = rng.uniform(-width / 2, width / 2), rng.uniform(0, depth)
        sp, ph, hz = speed * rng.uniform(0.9, 1.1), rng.uniform(0, 6.28), rng.uniform(2.9, 3.5)
        p = Vector(start) + r * ox - f * oy + f * sp * t
        run_pose(c, p, yaw + rng.uniform(-6, 6), face, t, ph, hz)
