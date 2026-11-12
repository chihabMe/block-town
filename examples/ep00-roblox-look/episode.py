"""Roblox-look demo: a curfew town in the rain. Five shots, about 8 seconds.

The pattern for an episode in the Roblox look (docs/ROBLOX_LOOK.md):
  * build_town(..., style="roblox")             the cast, the street and every prop turn into the new look
  * one landmark that IS the rule, plus the rule sign, both on screen in the first two seconds
  * run(SHOTS, tod="rain")                       the mood: "sun", "fog", "rain", "dusk" or "night"

    blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep00-roblox-look check
    blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep00-roblox-look stills
"""
import math

from anim import *
from roblox import giant_clock, puddles, rule_sign

build_town("HOME BY 8", ("CLOCK SHOP", "EARLY BIRD"), clock="7:59", style="roblox")
giant_clock(2, 64, hours=7, minutes=59)
rule_sign(1.6, 30, "CURFEW 8 PM", yaw=8)
puddles([(-3, 16, 3.2), (2.5, 22, 2.4), (-8, 30, 2.8), (6, 34, 3.6), (-1, 52, 4.0)])
NIA_AT = (-5.7, 11.2, ROAD)


def wide(t, d, T):                      # "In this town," : the street, the clock in the fog
    stand(GRAN, (-9.5, 36, ROAD), 200, "stern", T)
    shot((-4.6, 0.6 + t * 1.6, 2.4 + t * 0.4), (-3.6, 33.0, 12.2), 60)


def sign(t, d, T):                      # "nobody goes out after eight." : the rule sign, a man hurrying past
    sw = math.sin(2 * math.pi * 2.6 * T)
    pose(MAN, (-6.5 + t * 8.0, 33.0, ROAD + abs(sw) * 0.2), 90, "scared",
         armL=(60 * sw, 10), armR=(-60 * sw, 10), legL=-50 * sw, legR=50 * sw, lean=-10, head=(-35, 4))
    shot((0.2 + t * 0.3, 14.5 + t * 0.8, 4.6), (1.6, 30.0, 6.0), 52)


def clock(t, d, T):                     # "When the giant clock rings," : low angle, a shake on "rings"
    hit = clamp((T - WT[widx("rings")]) / 0.6)
    shake = (1 - hit) * 0.35 if T >= WT[widx("rings")] else 0.0
    j = Vector((math.sin(T * 61) * shake, 0, math.cos(T * 47) * shake))
    shot(Vector((-3.0, 36.0 - t * 1.5, 1.6)) + j, (2.0, 64.0, 23.0), 56)


def doors(t, d, T):                     # "every door slams shut." : everyone runs home, toward the camera
    for i, (c, x, y0, ph) in enumerate(((DAD, -16.0, 46, 0.0), (KID, -17.5, 42, 1.3), (TALL, -15.2, 52, 2.1),
                                         (TEACH, -18.0, 57, 0.7))):
        walk(c, x, y0, -1, T - WT[widx("every")], "scared", ph=ph, speed=7.5)
    shot((-11.0, 24.0 - t * 1.2, 4.2), (-16.5, 44.0, 3.6), 46)


def nia(t, d, T):                       # "Tonight, Nia is still outside." : close on Nia, alone in the rain
    k = snap(T, WT[widx("still")])
    stand(NIA, NIA_AT, 24, "scared" if k > 0 else "sad", T, armL=(18, mix(14, 30, k)), armR=(6, mix(8, 26, k)),
          head=(mix(26, 10, k), 14))
    push = t * 0.5
    shot((-3.3 - push * 0.4, 5.4 + push, 5.1), (-5.6, 11.2, 4.5), 34, side=0.7, key_w=220)


SHOTS = [
    ("wide", 0.0, wide),
    ("sign", cut("nobody"), sign),
    ("clock", cut("When"), clock),
    ("doors", cut("every"), doors),
    ("nia", cut("Tonight,"), nia),
]
run(SHOTS, tod="rain")
