"""The world library: places built once, saved, and loaded again by every episode.

    street = place("street", rule_big="KNOW YOUR PRICE", shop_signs=("PRICE SHOP", "TAG CAFE"))
    hall = place("school_hall", banner="TALENT SHOW")
    stand(BOY, hall.mark("stage"), 180, "happy", T);  hall.cam("back")

Each place is a module in this folder with:
    GEO              the argument names that change the place's shape (they are part of the saved copy's name)
    build(**geo)     builds it from kit code at its parking spot; returns {"marks": {...}, "cams": {...}, ...}
    restore(p)       (optional) after loading a saved copy: reconnect the kit's lists (houses, lamps, shops)
    dress(p, **ep)   (optional) every episode: what changes per video (sign words, a crowd) and the helper functions
                     (p["light"](on), p["tuck"](k)). Runs after build() and after loading.

Places are built from code every time: since town.prim() the whole street builds in about 2.5 s, faster than loading a
saved copy (about 6 s). A heavy place can set CACHE = True in its module: the first time it is used with a given shape
it is saved to places/cache/<name>-<hash>.blend (with a .json of its marks and cameras) and appended from that file
afterwards. The hash covers the place's module, the kit files it is built with and its GEO arguments, so a change to any
of them rebuilds it on its own. BT_PLACE_CACHE=1 saves and loads every place, BT_PLACE_CACHE=0 none.

Marks are (x, y, z) spots or (x, y, z, yaw) for a character who should face a way. Cams are (pos, target, fov).
"""
import ast, hashlib, importlib, json, os, time
from pathlib import Path

import bpy

import town as T

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
CACHE = HERE / "cache"
DEPS = ("town.py", "roblox.py", "world2.py", "rprops.py", "rlook_tex.py", "places/__init__.py")
FORCE = os.environ.get("BT_PLACE_CACHE")          # "1" every place saved/loaded, "0" none, unset: the module's CACHE
LOADED = []          # every Place used in this episode, in order


class Place(dict):
    """One place in this episode. It is also a dict (p["stage"], p["light"](on)) so older episode code keeps working."""

    def __init__(self, name, objs, info, root=None):
        super().__init__()
        self.name, self.objs, self.info, self.root = name, objs, info, root
        self.marks = info.get("marks", {})
        self.cams = info.get("cams", {})

    def mark(self, n):
        """A named spot: (x, y, z) or (x, y, z, yaw)."""
        if n not in self.marks:
            raise KeyError(f"{self.name} has no mark {n!r}. Marks: {', '.join(self.marks)}")
        return tuple(self.marks[n])

    def spot(self, n):
        """A mark without its yaw: (x, y, z), for stand(c, place.spot("desk_3"), yaw, ...)."""
        return self.mark(n)[:3]

    def yaw(self, n, default=0.0):
        m = self.mark(n)
        return m[3] if len(m) > 3 else default

    def cam(self, n, fov=None, **kw):
        """Use a named camera spot inside a shot: place.cam("back"). kw goes to town.shot (side, key_w, roll, ...)."""
        if n not in self.cams:
            raise KeyError(f"{self.name} has no camera {n!r}. Cameras: {', '.join(self.cams)}")
        pos, target, f = self.cams[n]
        return T.shot(tuple(pos), tuple(target), fov or f, **kw)

    def tagged(self, tag):
        return [o for o in self.objs if tag in o.keys()]

    def one(self, tag):
        found = self.tagged(tag)
        if not found:
            raise KeyError(f"{self.name}: nothing tagged {tag!r}")
        return found[0]


def _key(mod, geo):
    h = hashlib.sha1()
    for n in DEPS:
        h.update((KIT / n).read_bytes())
    h.update(Path(mod.__file__).read_bytes())
    h.update(json.dumps(geo, sort_keys=True, default=str).encode())
    h.update(bpy.app.version_string.encode())
    return h.hexdigest()[:12]


def _tag_materials():
    """Write each kit material's MATS key on it, so a loaded copy can be matched to this episode's materials."""
    for k, m in T.MATS.items():
        try:
            m["bt_key"] = repr(k)
        except (TypeError, ReferenceError):
            pass


def _merge_materials():
    """After loading: a loaded material whose key this episode already has is swapped for the episode's own (so
    time_of_day and window_light still reach it); new keys are added to MATS (so mat(key=...) finds them)."""
    known = {m.as_pointer() for m in T.MATS.values()}
    merged = added = 0
    for m in list(bpy.data.materials):
        if m.as_pointer() in known or "bt_key" not in m.keys():
            continue
        try:
            k = ast.literal_eval(m["bt_key"])
        except (ValueError, SyntaxError):
            continue
        if k in T.MATS:
            m.user_remap(T.MATS[k])
            bpy.data.materials.remove(m)
            merged += 1
        else:
            T.MATS[k] = m
            known.add(m.as_pointer())
            added += 1
    return merged, added


def _build(name, mod, geo, coll_name):
    before = {o.as_pointer() for o in bpy.data.objects}
    info = mod.build(**geo) or {}
    objs = [o for o in bpy.data.objects if o.as_pointer() not in before]
    coll = bpy.data.collections.new(coll_name)
    T.scene.collection.children.link(coll)
    for o in objs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    return coll, objs, info


def _save(coll, info, path):
    CACHE.mkdir(parents=True, exist_ok=True)
    _tag_materials()
    tmp = path.with_suffix(".tmp.blend")
    bpy.data.libraries.write(str(tmp), {coll}, path_remap="ABSOLUTE", fake_user=True, compress=False)
    os.replace(tmp, path)
    path.with_suffix(".json").write_text(json.dumps(info))


def _load(path, coll_name):
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        dst.collections = [coll_name]
    coll = dst.collections[0]
    T.scene.collection.children.link(coll)
    coll.use_fake_user = False
    return coll, list(coll.all_objects), json.loads(path.with_suffix(".json").read_text())


def place(name, **kw):
    """Put a place from the library into this episode and return it (a Place). Arguments named in the place's GEO
    change its shape; the rest (sign words, a crowd) are applied fresh every episode."""
    if T._LOOK is None:
        T.use_look("roblox", True)
    mod = importlib.import_module(f"places.{name}")
    geo = {k: v for k, v in kw.items() if k in mod.GEO}
    ep = {k: v for k, v in kw.items() if k not in mod.GEO}
    key = _key(mod, geo)
    coll_name = f"place:{name}-{key}"
    path = CACHE / f"{name}-{key}.blend"
    t0 = time.perf_counter()
    use_cache = FORCE == "1" if FORCE in ("0", "1") else bool(getattr(mod, "CACHE", False))
    if use_cache and path.exists() and path.with_suffix(".json").exists():
        coll, objs, info = _load(path, coll_name)
        merged, added = _merge_materials()
        how = f"loaded from {path.name} ({len(objs)} objects, {merged} materials shared, {added} new)"
        loaded = True
    else:
        coll, objs, info = _build(name, mod, geo, coll_name)
        how = f"built from code ({len(objs)} objects)"
        if use_cache:
            t1 = time.perf_counter()
            _save(coll, info, path)
            how += f", saved as {path.name} in {time.perf_counter() - t1:.1f}s"
        loaded = False
    p = Place(name, objs, info)
    roots = [o for o in objs if o.parent is None and o.get("bt_root")]
    p.root = roots[0] if roots else None
    if loaded and hasattr(mod, "restore"):
        mod.restore(p)
    if hasattr(mod, "dress"):
        mod.dress(p, **ep)
    elif ep:
        raise TypeError(f"place {name!r} takes no arguments {sorted(ep)} (shape arguments: {', '.join(mod.GEO)})")
    LOADED.append(p)
    print(f"TJ place {name}: {how} in {time.perf_counter() - t0:.1f}s", flush=True)
    T.tick(f"place {name}")
    return p
