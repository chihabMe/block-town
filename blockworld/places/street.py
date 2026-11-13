"""The main street: two rows of houses, two shops, the rule billboard, lamps and trees, the town hall at the far end
(y = 190), and in world v2 the dressing from world2.py (gardens, fences, cars, hills, back roofs, clouds).

build_town(...) in town.py is a shortcut for place("street", ...). Episode arguments (never saved):
    rule_big, rule_title   the billboard's big line and small title
    shop_signs             the two shops' names
    hall_sign, clock       the town hall's name and its clock
"""
import ast
import json

import town as T

GEO = ("shop_spots", "style", "detail")


def build(shop_spots=((1, 30), (-1, 90)), style="roblox", detail=True):
    shop_spots = [tuple(s) for s in shop_spots]
    T.ground()
    k = 0
    for sx in (-1, 1):
        for y in T.HOUSE_Y:
            x = sx * (T.ROAD_W / 2 + T.WALK_W + 6 + 9)
            if (sx, y) in shop_spots:
                r = T.shop(x, y, None)
                r["bt_shop_i"] = shop_spots.index((sx, y))
            else:
                if detail and style == "roblox":
                    c, dk = T.PAL2[k % len(T.PAL2)]
                    T.house(x, y, c, dk, roof_h=7 + (k % 3), roof=T.ROOFS2[(k * 2 + (sx > 0)) % len(T.ROOFS2)])
                else:
                    c, dk = T.PAL[k % len(T.PAL)]
                    T.house(x, y, c, dk, roof_h=7 + (k % 3))
            k += 1
            T.tree(sx * (T.ROAD_W / 2 + T.WALK_W + 2.6), y + 15, 0.8 + 0.15 * (k % 3), seed=k)
            T.lamp(sx * (T.ROAD_W / 2 + 1.6), y + 15)
    T.town_hall(190, None)
    bs, by = shop_spots[0]
    T.billboard(bs * 31, by, 14, None, None, yaw=bs * (-90 + 22))
    T.clouds()
    if detail and style == "roblox":
        import world2
        world2.dress(shop_spots)
    # tags a loaded copy needs to reconnect houses (their own window lights) and street lamps
    for i, hs in enumerate(T.HOUSES):
        hs["root"]["bt_house"] = json.dumps({"i": i, "x": hs["x"], "y": hs["y"], "h": hs["h"], "roof_h": hs["roof_h"],
                                             "roof": hs["roof"], "win": repr(("window", hs["x"], hs["y"]))})
    for li in T.LAMPS:
        li["bt_lamp"] = True
    return {"marks": _marks(shop_spots), "cams": _cams(shop_spots)}


def _marks(shop_spots):
    m = {"road": (0, 0, T.ROAD), "hall_steps": (0, 178, 3.6, 0), "billboard_foot": (shop_spots[0][0] * 17, shop_spots[0][1], T.WALK)}
    for i, (sx, y) in enumerate(shop_spots):                          # on the sidewalk in front of each shop's door
        m[f"shop_{i + 1}_door"] = (sx * 18, y, T.WALK, -90 if sx > 0 else 90)    # facing the road
    k = 0
    for sx in (-1, 1):
        for y in T.HOUSE_Y:
            if (sx, y) not in shop_spots:
                m[f"house_{k + 1}_door"] = (sx * 18, y, T.WALK, -90 if sx > 0 else 90)
                k += 1
    return m


def _cams(shop_spots):
    cams = {"down_street": ((0, -30, 6), (0, 60, 6), 42),          # along the road toward the town hall
            "hall_wide": ((0, 92, 9), (0, 180, 17), 55)}            # the whole town hall front
    for i, (sx, y) in enumerate(shop_spots):                         # a person at shop_N_door with the shop behind
        cams[f"shop_{i + 1}_front"] = ((sx * 10.5, y - 17, 6.4), (sx * 21.0, y + 1, 5.6), 50)
    return cams


def restore(p):
    """After loading a saved street: refill the kit's lists of houses (window lights), shops and street lamps."""
    houses = sorted(((json.loads(o["bt_house"]), o) for o in p.objs if "bt_house" in o.keys()), key=lambda t: t[0]["i"])
    for d, o in houses:
        T.HOUSES.append({"x": d["x"], "y": d["y"], "win": T.MATS[ast.literal_eval(d["win"])], "root": o, "h": d["h"],
                         "roof_h": d["roof_h"], "roof": d["roof"]})
    T.SHOPS.extend(sorted((o for o in p.objs if "bt_shop" in o.keys()), key=lambda o: o["bt_shop_i"]))
    T.LAMPS.extend(o.data for o in p.objs if o.type == "LIGHT" and o.data.get("bt_lamp"))


def dress(p, rule_big="", shop_signs=("CORNER SHOP", "BAKERY"), rule_title="TOWN RULE", hall_sign="TOWN HALL",
          clock="8:00"):
    for o in p.objs:
        if "bt_shop_i" in o.keys():
            T.shop_sign(o, shop_signs[o["bt_shop_i"]])
        elif o.get("bt_billboard"):
            T.billboard_text(o, rule_title, rule_big)
        elif o.get("bt_townhall"):
            T.hall_text(o, hall_sign, clock)
