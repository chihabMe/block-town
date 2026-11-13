"""The cast library: everyone the town has met so far, built the same way in every episode.

Use after build_town(...) / place(...) (the Roblox look must be on):
    import cast
    doc = cast.get("doctor")          an extra, built once per episode (a second get returns the same person)
    mayor = cast.role("mayor")        a recurring character in a costume (Dad with a sash and a top hat)
    people = cast.crowd(spots)        a random crowd, one per spot (the school hall's audience code)
    cast.names()                      what is in the library

The 8 recurring characters (NIA, TEACH, TALL, BOY, DAD, GRAN, KID, MAN) are built by town.py and never change.
Add a new person here once a story needs them, so the next episode gets the same face and clothes.
"""
import town as T

# name: (character(...) arguments, keyword arguments, costume pieces from rprops, what they are)
EXTRAS = {
    "doctor": (("Doctor", "#C98A5A", "#F4F6F8", "#5FA8D3", "side", "dark"), dict(sleeves="long", seed=11), ("red_cross",),
               "white coat with a red cross (ep08)"),
    "watchman": (("Watchman", "#E1B892", "#2F3F5E", "#2A2A33", "side", "grey"), dict(sleeves="long", seed=11),
                 ("flat_cap", "moustache", "lantern"), "old night-watchman with a lantern (ep07)"),
    "baker": (("Baker", "#C98A5A", "#F2EEE6", "#3A3A46", "bun", "brown"), dict(sleeves="long", seed=21), (),
              "baker in white (ep07)"),
    "postman": (("Postman", "#8A5A3C", "#3E7CC9", "#22304A", "cap", "#1F3A7A"), dict(seed=22), ("mail_bag",),
                "postman with a cap and mail bag (ep07)"),
    "driver": (("Driver", "#E4B58A", "#2F55A8", "#22222A", "cap", "#1F3A7A"), dict(seed=9), (), "bus driver (ep05)"),
    "guard": (("Guard", "#C98A5A", "#FF7A1A", "#2F4B7C", "cap", "#FFD21F"), dict(seed=14), ("hivis",),
              "guard in a hi-vis vest (freeze)"),
    "delivery": (("Delivery", "#D9A27A", "#2B62D9", "#1F2330", "cap", "#E23B3B"), dict(seed=17), (),
                 "delivery driver (freeze)"),
    "baby": (("Baby", "#EDB78F", "#FFFFFF", "#9AD0FF", "curl", "brown"), dict(shoes="#EDB78F", scale=0.45), (),
             "a baby (ep05)"),
    "jake": (("Jake", "#E0B080", "#14B8C4", "#243044", "tuft", "blond"), dict(stripes="#F4F7FA", shoes="#F2F2F2"), (),
             "a school kid in a striped tee (ep03)"),
    "remy": (("Remy", "#F0C8A0", "#3A7BD5", "#2A2A32", "curl", "brown"), dict(scale=0.75, shoes="#F2F2F2"), (),
             "a small kid (ep03)"),
}

# role: (recurring character's name in town.py, costume pieces, what they are)
ROLES = {
    "mayor": ("DAD", ("sash", "top_hat"), "Dad with a MAYOR sash and a top hat (ep07)"),
    "nurse": ("TEACH", ("nurse_cap",), "the teacher in a nurse's cap (ep07)"),
    "ice_cream_man": ("MAN", ("apron", "paper_hat"), "Man in an apron and paper hat (ep07)"),
    "mailman": ("DAD", ("mail_bag",), "Dad with a mail bag (ep09)"),
}

_MADE = {}


def names():
    return {"extras": {k: v[3] for k, v in EXTRAS.items()}, "roles": {k: v[2] for k, v in ROLES.items()}}


def _red_cross(c):
    from roblox import rbox
    from rprops import glow
    for sx, sz in ((0.5, 0.14), (0.14, 0.5)):                 # a red cross on the chest
        rbox((sx, 0.06, sz), (0.5, -0.53, 1.45), glow("#FF3B30", 1.6), c["body"], bv=0.02)


def _wear(c, pieces):
    import rprops
    out = []
    for p in pieces:
        out.append(_red_cross(c) if p == "red_cross" else getattr(rprops, p)(c))
    c.setdefault("props", []).extend(out)
    return out


def get(name):
    """An extra from the library (see names()). Built the first time it is asked for in an episode."""
    if name not in EXTRAS:
        raise KeyError(f"no extra {name!r} in the cast library: {', '.join(EXTRAS)}")
    if name not in _MADE:
        args, kw, pieces, _ = EXTRAS[name]
        c = T.character(*args, **kw)
        _wear(c, pieces)
        _MADE[name] = c
    return _MADE[name]


def role(name):
    """A recurring character dressed for a role (see names()). The costume stays on for the whole episode."""
    if name not in ROLES:
        raise KeyError(f"no role {name!r} in the cast library: {', '.join(ROLES)}")
    key = "role:" + name
    if key not in _MADE:
        who, pieces, _ = ROLES[name]
        c = getattr(T, who)
        _wear(c, pieces)
        _MADE[key] = c
    return _MADE[key]


def crowd(spots, seed=9):
    """A random crowd, one person per spot (x, y, z), the same people for the same seed. Pose them each frame with
    anim.sit / clap / cheer / gasp, or seat them in the school hall with hall["fill"](T, mood)."""
    from places.school_hall import crowd_people
    return crowd_people([tuple(s)[:3] for s in spots], seed)
