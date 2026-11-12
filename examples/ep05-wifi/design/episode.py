"""ep05 design sheet (gate 4): every new piece next to the cast, before any shot is written. Stills only:

    blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep05-wifi/design stills
"""
from anim import *
from roblox import rule_sign
from rprops import bars, big_phone, hivis, phone_in_hand, pigeon, poster, sash, top_hat, wifi_tower

build_town("BE NICE", ("SIGNAL SHOP", "NICE CAFE"), style="roblox")
wifi_tower(0, 140)
rule_sign(7.5, 104, "BE NICE", "THE TOWER IS WATCHING", yaw=-8)
poster(0, 134, 13.0, face="angry", skin="#C98A5A", cap="#2B62D9")
REPAIR = character("Repairman", "#D9A27A", "#FF7A1A", "#2F4B7C", "cap", "#FFD21F", seed=7)
hivis(REPAIR)
sash(DAD); top_hat(DAD)
for c in (BOY, GRAN, MAN):
    phone_in_hand(c)
PIGEON = pigeon(14.5, 60, yaw=-30)
B0, B4, B4b, B0m = bars(0, x_mark=True), bars(4), bars(4), bars(0, x_mark=True)
big_phone(0, -40, 8, lines=("Searching...",), bars_on=0)


def tower(t, d, T):                      # the landmark, the sign and the poster, with a person for scale
    stand(MAN, (-4.5, 98, ROAD), 0, "smile", T)
    shot((-9, 66, 3.2), (-1, 140, 27), 54)


def cast1(t, d, T):                      # the hero with zero bars, Gran with full bars
    stand(BOY, (-1.2, 60, ROAD), 10, "sad", T, armR=(72, -8), head=(-8, -14))
    stand(GRAN, (2.6, 63, ROAD), -10, "happy", T, ph=1)
    shot((0.4, 46, 4.4), (0.6, 61, 3.6), 34)
    put(B0, over(BOY, 0.4), 0.55); put(B4, over(GRAN, 0.4), 0.55)


def mayor(t, d, T):
    stand(DAD, (0, 60, ROAD), 0, "smug", T, armR=(10, 140), head=(0, 8))
    shot((0.3, 49, 4.4), (0, 60, 3.9), 36)
    put(B4b, over(DAD, 1.5), 0.55)


def cast2(t, d, T):                      # the repairman, the man punished first, the pigeon
    stand(REPAIR, (-2.4, 60, ROAD), 0, "laugh", T)
    stand(MAN, (2.0, 60, ROAD), 0, "shock", T, armR=(72, -8), head=(-8, -14), ph=1)
    PIGEON.location = (0.0, 57.5, ROAD)
    shot((0, 43, 4.0), (0, 60, 3.6), 36)
    put(B0m, over(MAN, 0.5), 0.6)


def phone(t, d, T):                      # a phone-screen insert
    shot((0.6, -54, 8.4), (0, -40, 8), 42)


run([("tower", 0.0, tower), ("cast1", 1.0, cast1), ("mayor", 2.0, mayor), ("cast2", 3.0, cast2),
     ("phone", 4.0, phone)], end=5.0, tod="sun")
