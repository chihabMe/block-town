"""Blender -> Three.js bake for one span of an episode. Normally run by render_threejs.sh, not by hand.

Runs the episode's normal render loop, but at each frame it records, instead of rendering:
  every object's world matrix, visibility and material slots; the camera, sun and key light; the sky; material glow
  strengths (windows and lamps change at dusk) and the street lamps.
First frame: scene.glb (Z-up geometry). Last frame: materials.json (recipes for Three.js), anim.json + anim.bin.
Everything is written to BT_TJ_OUT (default EPISODE/threejs/).

    BT_LIFE=1 blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/threejs/bake.py -- EPISODE render F0 F1
BT_TJ_REF=1 also renders the normal Blender frame into BT_FRAME_DIR (for comparisons).
"""
import json, os, re, runpy, shutil, sys, time
from pathlib import Path

import bpy
import numpy as np

BW = Path(__file__).resolve().parent.parent                 # SKILL/blockworld
sys.path.insert(0, str(BW))
import town  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:]
F0, F1 = int(ARGS[2]), int(ARGS[3])
OUT = Path(os.environ.get("BT_TJ_OUT") or Path(ARGS[0]).resolve() / "threejs")
OUT.mkdir(parents=True, exist_ok=True)
REF = os.environ.get("BT_TJ_REF") == "1"
_orig_render = town.render_still

S = {"objs": None, "mats": [], "vis": [], "slots": [], "cam": [], "sun": [], "key": [], "sky": [], "emit": [],
     "lamp": [], "times": []}


def col(sock):
    return [round(float(x), 5) for x in sock.default_value[:3]]


def linked(sock):
    return sock.links[0].from_node if sock.is_linked else None


def image_info(img_node):
    src = Path(bpy.path.abspath(img_node.image.filepath))
    dst = OUT / "tex" / src.name
    if not dst.exists():
        dst.parent.mkdir(exist_ok=True)
        shutil.copy(src, dst)
    proj = "uv"
    vec = linked(img_node.inputs["Vector"])
    if vec is not None:
        proj = "objproj" if vec.type == "COMBXYZ" else "unknown"
    return {"src": f"tex/{src.name}", "proj": proj, "clip": img_node.extension == "CLIP"}


def describe(m):
    """Turn one Blender material into a small recipe Three.js can rebuild."""
    d = {"color": [0.8, 0.8, 0.8], "rough": 0.5, "spec": 0.5, "emit": [0, 0, 0], "emit_s": 0.0, "alpha": 1.0,
         "kind": "flat"}
    if not m.use_nodes or "Principled BSDF" not in m.node_tree.nodes:
        d["kind"] = "nonode"
        d["color"] = [round(x, 5) for x in m.diffuse_color[:3]]
        return d
    b = m.node_tree.nodes["Principled BSDF"]
    d["rough"] = round(b.inputs["Roughness"].default_value, 4)
    d["spec"] = round(b.inputs["Specular IOR Level"].default_value, 4)
    d["emit"] = col(b.inputs["Emission Color"])
    d["emit_s"] = round(b.inputs["Emission Strength"].default_value, 4)
    d["alpha"] = round(b.inputs["Alpha"].default_value, 4)
    em = linked(b.inputs["Emission Color"])
    if em is not None and em.type == "TEX_IMAGE":
        d["emit_img"] = image_info(em)                # a lit screen: the picture glows
    src = linked(b.inputs["Base Color"])
    d["color"] = col(b.inputs["Base Color"])
    if src is None:
        return d
    if src.type == "TEX_IMAGE":
        d["kind"] = "image"; d["img"] = image_info(src)
    elif src.type == "TEX_BRICK":
        d["kind"] = "brick"
        d["brick"] = {k: (col(src.inputs[k]) if k in ("Color1", "Color2", "Mortar") else src.inputs[k].default_value)
                      for k in ("Color1", "Color2", "Mortar", "Scale", "Mortar Size", "Brick Width", "Row Height")}
        d["brick"]["offset"] = src.offset; d["brick"]["offset_freq"] = src.offset_frequency
    elif src.type == "MIX":
        a = linked(src.inputs["A"]); bb = linked(src.inputs["B"]); f = linked(src.inputs["Factor"])
        d["A"] = col(src.inputs["A"]) if hasattr(src.inputs["A"].default_value, "__len__") else None
        if a is None and d["A"]:
            d["color"] = d["A"]
        if src.blend_type == "MULTIPLY" and bb is not None and bb.type == "TEX_IMAGE":
            d["kind"] = "multiply"; d["img"] = image_info(bb)
        elif bb is not None and bb.type == "TEX_IMAGE" and f is not None:
            d["kind"] = "decal"; d["img"] = image_info(bb)
            d["front_only"] = f.type == "MATH"
        elif f is not None and f.type == "MATH" and f.operation == "LESS_THAN":
            fr = linked(f.inputs[0]); mul = linked(fr.inputs[0]) if fr else None
            d["kind"] = "banded"; d["B"] = col(src.inputs["B"])
            d["freq"] = mul.inputs[1].default_value if mul else 1.5; d["thr"] = f.inputs[1].default_value
        else:
            d["kind"] = "mix?"
    else:
        d["kind"] = "unknown:" + src.type
    return d


def plastic():
    try:
        import roblox
        roblox._plastic_all()          # the only roblox-look hook that changes material values (fog is off in sun/dusk)
    except Exception:  # noqa: BLE001
        pass


def setup():
    """First frame: ids, overlay flags, geometry export, lamp list."""
    plastic()
    objs = [o for o in bpy.context.scene.objects if o.type in ("MESH", "FONT", "CURVE")]
    for i, o in enumerate(objs):
        o["hid"] = i
    anim = sys.modules.get("anim")
    overlay = set()
    for card in (anim.CARDS if anim else []):
        for o in card.children_recursive:
            if "hid" in o.keys():
                overlay.add(o["hid"])
    deps = bpy.context.evaluated_depsgraph_get()
    copies = []
    for o in objs:
        if o.type != "MESH":
            me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
            c = bpy.data.objects.new(o.name + "__mesh", me)
            bpy.context.scene.collection.objects.link(c)
            c.matrix_world = o.matrix_world
            c["hid"] = o["hid"]
            copies.append(c)
    bpy.ops.object.select_all(action="DESELECT")
    for o in [o for o in objs if o.type == "MESH"] + copies:
        o.select_set(True)
    t0 = time.perf_counter()
    bpy.ops.export_scene.gltf(filepath=str(OUT / "scene.glb"), export_format="GLB", use_selection=True,
                              export_yup=False, export_apply=True, export_extras=True, export_cameras=False,
                              export_lights=False, export_animations=False, export_materials="EXPORT")
    print(f"TJ export {time.perf_counter() - t0:.1f}s, {len(objs)} objects ({len(copies)} text/curve), "
          f"{len(overlay)} overlay parts", flush=True)
    for c in copies:
        me = c.data
        bpy.data.objects.remove(c)
        bpy.data.meshes.remove(me)
    S["objs"] = objs
    S["overlay"] = overlay
    S["lamps"] = [o for o in bpy.context.scene.objects if o.type == "LIGHT" and o.data in town.LAMPS]


def write_materials():
    plastic()
    objs = S["objs"]
    S["matlist"] = list(bpy.data.materials)
    mats = {m.name: describe(m) for m in S["matlist"]}
    info = [{"hid": o["hid"], "name": o.name, "shadow": bool(getattr(o, "visible_shadow", True)),
             "overlay": o["hid"] in S["overlay"]} for o in objs]
    lamps = [{"m": [round(float(x), 5) for x in np.array(o.matrix_world).T.reshape(16)],
              "size": o.data.spot_size, "blend": o.data.spot_blend, "c": list(o.data.color)} for o in S["lamps"]]
    (OUT / "materials.json").write_text(json.dumps({"materials": mats, "objects": info, "lamps": lamps}))
    kinds = {}
    for d in mats.values():
        kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
    print("TJ material kinds", kinds, flush=True)


def emission_now():
    out = {}
    for m in bpy.data.materials:
        if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
            out[m.name] = round(m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value, 4)
    return out


def record():
    objs = S["objs"]
    S["mats"].append(np.array([np.array(o.matrix_world).T.reshape(16) for o in objs], dtype=np.float32))
    S["vis"].append(np.array([not o.hide_render for o in objs], dtype=bool))
    S["slots"].append([tuple(m.name if m else "" for m in o.data.materials) if o.type == "MESH" and o.data else ()
                       for o in objs])
    cam = town.cam
    S["cam"].append({"m": [round(float(x), 6) for x in np.array(cam.matrix_world).T.reshape(16)],
                     "fov": round(float(np.degrees(cam.data.angle)), 4)})
    sd = town.sun.data
    S["sun"].append({"m": [round(float(x), 6) for x in np.array(town.sun.matrix_world).T.reshape(16)],
                     "e": round(sd.energy, 4), "c": [round(x, 5) for x in sd.color]})
    kd = town.key.data
    S["key"].append({"p": [round(x, 4) for x in town.key.location], "e": kd.energy, "c": [round(x, 4) for x in kd.color]})
    r = town.ramp.color_ramp
    S["sky"].append([round(x, 5) for x in (*r.elements[0].color[:3], *r.elements[1].color[:3],
                                           town.bg.inputs["Strength"].default_value)])
    S["emit"].append(emission_now())
    S["lamp"].append(round(town.LAMPS[0].energy, 2) if town.LAMPS else 0.0)


def finish():
    write_materials()
    objs = S["objs"]
    M = np.stack(S["mats"]); V = np.stack(S["vis"])
    n = len(M)
    moving = np.abs(M - M[0]).max(axis=(0, 2)) > 1e-5
    flick = (V != V[0]).any(axis=0)
    swap = [any(S["slots"][f][i] != S["slots"][0][i] for f in range(n)) for i in range(len(objs))]
    dyn = [i for i in range(len(objs)) if moving[i] or flick[i] or swap[i]]
    np.ascontiguousarray(M[:, dyn, :].transpose(1, 0, 2), dtype=np.float32).tofile(OUT / "anim.bin")
    names = sorted({k for e in S["emit"] for k in e})
    emit = {}
    for nm in names:
        vals = [e.get(nm, 0.0) for e in S["emit"]]
        if max(vals) - min(vals) > 1e-4:
            emit[nm] = vals
    out = {"f0": F0, "f1": F1, "fps": getattr(sys.modules.get("anim"), "FPS", 30), "frames": n,
           "static": {str(objs[i]["hid"]): {"m": [round(float(x), 5) for x in M[0, i]], "v": bool(V[0, i])}
                      for i in range(len(objs))},
           "dynamic": [{"hid": objs[i]["hid"], "v": [int(x) for x in V[:, i]],
                        "s": [list(S["slots"][f][i]) for f in range(n)] if swap[i] else None} for i in dyn],
           "cam": S["cam"], "sun": S["sun"], "key": S["key"], "sky": S["sky"], "emit": emit, "lamp": S["lamp"]}
    (OUT / "anim.json").write_text(json.dumps(out, separators=(",", ":")))
    print(f"TJ anim: {n} frames, {len(objs)} objects, {len(dyn)} dynamic, {len(emit)} glowing materials change, "
          f"bake per frame mean {np.mean(S['times'][1:]) * 1000:.1f} ms", flush=True)


def render_still(path):
    t0 = time.perf_counter()
    bpy.context.view_layer.update()
    if S["objs"] is None:
        setup()
    record()
    S["times"].append(time.perf_counter() - t0)
    f = int(re.search(r"f_(\d+)", str(path)).group(1))
    if REF:
        _orig_render(path)
    if f == F1:
        finish()


town.render_still = render_still
runpy.run_path(str(BW / "run.py"), run_name="__main__")
