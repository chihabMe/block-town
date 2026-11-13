"""Shared pieces for outdoor places on their own plot (plots 1000 studs apart: a backdrop reaches ~400 studs out):
grass, hills all round, a ring of far-off houses (or towers
downtown), trees and clouds, so each plot looks like another corner of the same town. Kit helpers that place things in
world coordinates (world2.bench, hydrant, bin_, tree2, props.car, rprops.bus, town.lamp) take cx + local x.
"""
import math
import random

import town as T
from world2 import discs, ico, multi, prism, tree2


def cloud_mat():
    m = T.MATS.get("cloud")
    if m is None:
        m = T.mat("#FFFFFF", emit=1.0, key="cloud")
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
    return m


TOWER_GLOW = {"day": 0.0, "sun": 0.0, "fog": 0.4, "rain": 0.4, "dusk": 1.3, "night": 2.6}


def tower_window():
    """Office-tower glass: blue by day, lit yellow at dusk and night (window_glow_hook switches it)."""
    m = T.MATS.get("towerwin")
    if m is None:
        m = T.mat("#8DB7D6", emit=0.0, key="towerwin")
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Color"].default_value = T.lin("#F7CE6E")
        b.inputs["Roughness"].default_value = 0.15
        b.inputs["Specular IOR Level"].default_value = 0.6
        m["plastic"] = True
    return m


def tower_hook():
    """Call from dress(): tower windows follow the time of day."""
    m = tower_window()

    def hook(mode):
        T.emission(m, TOWER_GLOW.get(mode, 0.6))
    T.TOD_HOOKS.append(hook)
    if T.TOD:
        hook(T.TOD)


def backdrop(cx, cy, seed=1, size=260, ring="houses", ring_r=(105, 140), hills_r=(230, 290), trees=24, clear=60):
    """Grass, lawn patches, a ring of houses or towers, trees (outside `clear` studs from the centre), hills, clouds."""
    rng = random.Random(seed)
    T.box((size * 3, size * 3, 1), (cx, cy, -0.5), T.mat("#4E9E3C"))
    light, dark, sl, sd = T.mat("#5CB548"), T.mat("#449236"), [], []
    for _ in range(70):
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(clear * 0.8, size * 0.6)
        (sl if rng.random() < 0.5 else sd).append((cx + d * math.cos(a), cy + d * math.sin(a), rng.uniform(3, 8)))
    discs("lawn.light", sl, light, z=0.04)
    discs("lawn.dark", sd, dark, z=0.04)
    n = 18
    for i in range(n):                                              # far-off houses / towers all round
        a = i / n * 2 * math.pi + rng.uniform(-0.06, 0.06)
        d = rng.uniform(*ring_r)
        hx, hy = cx + d * math.cos(a), cy + d * math.sin(a)
        if ring == "towers":
            h = rng.uniform(50, 110)
            col = ("#8FA3B8", "#B8A48F", "#9BB3A0", "#A89BB8", "#C7C2B8")[i % 5]
            multi("skyline", [((22, 22, h), (hx, hy, h / 2))], T.mat(col))
            multi("skyline.win", [((22.2, 22.2, 1.2), (hx, hy, z)) for z in range(6, int(h) - 2, 6)], tower_window())
        else:
            c = T.PAL2[i % len(T.PAL2)][0]
            multi("backhouse", [((20, 20, 13), (hx, hy, 6.5))], T.mat(c))
            o = prism("backroof", 24, 22, 7, (hx, hy, 13), T.mat(T.ROOFS2[i % len(T.ROOFS2)]))
            o.rotation_euler = (0, 0, a)
    k = 0
    while k < trees:                                                # trees between the plot and the ring
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(clear, ring_r[0] - 12)
        tree2(cx + d * math.cos(a), cy + d * math.sin(a), rng.uniform(0.9, 1.4), ("round", "pine", "blossom")[k % 3],
              seed=seed * 100 + k)
        k += 1
    for i in range(18):                                             # hills
        a = i / 18 * 2 * math.pi + rng.uniform(-0.08, 0.08)
        d = rng.uniform(*hills_r)
        o = ico(rng.uniform(70, 110), (cx + d * math.cos(a), cy + d * math.sin(a), -6),
                T.mat(("#4C9A4A", "#5AAE52", "#3F8A44", "#66B85A")[i % 4]), scale=(1.25, 1.25, rng.uniform(0.28, 0.5)),
                rng=rng, sub=2)
        o.visible_shadow = False
    cm = cloud_mat()
    for i in range(9):                                              # clouds in every direction
        a = i / 9 * 2 * math.pi
        d, z, s = rng.uniform(260, 340), rng.uniform(110, 170), rng.uniform(0.9, 1.4)
        tx, ty = -math.sin(a), math.cos(a)                          # along the ring
        for j in range(5):
            o = T.prim("uv_sphere", segments=16, ring_count=8, radius=rng.uniform(10, 17) * s)
            o.location = (cx + d * math.cos(a) + (j - 2) * 12 * s * tx, cy + d * math.sin(a) + (j - 2) * 12 * s * ty,
                          z + rng.uniform(-3, 5) * s)
            o.rotation_euler = (0, 0, a)
            o.scale = (0.3, 1, 0.8)
            o.data.materials.append(cm)
            o.visible_shadow = False
            o["cloud"] = True


def road(cx, cy, length, width=24, along="x", walk=9, kerb_line=True):
    """A road with a dashed yellow middle line and a raised sidewalk on both sides (like the street's). Returns the
    sidewalk centre offsets (+/-)."""
    ax = along == "x"
    size = (length, width, 0.2) if ax else (width, length, 0.2)
    T.box(size, (cx, cy, 0.0), T.mat("#26262C"))
    dashes = []
    for i in range(int(length / 12)):
        p = -length / 2 + 6 + i * 12
        dashes.append(((6.5, 0.7, 0.04), (cx + p, cy, 0.11)) if ax else ((0.7, 6.5, 0.04), (cx, cy + p, 0.11)))
    multi("road.dashes", dashes, T.mat("#F5C52A")).visible_shadow = False
    off = width / 2 + walk / 2
    for s in (-1, 1):
        if ax:
            T.box((length, walk, T.WALK_H), (cx, cy + s * off, T.WALK_H / 2), T.mat("#C3C6CE"))
            T.box((length, 0.5, T.WALK_H + 0.04), (cx, cy + s * (width / 2 + 0.25), T.WALK_H / 2), T.mat("#9EA1AA"))
        else:
            T.box((walk, length, T.WALK_H), (cx + s * off, cy, T.WALK_H / 2), T.mat("#C3C6CE"))
            T.box((0.5, length, T.WALK_H + 0.04), (cx + s * (width / 2 + 0.25), cy, T.WALK_H / 2), T.mat("#9EA1AA"))
    return off


def zebra(cx, cy, road="x", n=8, road_w=24):
    """Zebra stripes across a road that runs along `road` ("x" or "y"), centred at (cx, cy)."""
    parts = []
    for i in range(n):
        p = -road_w / 2 + 2.2 + i * (road_w - 4.4) / (n - 1)
        parts.append(((6.0, 1.6, 0.03), (cx, cy + p, 0.125)) if road == "x" else ((1.6, 6.0, 0.03), (cx + p, cy, 0.125)))
    multi("road.zebra", parts, T.mat("#F2F2F2")).visible_shadow = False


def lamp(r, lx, ly, arm=(0, -1)):
    """A street lamp on a sidewalk (local spot under root r), its arm over the road in direction arm (a unit x/y
    step). It switches on at dusk and night like the street's lamps."""
    import bpy
    ax, ay = arm
    e = T.empty("lamp", (lx, ly, T.WALK), r)
    T.box((0.5, 0.5, 13.2), (0, 0, 6.6), T.mat("#15161B"), e)
    T.box((0.4 + 3.8 * abs(ax), 0.4 + 3.8 * abs(ay), 0.4), (ax * 2.0, ay * 2.0, 13.0), T.mat("#15161B"), e)
    T.box((1.0 + 1.0 * abs(ax), 1.0 + 1.0 * abs(ay), 0.5), (ax * 3.6, ay * 3.6, 12.6), T.LAMP_BULB, e)
    li = bpy.data.lights.new("lampL", "SPOT")
    li.color = T.lin("#FFBD6B")[:3]
    li.spot_size = math.radians(118)
    li.spot_blend = 0.5
    li.shadow_soft_size = 0.6
    li["bt_lamp"] = True
    lo = bpy.data.objects.new("lampL", li)
    lo.location = (ax * 3.6, ay * 3.6, 12.2)
    lo.parent = e
    T.COL.objects.link(lo)
    T.LAMPS.append(li)
    return e
