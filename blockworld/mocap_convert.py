"""Turn a motion-capture clip (BVH, e.g. the free CMU database) into a pose clip for our blocky characters.

    blender -b --factory-startup --python-exit-code 1 -P blockworld/mocap_convert.py -- IN.bvh OUT.json [first last]

Our characters bend only at the shoulders, hips, neck and waist (Roblox-style, no elbows or knees). For every frame
this measures, on the mocap skeleton: which way the hips face, how the torso leans and tilts, the direction of each
upper arm and thigh, the head nod, the hip bounce and how far the body travelled. It writes them as pose() angles
(blockworld/mocap/<name>.json); anim.mocap() plays a clip on any character.
"""
import json
import math
import sys

import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = ARGS[0], ARGS[1]
FIRST = int(ARGS[2]) if len(ARGS) > 2 else None
LAST = int(ARGS[3]) if len(ARGS) > 3 else None
OUR_LEG = 2.0                 # our characters' leg length in studs (hip pivot to the sole)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_anim.bvh(filepath=SRC, axis_forward="-Z", axis_up="Y", global_scale=1.0, frame_start=0,
                        use_fps_scale=False, rotate_mode="NATIVE")
arm = bpy.context.object
scene = bpy.context.scene
act = arm.animation_data.action
f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
if FIRST is not None:
    f0, f1 = max(f0, FIRST), min(f1, LAST)
fps = None
with open(SRC) as fh:
    for line in fh:
        if line.strip().startswith("Frame Time"):
            fps = 1.0 / float(line.split(":")[1])
            break


def P(name, tail=False):
    pb = arm.pose.bones[name]
    return arm.matrix_world @ (pb.tail if tail else pb.head)


def deg(a):
    return round(math.degrees(a), 2)


Z = Vector((0, 0, 1))
rows = []
scene.frame_set(f0)
leg_len = (P("RightLeg") - P("RightUpLeg")).length + (P("RightFoot") - P("RightLeg")).length
scale = OUR_LEG / leg_len
start = P("Hips").copy()
yaw0 = None
for f in range(f0, f1 + 1):
    scene.frame_set(f)
    hips = P("Hips")
    # pelvis frame: right = left hip -> right hip (flattened), forward = up x right
    rp = P("RightUpLeg") - P("LeftUpLeg")
    rp.z = 0
    rp.normalize()
    fp = Z.cross(rp).normalized()
    yaw = math.atan2(fp.x, -fp.y)
    if yaw0 is None:
        yaw0, F0, R0 = yaw, fp.copy(), rp.copy()
    # chest frame
    up = (P("Neck") - P("Hips")).normalized()
    rc = P("RightArm") - P("LeftArm")
    rc = (rc - up * rc.dot(up)).normalized()
    fc = up.cross(rc).normalized()
    lean = -math.atan2(up.dot(fp), up.dot(Z))                    # pose(): lean < 0 = forward
    tilt = math.atan2(up.dot(-rp), up.dot(Z))                     # pose(): tilt > 0 toward armR (the left side)

    def arm_angles(a, b, side):
        d = (P(b) - P(a)).normalized()
        lx, ly, lz = -d.dot(rc), -d.dot(fc), d.dot(up)          # our local axes: -Y forward, -X the right side
        fwd = math.atan2(-ly, math.hypot(lx, lz))
        out = math.atan2(-lx, -lz) if side == "L" else math.atan2(lx, -lz)
        return [deg(fwd), deg(out)]

    def leg_angle(a, b):
        d = (P(b) - P(a)).normalized()
        ly, lz = -d.dot(fp), d.dot(Z)
        return deg(math.atan2(-ly, -lz))

    hd = (P("Head", tail=True) - P("Neck")).normalized()
    look = -math.atan2(hd.dot(fc), hd.dot(up))
    move = hips - start
    rows.append({
        "yaw": deg(yaw - yaw0),
        "fwd": round(move.dot(F0) * scale, 3), "side": round(move.dot(R0) * scale, 3),
        # height from the lowest foot, not the hips: without knees a squat would sink the whole body into the ground
        "up": round(min(P(b).z for b in ("LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase")) * scale, 3),
        "lean": deg(lean), "tilt": deg(tilt),
        "armL": arm_angles("RightArm", "RightForeArm", "L"),      # our armL is the character's right arm
        "armR": arm_angles("LeftArm", "LeftForeArm", "R"),
        "legL": leg_angle("RightUpLeg", "RightLeg"), "legR": leg_angle("LeftUpLeg", "LeftLeg"),
        "head": [0.0, deg(max(-0.6, min(0.6, look)))],
    })
low = min(r["up"] for r in rows)
for r in rows:
    r["up"] = round(r["up"] - low, 3)                              # the lowest foot of the clip is the ground
json.dump({"source": SRC.split("/")[-1], "fps": round(fps, 3), "frames": rows}, open(OUT, "w"))
print(f"MOCAP {len(rows)} frames at {fps:.0f} fps -> {OUT}")
