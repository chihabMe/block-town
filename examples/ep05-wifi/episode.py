"""Worked example: "In this world, your Wi-Fi gets stronger the nicer you are." Roblox look, sunny, 42 shots, 61 s.

Made through all seven gates of SKILL.md. Read it with docs/ROBLOX_LOOK.md:
  * the set: a landmark that IS the rule (the Wi-Fi tower) + the official sign, on screen in the first 2 s
  * tags that show the rule on people (signal bars, "4K", "FROZEN: 3 DAYS"), popping on the spoken word
  * phone-screen inserts, a poster that goes up mid-story, a dusk flashback

    blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep05-wifi check
"""
from anim import *
from props import car
from roblox import rule_sign
from rprops import (bar_token, bars, beam, big_phone, bus, door, hand_box, hivis, phone_in_hand, pigeon, poster, sash, top_hat,
                    wifi_tower)

build_town("BE NICE", ("SIGNAL SHOP", "NICE CAFE"), style="roblox")

# ---------------------------------------------------------------- the set
wifi_tower(0, 140)
rule_sign(7.5, 104, "BE NICE", "THE TOWER IS WATCHING", yaw=-8)
POSTER = poster(0, 134, 13.0, face="angry", skin="#C98A5A", cap="#2B62D9")      # Max's face, on the tower legs
PIGEON = pigeon(14.5, 60, yaw=-30)
car(5.0, 44.0, col="#2B62D9")
bus(5.5, -24.0)                                     # far from the tower: a bus in its sight lines hides it
DOOR = door(26.6, 28.2, 0.0, yaw=90)                # on the SIGNAL SHOP's door

# ---------------------------------------------------------------- the people
MAX = BOY                                           # the hero
sash(DAD); top_hat(DAD)                             # the mayor
REPAIR = character("Repairman", "#D9A27A", "#FF7A1A", "#2F4B7C", "cap", "#FFD21F", seed=7)
hivis(REPAIR)
BABY = character("Baby", "#EDB78F", "#FFFFFF", "#9AD0FF", "curl", "brown", shoes="#EDB78F", scale=0.45)
DRIVER = character("Driver", "#E4B58A", "#2F55A8", "#22222A", "cap", "#1F3A7A", seed=9)
for c in (BOY, GRAN, MAN, TEACH, TALL, BABY, REPAIR):
    phone_in_hand(c)
LUNCH = hand_box(MAX)
BEAM = beam()

# phone inserts, far from the street
PH_SEARCH = big_phone(0, -380, 8, screen="search")        # pictures from pictures.json
PH_CALL = big_phone(40, -380, 8, screen="call")
PH_SIGNAL = big_phone(80, -380, 8, screen="signal", spinner=False)
PH_HEARTS = big_phone(120, -380, 8, screen="hearts", spinner=False)

# ---------------------------------------------------------------- tags and bubbles
BX, BXman = bars(0, x_mark=True), bars(0, x_mark=True)
B4 = [bars(4) for _ in range(7)]
B1 = bars(1)
B3, B2 = bars(3), bars(2)                             # the countdown on Max's tag in s34
TOKENS = [bar_token(i) for i in range(4)]             # his bars flying away in s34
T4K = card(["4K"], 1.1, "#FFD84A")
TLOAD = card(["LOADING...", "10 MIN"], 0.55, "#FF5A4F")
TMBPS = card(["1000 Mbps"], 0.42, "#3BE37E")
TQ = card(["?"], 0.9, "#FFD84A")
TMAX = card(["MAX"], 0.7, "#FFFFFF")
TFROZEN = card(["FROZEN:", "3 DAYS"], 0.5, "#7FE3FF")
TFAIL = card(["CALL FAILED"], 0.55, "#FF3B30")
TDOORS = card(["DOORS HELD: 50"], 0.5, "#FFD84A")
TLUNCH = card(["LUNCHES: 30"], 0.5, "#FFD84A")
T312 = card(["312 PHONES"], 1.4, "#3BE37E")
TAGE = card(["AGE 6"], 0.55, "#FFD84A")
BMOVE = card(["MOVE IT,", "GRANDMA!"], 0.5, bubble=True)
BSORRY = card(["SORRY!"], 0.55, bubble=True)
BGIVE = card(["GIVE MY WI-FI", "TO GRANDMA!"], 0.42, bubble=True)
BAFTER = card(["AFTER YOU!"], 0.5, bubble=True)
HEARTS = [card(["♥"], 0.7, "#FF3B6B") for _ in range(10)]
HIDE = (0.001, 0.001, 0.001)
FLASHBACK = (wcut(211), wcut(226))                  # "When I was six ... Give my Wi-Fi to Grandma."


@before_each_frame
def reset(T):
    """Every frame starts from the same state; shots then change only what they need."""
    up = WT[161] <= T and not FLASHBACK[0] <= T < FLASHBACK[1]      # the poster goes up on word 161 ("face")
    POSTER.scale = (1, 1, 1) if up else HIDE
    LUNCH.scale, BEAM.scale = HIDE, HIDE
    DOOR.rotation_euler.z = math.radians(90)
    PIGEON.location = (14.5, 60, WALK)


def front(c, dist=7.0, fov=34, side=0.9, rise=0.4, push=0.0, t=0.0):
    """A face shot from in front of c, pushing in by push studs per second. With a tag above the head use
    dist about 9.5 and fov 46, or the tag is out of frame."""
    closeup(c, dist=max(2.5, dist - push * t), fov=fov, side=side, rise=rise)


# ---------------------------------------------------------------- the rule
def s01(t, d, T):   # In this world,
    shot((0, -20 + t * 5, 30 - t * 2), (0, 140, 30), 48)


def s02(t, d, T):   # your Wi-Fi gets stronger
    shot((-7 + t, 117 + t * 2.5, 45), (0, 139, 52.5), 40)


def s03(t, d, T):   # the nicer you are.
    stand(GRAN, (LX, 36, WALK), 90, "happy", T, armR=(12, 138 + osc(T, 2.5, 18)))
    front(GRAN, 8.5, 36, push=1.2, t=t)
    put(B4[0], over(GRAN, 0.4), 0.55 * wpop(8))


def s04(t, d, T):   # You see, every phone
    # Wide enough for the whole BE NICE sign (a 10.6-stud board needs ~25 studs of distance in a 9:16 frame),
    # with the kid in front of it pointing up at it.
    stand(KID, (5.6, 97.2, ROAD), -20, "smile", T, armR=(150, 18), head=(0, 12))
    shot((1.4 + t * 0.3, 78.5 + t * 1.0, 4.2), (6.8, 104, 7.2), 50)


def s05(t, d, T):   # listens to the giant tower.
    shot((-11 + t * 1.5, 110, 1.4), (0, 140, 38), 62)


def s06(t, d, T):   # Nice people stream movies in 4K.
    stand(TEACH, (LX, 52, WALK), 90, "happy", T, armR=(72, -8), head=(-6, -12))
    front(TEACH, 9.5, 46, push=0.8, t=t)
    put(B4[0], over(TEACH, 0.3), 0.5)
    put(T4K, over(TEACH, 1.5), wpop(25))


def s07(t, d, T):   # Rude people wait ten minutes for one picture.
    stand(TALL, (RX, 70, WALK), -90, "angry", T, armR=(72, -8), head=(6, -12), tilt=4)
    front(TALL, 9.5, 46, side=-0.9, push=0.6, t=t)
    put(B1, over(TALL, 0.5), 0.5)
    put(TLOAD, over(TALL, 1.7), wpop(29))


def s08(t, d, T):   # Babies have the fastest internet in town,
    stand(BABY, (LX, 64, WALK), 90, "happy", T, armR=(72, -8), head=(0, -10))
    e = eyes(BABY)
    shot((LX + 5.0 - t * 0.4, 62.4, 2.8), e + Vector((0, 0, 0.3)), 44)
    put(B4[1], over(BABY, 0.2), 0.35)
    put(TMBPS, over(BABY, 0.85), wpop(37))


def s09(t, d, T):   # and they can't even read.
    stand(BABY, (LX, 64, WALK), 90, "shock", T, armR=(150, -6), head=(4, 18))
    e = eyes(BABY)
    shot((LX + 2.6, 63.3, 2.4), e + Vector((0, 0, 0.15)), 36)
    put(TQ, over(BABY, 0.4), wpop(44))


def s10(t, d, T):   # So everybody here is nice.
    for i, c in enumerate((NIA, TEACH, KID, TALL, GRAN)):
        stand(c, (LX + (i % 2) * 1.2, 22 + i * 3.0, WALK), 90, "happy", T, ph=i,
              armR=(12, 136 + osc(T, 2.5, 18, i)))
    shot((-3 + t, 18.5, 5.5), (LX, 28.5, 4.0), 50)


def s11(t, d, T):   # Nobody honks.
    k = clamp((T - wcut(51)) / 0.9)
    walk(KID, 0, 0, 1, T, "happy", z=ROAD)
    pose(KID, (9.0 - 11 * smooth(k), 52.5, ROAD), -90, "happy", armL=(30 * math.sin(T * 9), 6),
         armR=(-30 * math.sin(T * 9), 6), legL=-30 * math.sin(T * 9), legR=30 * math.sin(T * 9))
    put(B4[0], over(KID, 0.4), 0.45)
    shot((-6.5, 62, 3.4), (2.5, 50, 2.4), 50)


def s12(t, d, T):   # Nobody cuts in line.
    for i, c in enumerate((NIA, MAN, GRAN)):
        stand(c, (-21.5, 84 + i * 2.6, 0.0), 180, "smile", T, ph=i)
    stand(TALL, (-19.6, 94.2, 0.0), -90, "happy", T, armR=(40, 70), head=(20, 0))
    put(BAFTER, over(TALL, 0.5), wpop(54))
    shot((-10.5, 82 + t * 0.6, 5.4), (-19.6, 90, 4.3), 48)


def s13(t, d, T):   # Not even the bus driver.
    stand(DRIVER, (11.6, -35.8, ROAD), 0, "laugh", T, armR=(12, 136 + osc(T, 2.6, 20)))
    put(BAFTER, over(DRIVER, 0.5), wpop(60))
    shot((10.6 + t * 0.4, -48.5, 4.8), (10.8, -35.6, 5.2), 46)


# ---------------------------------------------------------------- punished first
def s14(t, d, T):   # Last week, one man yelled at a grandma.
    k = wpop(66)
    stand(MAN, (LX, 69, WALK), 0, "angry" if k > 0 else "stern", T, armR=(mix(10, 88, k), 6), lean=mix(0, -8, k))
    stand(GRAN, (LX, 65.6, WALK), 180, "scared" if k > 0 else "smile", T, lean=mix(0, 6, k))
    put(BMOVE, over(MAN, 0.9), k)
    shot((-5.5, 67.3 - t * 0.3, 5.6), (LX, 67.3, 4.8), 50)


def s15(t, d, T):   # His phone froze for three whole days.
    stand(MAN, (LX, 69, WALK), 0, "shock", T, armR=(72, -8), head=(0, -10))
    front(MAN, 9.5, 46, push=0.7, t=t)
    put(BXman, over(MAN, 0.3), 0.5 * wpop(71))
    put(TFROZEN, over(MAN, 1.5), wpop(74))


# ---------------------------------------------------------------- Max
MAX_AT = (RX, 36, WALK)


def s16(t, d, T):   # My name is Max, and I have zero bars.
    stand(MAX, MAX_AT, 0, "smile" if T < WT[84] else "sad", T)
    front(MAX, 9.5, 46, push=0.9, t=t)
    put(TMAX, over(MAX, 1.5), wpop(80))
    put(BX, over(MAX, 0.4), 0.55 * wpop(84))


def s17(t, d, T):   # My phone only ever says one word: Searching.
    shot((0.3, -398 + t * 1.2, 8.3), (0, -380, 8), 42)


def s18(t, d, T):   # Everyone thinks I'm the meanest kid in town.
    walk(MAX, RX, 50, -1, t, "sad")
    for c, y, ph in ((TALL, 41, 0), (NIA, 44.5, 1)):
        stand(c, (RX + 3.4, y, 0.0), -70, "angry", T, ph=ph, armR=(88, 10))
    put(BX, over(MAX, 0.4), 0.55)
    shot((RX - 3.5, 33, 4.6), (RX + 1, 45, 3.8), 50)


def s19(t, d, T):   # And the worst part?
    stand(MAX, MAX_AT, 0, "sad", T, head=(0, -6))
    front(MAX, 6.0, 30, push=2.2, t=t)


def s20(t, d, T):   # My grandma lives alone across the street.
    stand(MAX, MAX_AT, -90, "sad", T)
    stand(GRAN, (LX, 36, WALK), 90, "sad", T, armR=(10, 120 + osc(T, 1.5, 12)))
    shot((RX + 4.5, 37.5, 5.6), (LX, 36, 3.8), 34)


def s21(t, d, T):   # Her street always has amazing Wi-Fi, though.
    for i, c in enumerate((NIA, TEACH, GRAN, KID)):
        stand(c, (LX - (i % 2) * 1.5, 28 + i * 4.2, WALK), 90, "happy", T, ph=i)
        put(B4[i], over(c, 0.4), 0.5 * wpop(118))
    shot((-3, 24 + t, 6.5), (LX, 36, 4), 46)


def s22(t, d, T):   # But my Sunday video calls
    shot((-0.3 + 40, -397 + t * 1.5, 8.2), (40, -380, 8), 42)


def s23(t, d, T):   # never connect.
    stand(GRAN, (LX, 36, WALK), 90, "sad", T, armR=(72, -8), head=(0, -12))
    front(GRAN, 9.5, 46, push=0.6, t=t)
    put(TFAIL, over(GRAN, 1.4), wpop(126))


def s24(t, d, T):   # So I tried being nicer.
    stand(MAX, MAX_AT, 0, "determined", T, armL=(20, 30), armR=(20, 30), lean=4)
    front(MAX, 7.0, 36, push=1.0, t=t)
    put(BX, over(MAX, 0.4), 0.55)


def s25(t, d, T):   # I held fifty doors. Zero bars.
    DOOR.rotation_euler.z = math.radians(170)
    stand(MAX, (25.0, 33.2, 0.0), -90, "happy", T, armL=(15, 75), head=(-15, 0))
    k = (T - wcut(132)) * 2.2
    for c, off in ((NIA, 0.0), (KID, 1.6)):
        y = 44 - (k - off) * 2.0
        pose(c, (24.4 - 0.3 * (k - off), y, 0.0), 0, "happy", armL=(30 * math.sin(T * 9), 6),
             armR=(-30 * math.sin(T * 9), 6), legL=-30 * math.sin(T * 9), legR=30 * math.sin(T * 9))
    put(TDOORS, over(MAX, 2.0), wpop(134))
    put(BX, over(MAX, 0.4), 0.55 * wpop(136))
    shot((17.0, 35.4, 5.2), (25.0, 32.4, 4.6), 60)


def s26(t, d, T):   # I gave away my lunch for a month. Zero bars.
    LUNCH.scale = (1, 1, 1)
    stand(MAX, (RX, 50, WALK), 0, "happy", T, armR=(80, -4))
    stand(KID, (RX, 46.8, WALK), 180, "laugh", T, armL=(60, 10))
    put(TLUNCH, over(MAX, 1.3), wpop(145))
    put(BX, over(MAX, 0.4), 0.55 * wpop(146))
    shot((7.0, 48.9 + t * 0.4, 4.8), (RX, 49.4, 4.4), 54)


def s27(t, d, T):   # I said sorry to a pigeon. Still zero.
    PIGEON.location = (RX, 63.6, WALK)
    PIGEON.rotation_euler.z = math.radians(180)
    k = wpop(150)
    stand(MAX, (RX, 60.6, WALK), 180, "sad", T, lean=mix(0, -32, k), armL=(mix(0, 20, k), 5), armR=(mix(0, 20, k), 5))
    put(BSORRY, over(MAX, -0.6), k)
    put(BX, over(MAX, 0.4), 0.55 * wpop(154))
    shot((10.5, 67.5, 3.4), (RX, 61.6, 2.8), 58)


# ---------------------------------------------------------------- the cost
def s28(t, d, T):   # Then the mayor put my face on the tower.
    k = wpop(161, 0.2)
    POSTER.scale = (k + 0.001,) * 3
    stand(DAD, (-3.8, 128, ROAD), -15, "smug", T, armL=(150, 25))
    shot((3, 110, 3.2), (0, 133, 11), 56)


def s29(t, d, T):   # Meanest kid in town.
    shot((0.2, 121 + t * 2.0, 13.4), (0, 134, 13.2), 40)


def s30(t, d, T):   # So I walked to the tower to ask why.
    walk(MAX, 0, 98, 1, t, "determined", z=ROAD)
    put(BX, over(MAX, 0.4), 0.55)
    e = MAX["root"].location
    shot((e.x + 1.5, e.y - 9, 3.6), (0, 134, 14), 52)


def s31(t, d, T):   # The repairman checked my phone and laughed.
    k = wpop(184)
    stand(REPAIR, (1.8, 124, ROAD), -20, "laugh" if k > 0 else "smile", T, armR=(72, -8), head=(0, mix(-10, 10, k)),
          lean=mix(0, 5, k))
    stand(MAX, (-1.6, 122.6, ROAD), 30, "sad", T)
    shot((0.6, 114.5, 4.6), (0.2, 123.4, 4.0), 40)


def s32(t, d, T):   # My Wi-Fi wasn't zero.
    stand(MAX, (-1.6, 122.6, ROAD), 0, "shock", T)
    front(MAX, 6.5, 32, push=2.0, t=t)


def s33(t, d, T):   # It was the strongest in town.
    shot((80.3, -398 + t * 1.2, 8.3), (80, -380, 8), 42)


# ---------------------------------------------------------------- the twist
def s34(t, d, T):   # I was just giving every bar away.
    # Show the idea literally: close on Max, his four bars pop out of his tag one by one and fly off toward
    # Grandma's side of the street while the tag counts down 4 -> 3 -> 2 -> 1 -> X. (A long beam between two small
    # figures read as "a blue line" to viewers.)
    stand(MAX, MAX_AT, 0, "shock", T, head=(0, 6))
    front(MAX, 9.5, 46, push=0.7, t=t)
    m = town.cam.rotation_euler.to_matrix()
    right, up = m.col[0], m.col[1]
    tag = over(MAX, 0.45)
    starts = [0.22 + 0.2 * k for k in range(4)]                 # tallest bar leaves first
    gone = sum(1 for s0 in starts if t >= s0)
    put((B4[0], B3, B2, B1, BX)[gone], tag, 0.55)
    for k, s0 in enumerate(starts):
        i = 3 - k
        if t < s0:
            continue
        f = clamp((t - s0) / 0.75)
        e = smooth(f)
        home = tag + right * ((-0.81 + i * 0.54) * 0.55) + up * 0.2
        p = home - right * (6.5 * e) + up * (1.8 * math.sin(e * math.pi * 0.9))
        put(TOKENS[i], p, 0.55 * (1 + 0.5 * e) * (1 - clamp((f - 0.85) / 0.15)))


def s35(t, d, T):   # To Grandma's whole street.
    for i, c in enumerate((NIA, TEACH, GRAN, KID, TALL, MAN, DAD)):
        stand(c, (LX - (i % 2) * 1.6, 20 + i * 5.5, WALK), 90, "happy", T, ph=i)
        put(B4[i], over(c, 1.5 if c is DAD else 0.4), 0.5)
    shot((2 - t, 8, 9 + t), (LX, 40, 3), 50)


def s36(t, d, T):   # Three hundred and twelve phones.
    s35(t, d, T)
    shot((4, -2 - t * 2, 18 + t * 2), (LX, 44, 2), 52)
    fwd = (Vector((LX, 44, 2)) - town.cam.location).normalized()
    put(T312, town.cam.location + fwd * 14 + Vector((0, 0, 1.2)), wpop(206))


def s37(t, d, T):   # When I was six, I told the tower one thing.
    time_of_day("dusk")                             # a flashback: dusk, little Max, no poster yet
    stand(MAX, (0, 120, ROAD), 180, "smile", T, head=(0, 22))
    size(MAX, 0.62)
    put(TAGE, over(MAX, 1.4), wpop(214))
    shot((1.8, 111.5, 2.6), (0, 130, 11), 62)


def s38(t, d, T):   # Give my Wi-Fi to Grandma.
    time_of_day("dusk")
    stand(MAX, (0, 120, ROAD), 180, "happy", T, head=(0, 28), armL=(150, 30), armR=(150, 30))
    size(MAX, 0.62)
    put(BGIVE, over(MAX, 0.9) + Vector((0, 0, 0.6)), wpop(221))
    shot((-2.6, 111.5, 2.6), (0, 124, 5.0), 52)


# ---------------------------------------------------------------- the button
def s39(t, d, T):   # My phone still says Searching.
    shot((0.3, -396 + t * 1.0, 8.3), (0, -380, 8), 42)


def s40(t, d, T):   # But Grandma just sent me
    stand(GRAN, (LX, 36, WALK), 90, "laugh", T, armR=(72, -8), head=(0, -8))
    front(GRAN, 8.0, 38, push=0.8, t=t)
    e = eyes(GRAN)
    for i, h in enumerate(HEARTS):
        k = clamp((T - WT[233] - i * 0.09) / 1.2)
        put(h, e + Vector((1.2 + 0.4 * math.sin(i * 2.1), -0.6 + 0.5 * math.cos(i * 1.7), -1.2 + 4.0 * k)),
            0.0 if k <= 0 else 0.8)


def s41(t, d, T):   # forty-seven heart emojis.
    shot((120.3, -397 + t * 1.8, 8.3), (120, -380, 8), 42)


def s42(t, d, T):   # In 4K.
    stand(MAX, MAX_AT, 0, "laugh", T, armR=(72, -8), head=(0, -6))
    front(MAX, 7.5, 36, push=0.6, t=t)
    put(BX, over(MAX, 0.4), 0.55)
    e = eyes(MAX)
    for i, h in enumerate(HEARTS):
        a = i * 0.63 + T * 0.8
        put(h, e + Vector((math.cos(a) * 1.9, -1.0, math.sin(a) * 1.5 + 0.4)), 0.6)


CUTS = [("s01", 0), ("s02", 3), ("s03", 7), ("s04", 11), ("s05", 15), ("s06", 20), ("s07", 26), ("s08", 34),
        ("s09", 41), ("s10", 46), ("s11", 51), ("s12", 53), ("s13", 57), ("s14", 62), ("s15", 70), ("s16", 77),
        ("s17", 86), ("s18", 94), ("s19", 102), ("s20", 106), ("s21", 113), ("s22", 120), ("s23", 125), ("s24", 127),
        ("s25", 132), ("s26", 138), ("s27", 148), ("s28", 156), ("s29", 165), ("s30", 169), ("s31", 178), ("s32", 185),
        ("s33", 189), ("s34", 195), ("s35", 202), ("s36", 206), ("s37", 211), ("s38", 221), ("s39", 226), ("s40", 231),
        ("s41", 236), ("s42", 239)]
SHOTS = [(n, 0.0 if i == 0 else wcut(i), globals()[n]) for n, i in CUTS]     # (name, start, function)
run(SHOTS, tod="sun")
