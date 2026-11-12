# The Roblox look: the world, the cast, the props, the shots

Everything here is built in code from rounded boxes and spheres: no Roblox models, catalog items or footage.
`examples/ep05-wifi` uses every piece on this page; read its `episode.py` next to this file.

## 1. Start an episode

```python
import sys
from anim import *                       # town, cast, pose, shot, cards, stand, walk, run, word helpers
from roblox import giant_clock, puddles, rule_sign
from rprops import bars, big_phone, phone_in_hand, poster, sash, top_hat, wifi_tower   # what you need

build_town("BE NICE", ("SIGNAL SHOP", "NICE CAFE"), style="roblox")   # rule for the billboard, two shop signs
...                                                                    # landmark, signs, props, extra people, cards
run(SHOTS, tod="sun")                                                  # mood: sun, fog, rain, dusk, night
```

`finish.json` in the episode: `{"captions": "karaoke", "music_loop": 20.5, "music_db": -9}`.

## 2. The world (units are studs; 1 stud = 1 foot on tags; an adult is 5.3 studs)

```
y = 190   TOWN HALL (end of every view down the street)
          landmark: put it on the road at x = 0, y = 120–150
          house rows at y = -60, -30, 0, 30, 60, 90, 120, 150; shops at (36, 30) right and (-36, 90) left
x:  -36 houses | -27..-21 lawn | -21..-12 sidewalk | -12..12 road | 12..21 sidewalk | 21..27 lawn | 36 houses
          LAMP POSTS at x = ±13.6 and TREES at x = ±23.6, at y = -45, -15, 15, 45, 75, 105, 135, 165
```

| Where | z of the ground | Constant |
|---|---|---|
| Road | 0.1 | `ROAD` |
| Sidewalk (centre lines x = ±16.5) | 0.5 | `WALK`, `RX`, `LX` |
| Lawn and in front of shop doors | 0.0 | |

**Lamp posts and trees are the most common thing in front of a face.** Stage people between them (y = 20–40,
50–70, 80–100 …) or move the camera so the post is behind it.

Moods (`run(..., tod=...)`, or `time_of_day("dusk")` as the first line of one shot, for a flashback):

| Mood | Use | Cost per final frame |
|---|---|---|
| `sun` | comedy, most episodes | ~3.5–4.8 s |
| `fog`, `rain` | scary; rain falls and the road is wet | ~6.6 s |
| `dusk`, `night` | flashbacks, night scenes | ~4–5 s |

## 3. The cast

The eight recurring characters are rebuilt in this look automatically (same colours, hair and clothes). Give them
names and jobs per episode; never change their looks. `character(...)` makes new people in the same look and takes
`top="jacket" | "hoodie" | "shade"` and `legs="jeans" | "legs"`.

| Name in code | Look | Roles so far |
|---|---|---|
| `NIA` | yellow hoodie, black pigtails | friend, neighbour |
| `TEACH` | purple striped top, brown bun | teacher, "nice people" |
| `TALL` | green shirt, spiky ginger hair | the rude one, bully |
| `BOY` | red shirt, blue cap | the hero (Max in ep05) |
| `DAD` | blue shirt, red tie | dad; the mayor with `sash(DAD)` + `top_hat(DAD)` |
| `GRAN` | pink striped top, grey bun | grandma |
| `KID` | orange shirt, red beanie (small) | little kid |
| `MAN` | dark shirt, spiky hair | the stranger, the one punished first |

Faces (`pose(c, face=...)` or `stand(c, loc, yaw, face, T)`): smile, happy, laugh, stern, angry, determined, sad,
scared, shock, smug, sleepy, glasses. Swap the face on the key word.

## 4. Props and tags

| Piece | From | Notes |
|---|---|---|
| `rule_sign(x, y, big, small, yaw)` | `roblox` | The official red-and-white rule sign. Keep its text above the caption band |
| `giant_clock(...)`, `wifi_tower(x, y)` | `roblox`, `rprops` | Example landmarks. A landmark is big, simple, one strong colour, and **is** the rule |
| `bars(n, x_mark)` | `rprops` | Signal bars over a head (any "level" or counter). Show with `put(tag, over(c, 0.4), 0.55)` |
| `card(lines, size, colour)` / `card(lines, size, bubble=True)` | `anim` | Glowing text tags ("4K", "FROZEN: 3 DAYS") and speech bubbles |
| `phone_in_hand(c)` | `rprops` | Look at it: `armR=(72, -8), head=(0, -10)` |
| `big_phone(x, y, z, lines, bars_on, spinner)` | `rprops` | Insert shots of a screen. Put each one far away (`y = -380`) |
| `poster(x, y, z, face, skin, lines, cap)` | `rprops` | A face poster (wanted, meanest kid, missing) |
| `sash(c, "MAYOR")`, `top_hat(c)`, `hivis(c)` | `rprops` | Costumes |
| `bus`, `door`, `hand_box`, `beam`, `pigeon` | `rprops` | A bus, an opening shop door, a box held out, a glowing beam, a bird |
| `puddles([...])` | `roblox` | For rain shots |
| `car(...)`, `pole_sign(...)` | `props` | From the block kit; they turn plastic in this look |

New props: build them in the episode (or `rprops.py` if they are reusable) from `rbox`, `blob`, `cone`, `disc` and
`plastic` / `glow`, then show one design still before using them.

## 5. Making shots

A shot is `def name(t, d, T)`: `t` = seconds into the shot, `d` = its length, `T` = seconds into the video. List them as
`SHOTS = [(name, wcut(i), fn), ...]`, the first at `0.0`.

```python
def s16(t, d, T):                        # "My name is Max, and I have zero bars."
    stand(BOY, (RX, 36, WALK), 0, "smile" if T < WT[84] else "sad", T)
    closeup(BOY, dist=9.5 - 0.9 * t, fov=46)          # slow push-in
    put(TMAX, over(BOY, 1.5), wpop(80))               # "MAX" pops on word 80
    put(BX, over(BOY, 0.4), 0.55 * wpop(84))          # the zero-bars tag pops on "zero"
```

- **Close-ups with a tag above the head** need `closeup(c, dist≈9.5, fov≈46)`, with the tag at `over(c, 1.5)`.
  At `fov 36` the tag is outside the frame.
- **Inserts**: `shot((x + 0.3, y - 18 + t, z + 0.3), (x, y, z), 42)` on a `big_phone` or a poster.
- **Wide shots** of the landmark come back every 6–10 shots.
- **The camera always moves** a little (push in, drift, crane), and every shot starts 0.04 s before its word.
- **Props that appear or disappear** (a poster that goes up on a word, a box held only in one shot): reset them in a
  function registered with `before_each_frame(fn)`, so every frame starts from the same state.
- **Tags, bubbles and cards** are hidden at the start of every frame; show them again in each shot that needs them.
- **Speech bubbles** sit at `over(c, 0.5–0.9)`; a bowing or leaning character needs a lower one (`over(c, -0.6)`).

## 6. Check the stills against this list

- Is the face (or the object the line is about) clearly visible and not cut by the frame edge?
- Is anything in front of it: a lamp post, a tree, a bus, a sign, another person, a raised arm?
- Can every tag and sign be read, and is sign text above the caption band (top 62% of the frame)?
- Does the picture show the words being said at that moment?
- Is the landmark visible in the first 2 seconds?

## 7. Mistakes already made (do not repeat)

- A bus parked near the landmark blocked five landmark shots: keep big props away from the landmark's sight lines.
- Lamp posts at y = 45 and 75 stood in front of a crowd and of a two-person scene: see the map above.
- Text tags at `over(c, 2.0)` in tight close-ups were out of frame: widen the shot (section 5).
- A door opened toward the camera hid the hero: open doors away from the camera.
- An arm held toward the camera covered the face: raise arms outward, or toward the side away from the camera.
- Camera inside a prop or behind a character's shoulder looks like blobs: keep 1+ stud between the lens and anything.
