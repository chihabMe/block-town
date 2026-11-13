# Places

The town is a library. An episode names the places it needs, and only those are built. A school story does not build the street. A street story does not build the classroom.

```python
from places import place
import cast

street = place("street", rule_big="KNOW YOUR PRICE", shop_signs=("PRICE SHOP", "TAG CAFE"))
hall = place("school_hall", banner="TALENT SHOW")
doc = cast.get("doctor")
stand(BOY, hall.spot("stage"), hall.yaw("stage"), "happy", T)
hall.cam("crowd_pov")
```

`build_town(...)` is the shortcut for `place("street", ...)`. Old episodes that call `build_town` keep working. `rprops.school_hall(...)` and `rprops.bedroom(...)` also still work and return the same place.

`place()` turns the Roblox look on by itself. Call it after the imports and before anyone stands.

## How to stand someone

- `p.spot("door")` is `(x, y, z)`. `p.yaw("door")` is the way they face. `p.mark("door")` is both.
- Marks whose name contains `desk`, `seat`, `sofa` or `table` are for `sit(...)`. The seat is 2 studs up. Every other mark is for `stand(...)`.
- `walk_dir(c, start, yaw, t, face)` walks any direction. Use it when a mark faces across the street, not only down it.
- `p.cam("wide")` is a ready camera inside a shot. It calls `shot(...)`. Extra words (`roll`, `side`, `key_w`) pass through.

Per-video words (a banner, a shop name, a clock) are arguments of `place()`. They are drawn fresh every episode. They are not part of the saved shape.

## Where the places sit

Indoor places share one closed room (`places/_room.py`): two-tone walls, a door, windows that are bright by day and dark blue at night, and ceiling lamps that come on at dusk. They are parked in a row down `-Y`, 100 studs apart, so a camera in one room cannot see the next.

Outdoor places (`places/_outdoor.py`) each stand on their own plot, 1000 studs apart, with grass, hills, distant houses and clouds. Their lamps join the town's lamps. School windows glow at night like the houses. Downtown glass is blue by day and lit at dusk.

| Place | Parked at | What changes per video |
|---|---|---|
| `street` | the street, y −60 to 190 | `rule_big`, `rule_title`, `shop_signs`, `hall_sign`, `clock` |
| `bedroom` | y = −460 | the blanket moves with `p["tuck"](k)`: 0 at the waist, 1 up to the nose |
| `school_hall` | y = −560 | `banner`, `crowd=True`. `p["light"](on)` is the stage spotlight |
| `classroom` | y = −760 | `board` (one line or a list of chalk lines) or `board_picture` |
| `shop_inside` | y = −860 | `sign`, `special` (an offer card in the window) |
| `home` | y = −960 | `tv` (a landscape picture on the television) |
| `park` | (1000, 0) | `sign`. `p["swing"](T)` and `p["seesaw"](T)` move the playground |
| `school_front` | (2000, 0) | `name`, `clock`, `bus=True` |
| `downtown` | (3000, 0) | `signs` (`{index: name}`), `screen` (a landscape picture). `p["lights"]("green")` sets the traffic lights |

Pictures on the television, the classroom board and the downtown screen must be landscape. Phone pictures are portrait and will not fit those slots.

Shape arguments (where a place is parked, how many seats) are listed as `GEO` in the module. Passing one builds a different copy. Do not move a place to get it into a shot. Use its marks and cameras.

## Marks and cameras

### street

Marks: `road`, `hall_steps`, `billboard_foot`, `shop_1_door`, `shop_2_door`, `house_1_door` … one door per house that is not a shop.

Cameras: `down_street`, `hall_wide`, `shop_1_front`, `shop_2_front`.

The road between x = −8 and 8, and the sidewalk between |x| = 14 and 19, stay clear. Fences sit at |x| = 21.7.

### bedroom

Marks: `seat` (on the bed), `stand` (by the nightstand), `floor`.

Cameras: `front`, `bed_close`, `door`.

### school_hall

Marks: `stage`, `aisle`, `door`, `seat_1` … (`rows` × `per_row`, default 4 × 8).

Cameras: `back`, `crowd_pov`, `stage_front`, `side`.

`cast.crowd(spots)` builds the same kind of audience. The hall's own `crowd=True` fills its seats.

### classroom

Marks: `teacher`, `board`, `door`, `window`, `desk_1` … `desk_9` (three rows of three, facing the board).

Cameras: `back`, `teacher_pov`, `pupil_pov`, `window_side`, `board_close`, `door`.

### shop_inside

Marks: `keeper`, `customer`, `aisle`, `fridge`, `door`, `window`.

Cameras: `entrance`, `over_counter`, `customer_pov`, `aisle`, `fridge_side`, `wide`.

### home

Marks: `sofa_1` … `sofa_3`, `table_1` … `table_4`, `stove`, `sink`, `fridge`, `tv`, `door`, `window`.

Cameras: `wide`, `tv_pov`, `sofa_back`, `kitchen`, `table`, `door`.

### park

Marks: `bench_1`, `bench_2`, `swing_1`, `swing_2`, `slide_top`, `slide_bottom`, `sandbox`, `pond`, `fountain`, `path`, `gate`.

Cameras: `wide`, `playground`, `swings`, `pond`, `bench`, `fountain`, `gate`.

### school_front

Marks: `gate`, `steps`, `yard`, `bus_stop`, `bus_door`, `crossing`, `sidewalk`.

Cameras: `wide`, `gate`, `steps`, `bus_stop`, `bus`, `crossing`, `yard`.

### downtown

Marks: `crossing_L`, `crossing_R`, `sidewalk_L`, `sidewalk_R`, `screen_watch`, `cafe_door`, `bank_door`, `taxi`.

Cameras: `avenue`, `skyline`, `crossing`, `screen`, `corner_wide`, `sidewalk`, `cafe`.

## The cast

The eight recurring people (Nia, Teach, Tall, Boy, Dad, Gran, Kid, Man) stay in `town.py`. Do not change their colours, hair or clothes. `cast.py` adds people an episode asks for:

- `cast.get(name)` builds an extra once: `doctor`, `watchman`, `baker`, `postman`, `driver`, `guard`, `delivery`, `baby`, `jake`, `remy`.
- `cast.role(name)` dresses a recurring person: `mayor` (Dad), `nurse` (Teach), `ice_cream_man` (Man), `mailman` (Dad).
- `cast.crowd(spots)` builds one random person per spot.
- `cast.names()` lists the library.

A new person who will appear again goes into `cast.py`, not into one episode file.

## A new place

Add `blockworld/places/<name>.py` with `GEO`, `build(**geo)` and `dress(p, **words)`. `build` returns `{"marks": {...}, "cams": {...}}`. Park an indoor place on the next free y (−1060, then −1160). Park an outdoor place on the next free plot (4000, then 5000), 1000 studs from its neighbour, or a wide camera will see both. Add a section to this file in the same change.

Building is the normal path. `town.prim()` makes the street in about 2.5 seconds, which is faster than loading a saved copy. A place can set `CACHE = True`, or the episode can set `BT_PLACE_CACHE=1`, to save `places/cache/<name>-<hash>.blend`. The cache is not committed. Change the place's code, or a kit file it is built from, and the next run rebuilds it.
