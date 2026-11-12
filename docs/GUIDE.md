# Animation guide: the block-style "In this town" video

**What this is.** The manual for building a video in our block look: the town, the people, how they move, how the
camera moves, and how a script becomes shots. With this guide, **an idea and a script are enough to build the video**.
The paste-ready prompts are in [`PROMPTS.md`](PROMPTS.md). This guide is the block look; the Roblox look (round heads, printed clothes, fog and rain) is in [`ROBLOX_LOOK.md`](ROBLOX_LOOK.md) and uses the same map, moves and camera rules.

**Where the rules come from.** Every number here is taken from the first accepted test of this look
(11 s, 9 shots, 2026-11-11), which is now `examples/ep01-intro`. The look reference was a public block-style video
used for study only: never reuse its footage, story or ideas, and never use Roblox catalog items.

**Status.** The user's verdict on the intro: "ok, not perfect yet". Section 12 lists what is not good enough yet.
When a look decision changes, change it here first, then in the code.

---

## 1. The look in ten rules

1. **Free and offline.** Blender (Eevee) + local Kokoro voice + local sound effects. No paid tools, no asset kits.
2. **Everything is built from code** out of plain boxes. No downloaded models, no Roblox catalog items.
3. **People are six sharp blocks** (head, torso, two arms, two legs) with a square head, chunky box hair and a flat
   drawn face. No bevels, no fingers, no elbows or knees.
4. **The town is quiet, the people are loud.** Walls are muted colours; clothes, signs and tags are saturated.
5. **One straight street.** Clapboard houses with dark roofs and yellow windows, brick shops with lit signs, a town
   hall at the end, a billboard that carries the rule, low-poly trees, black streetlamps, flat blue sky, puffy clouds.
6. **Poses hold, then snap.** A character holds one clear pose, then jumps to the next in 0.14 s on a spoken word,
   and the face changes on the same frame. Nothing eases slowly, nothing fades.
7. **Nothing is ever frozen.** A held pose still breathes, and the camera drifts in every shot.
8. **A new shot every 1–2.5 s**, cut 0.04 s before a spoken word. The picture shows the exact words being said.
9. **One word of caption at a time**, yellow with a black outline, at 66% of the frame height.
10. **Vertical 1080×1920, 30 fps.** No music in the file ("Numbers" by TEMPOREX is added in TikTok).

---

## 2. Where the code lives

The kit is this skill. Paths below are relative to the skill folder (the folder that contains `SKILL.md`).

| File | What it does |
|---|---|
| `blockworld/town.py` | Materials, boxes, text, the eight characters, the street, light, camera |
| `blockworld/anim.py` | Word timing helpers, tags, `stand`, `walk`, and the check / stills / render loop |
| `blockworld/props.py` | Ready-made set pieces: car, pole sign, height wall, shoebox |
| `blockworld/run.py` | Opens an episode inside Blender. Episodes are not run directly |
| `blockworld/vo.py` | Narration (Kokoro blend) into `vo/voice.wav` |
| `blockworld/words.py` | Lines `script.txt` up with the narration → `vo/times.json` |
| `blockworld/finish.py` | One-word captions, sound effects, the final file |
| `blockworld/faces.py` | Draws a new face. `python3 blockworld/faces.py blockworld/faces` |
| `examples/ep01-intro/episode.py` | The intro. Copy this folder to start an episode |

**Starting a new episode.** Copy `examples/ep01-intro` to a new folder. Replace `script.txt`, `episode.py` and `cues.json`. Keep `vo_config.json` unless the voice should change. Dress the street with `build_town(rule_big, shop_signs)` inside the episode file. Do not edit the cast colours or the street layout in `town.py` for one episode.

`examples/ep01-intro` is that first test, moved into this kit. New episodes start by copying that folder.

## 3. The world

### 3.1 Units and map
Units are **studs**. In tags, **1 stud = 1 foot**. A normal adult is 5.3 studs tall.

```
                     y = 190   TOWN HALL (84 wide, 30 tall, 6 white columns, red clock)
                        ▲ "down the street" = +Y
   houses  lawn  sidewalk   road    sidewalk  lawn  houses
   x=-36  -27..-21 -21..-12 -12..12  12..21  21..27   x=36
                        │
            house rows at y = -60, -30, 0, 30, 60, 90, 120, 150
            a tree (x = ±23.6) and a lamp (x = ±13.6) between houses, at y + 15
```

| Thing | Value |
|---|---|
| Road | 24 wide, top at z = 0.1, yellow centre dashes, runs y = −200…320 |
| Sidewalks | 9 wide, top at **z = 0.5** (`WALK`), centre lines at **x = ±16.5** (`RX`, `LX`) |
| House | 24 wide, 18 deep, 15 tall + a 7–9 roof, front wall at x = ±27, door and 5 windows facing the road |
| Shop | 26 wide, 14 tall, brick, striped awning, lit sign. Now at (36, 30) and (−36, 90) |
| Billboard | Panel 19.6 × 10.6 on two posts, title + big line + a ruler strip. Now on the shop roof at (31, 30, 14) |
| Town hall | At y = 190, facing back down the street. It ends every down-the-street view |

A character standing on the sidewalk is at `(±16.5, y, 0.5)`; on the road at `(x, y, 0.1)`.

### 3.2 Building kit (functions in `blockworld/town.py`)
| Function | Makes |
|---|---|
| `box(size, loc, material, parent, rot)` | One block. Everything is made of these |
| `mat(hex, emit)` | Flat matte colour (roughness 1, no shine). `emit` makes it glow |
| `banded(hex, dark)` | Clapboard wall: thin darker lines every 0.67 studs |
| `brick()` | Brick wall |
| `text(body, size, loc, material, parent, rot, extrude)` | 3D text (DejaVu Sans Bold) for signs |
| `house`, `shop`, `billboard`, `town_hall`, `tree`, `lamp`, `clouds`, `ground` | The street pieces |
| `empty(name, loc, parent)` | An invisible parent, so a whole prop moves and turns as one |

### 3.3 Colours
| Use | Colours |
|---|---|
| House walls (muted, 6) | sage `#7C8C7A`, slate `#5F6F86`, sand `#C9B98A`, mauve `#8D6F8F`, teal `#6E9AA6`, clay `#B9826A` |
| Roofs, poles, dark trim | `#22232B`, `#15161B` |
| Windows (glow) | `#F7CE6E` |
| Ground | grass `#4E9E3C`, road `#26262C`, lane dashes `#F5C52A`, sidewalk `#C3C6CE` |
| Brick | `#A8432F` with pale mortar |
| Signs | navy board `#1B1F3A`, gold frame `#F5C52A`, glowing text `#FFD84A`, white `#FFFFFF` |
| Tags | good/tall green `#5BE36B`, bad/short red `#FF4B40`, loss red `#FF3B30`, neutral yellow `#FFD84A` |
| Sky (day) | horizon `#BDE4FA` → top `#5CB6F2`, white clouds |

Rules: every colour goes through `lin()` (sRGB → linear) or it renders washed out. View transform "Standard", look
"None", exposure 0. New props use the muted wall colours or greys; only signs, tags and clothes are saturated.

### 3.4 Time of day
`L.time_of_day("day" | "dusk" | "night")`, called inside a shot function when the mood changes.

| Mode | Use it for | Look |
|---|---|---|
| day | The rule, world-building, comedy, wins | Blue sky, warm sun, soft shadows |
| dusk | Sad or worried beats, "then one day…" | Grey-purple sky, windows glow, lamps on low |
| night | Danger, secrets, horror, the twist | Deep blue sky, lamps and windows bright, no clouds. Pass `key_w=400…900` to `shot()` so faces are lit |

### 3.5 Dressing the town for an episode
The street stays the same in every episode. Each episode changes only this:
1. **The rule billboard**: title "TOWN RULE" + the rule in 3–5 words ("1 LIE = 1 INCH").
2. **Two shop signs** that joke about the rule ("TALL & SMALL", "HONEST PIES").
3. **Two to five set pieces** that the script names (ep01 intro: a HEIGHT CHECK ruler wall, a car lot sign, a red
   car, a shoebox house). Put them at different y positions so shots do not see each other's props.
4. **In-world numbers** as tags (heights, prices, balances), never inside the caption.

### 3.6 Building a new prop or place
- Boxes only (a cylinder is allowed for wheels). 5–25 parts. One `empty` parent, parts in the parent's own
  coordinates, the front on the parent's −Y side.
- Size it against a 5.3-stud person before anything else. Door 6.4 tall, car 4.6 × 10 × 4.2, sign text 1–2 studs.
- One readable idea per prop: a big sign or one strong shape. If it needs text, max 3 words per line.
- Put the prop on a sidewalk or the road, turned to face the camera position planned for its shot.
- For props that are turned, place characters and the camera in the prop's own coordinates (see `box_pt()` in
  `episode.py`); guessing world coordinates around a rotated prop put the camera on the wrong side once.
- Render one still with a person next to it before using it in a shot.

**Not built yet** (build when a script needs it, show a still first): rooms and interiors (bedroom, classroom, shop
inside), a phone or screen prop, vehicles that drive, doors that open, water, rain, crowds over about 12 people.

---

## 4. The characters

### 4.1 Body
| Part | Size (studs) | Notes |
|---|---|---|
| Torso | 2 × 1 × 2 | Hips at z = 2.0 |
| Arm | 1 × 1 × 2 | Pivots at the shoulder, x = ±1.5. Short sleeve ends at 0.95, long at 1.62; the rest is skin |
| Leg | 1 × 1 × 2 | Pivots at the hip, x = ±0.5. The last 0.38 is the shoe |
| Head | 1.34 × 1.3 × 1.26 | A box. Pivots at the neck. Eye line is at z ≈ 4.6 |
| Whole | 5.3 tall | `scale` multiplies everything |

### 4.2 Design rules
- **Flat colours.** One shirt colour, one trouser colour, one skin colour, one hair colour.
- **Exactly one clothing detail**: stripes, hoodie strings, a tie, long or short sleeves.
- **One signature item for a main character**, readable at thumbnail size: pigtails with pink bands, a blue cap,
  a beanie with a bobble, glasses (a face), a red tie.
- **Shirt colours are spread around the colour wheel** so nobody is confused with anybody in a wide shot. The hero
  owns the brightest colour (Nia: yellow) and nobody else wears it.
- **Hair has volume**: a cap of boxes plus tufts, a bun, pigtails. Never a bare flat top (only the baby).
- Skin tones vary across the cast.
- Our own designs only: no Roblox faces, logos or catalog items.

### 4.3 Recurring cast (keep these identical in every episode)
| Name | Skin | Shirt | Trousers | Hair | Detail | Role |
|---|---|---|---|---|---|---|
| **Nia** | `#9A5B34` | yellow `#FFC533` hoodie | blue `#3D4C8A` | black pigtails, pink bands | long sleeves, white strings | the hero |
| Teacher | `#E4B58A` | purple `#8A4FB5` | `#2B2B3A` | brown bun | lilac stripes, "glasses" face | strict adult |
| Tall | `#F0C8A0` | green `#2FB58A` | `#2B3350` | ginger tufts | short sleeves | the honest, friendly kid |
| Boy | `#C98A5A` | red `#E23B3B` | `#1F1F27` | blue cap | short sleeves | the bully or rival |
| Dad | `#7A4A2C` | blue `#2F6FE0` | `#3A3A46` | black side part | red tie | parent, office man |
| Gran | `#EBC8A8` | pink `#E88BA8` | `#6A5A7A` | grey bun | white stripes | grandparent |
| Kid | `#F0C8A0` | orange `#F28A1E` | `#31406B` | red beanie | scale 0.8 | little brother or sister |
| Man | `#B97A4A` | dark grey `#3E3E48` | `#22222A` | dark tufts | long sleeves | any townsperson, the "example" person |

Episode extras so far: Baby (all skin colour, white trousers, one curl) and Sal the salesman (blue shirt, yellow tie).

### 4.4 Hair styles (`character(..., hair_style, hair_col)`)
`tuft` (spiky), `side` (side part), `long`, `bun`, `pig` (pigtails), `cap` (baseball cap, colour = cap), `beanie`
(colour = beanie), `curl` (baby). Hair colours by name: black, brown, dark, ginger, blond, grey, red, or any hex.

### 4.5 Faces (`faces.py`, 11 drawings)
| Face | Use when |
|---|---|
| `smile` | Neutral, walking, listening |
| `happy` | Joy, relief, laughing with someone (closed eyes, open mouth, blush) |
| `laugh` | Laughing **at** someone, mocking |
| `smug` | Lying, showing off, a bully before the fall |
| `stern` | Disapproval, a parent or teacher waiting |
| `glasses` | The same, for a character who wears glasses |
| `angry` | Rage, being caught, an argument |
| `sad` | Loss, loneliness, being left out |
| `scared` | Fear, danger close (zigzag mouth) |
| `shock` | The instant something happens (round mouth, pin pupils) |
| `determined` | The hero deciding to act |

Rules: every shot gives every visible face a fitting expression. The face changes on the same frame as the pose
snap. A new face is drawn in `faces.py` with its helpers (`eye_dot`, `eye_wide`, `eye_closed`, `brow`, `arc`,
`zigzag`, `blush`), added to `NAMES`, and shown on the sheet before use. Mouths do not move while the narrator
talks: the niche does not lip-sync.

### 4.6 Size
`size(c, s)` scales a character; `feet(s)` gives its tag text ("7 ft 5"). In ep01 size is the story (0.063 = 4 in,
0.11 = 7 in, 0.5 = 2 ft 8, 1.0 = 5 ft 4, 1.4 = 7 ft 5, 1.7 = 9 ft, 9 = a giant). In other episodes everybody is
1.0, children 0.8, and size is not touched. Camera distances scale with the character: a close-up of a 0.11-scale
person is 0.11 × the normal distance.

### 4.7 Making a new character
1. Reuse a recurring character if the role fits. Add a new one only for a named person the cast cannot play.
2. Pick: skin, a shirt colour nobody on screen has, trousers darker than the shirt, a hair style nobody on screen
   has, one detail, one signature item.
3. `character(name, skin, shirt, pants, hair_style, hair_col, sleeves, stripes, strings, tie, shoes, scale)`.
4. Render a still next to Nia and Man (front, three-quarter) and get it approved before animating.

---

## 5. Movement

### 5.1 The idea
The niche acts like a comic strip, not like a cartoon: **one strong pose per shot, a snap to a second pose on the
key word, and a camera that never stops**. Nothing is keyframed. Each frame is posed from code: a shot is a
function `f(t, d, T)` (`t` = seconds since the shot began, `d` = shot length, `T` = seconds since the video began).

### 5.2 `pose()` (all angles in degrees)
`pose(c, loc, yaw, face, armL, armR, legL, legR, head, lean, tilt)`

| Argument | Meaning |
|---|---|
| `yaw` | Which way the body faces. **0 = −Y** (toward the start of the street), 180 = +Y (toward the town hall), 90 = +X, −90 = −X |
| `armL`, `armR` | `(forward, outward)`. `armL` is the arm on the **viewer's left when the character faces the camera**. Forward 90 = straight ahead, 180 = straight up. Outward 90 = straight out to the side; negative = across the body |
| `legL`, `legR` | Forward swing. Negative = back |
| `head` | `(turn, look_up)`. Turn > 0 = toward the `armR` side. Look up > 0 = up, < 0 = down |
| `lean` | **< 0 leans forward**, > 0 leans back |
| `tilt` | Sideways lean, > 0 toward the `armR` side |
| `face` | A face name from 4.5 |

### 5.3 Timing helpers (`blockworld/anim.py`)
| Helper | Use |
|---|---|
| `cut(i)` | Start time of a shot: 0.04 s before word number `i` (0-based, counted in `script.txt`) |
| `WT[i]` | The time word `i` is spoken |
| `snap(t, t0, d=0.14)` | 0 before `t0`, then a fast move to 1 with a small overshoot. **Every pose change uses this** |
| `smooth(x)` | Soft 0→1 for camera moves over a whole shot: `smooth(t / d)` |
| `mix(a, b, k)` | Blend two numbers or positions |
| `osc(T, hz, amp, ph)` | A sine wobble, for breathing, waving and bouncing. Give each character its own `ph` |
| `stand(c, loc, yaw, face, T, ph, …)` | A held pose that breathes (arms ±2° at 0.5 Hz, head ±3°) |
| `walk(c, x, y0, way, T, face, ph, speed)` | Walk along the street (+1 or −1), 2 steps a second |
| `size(c, s, squash)` | Scale, with optional squash and stretch |
| `put(card, loc, k)` | Show a tag or bubble facing the camera, at scale `k` (use a `snap` for a pop) |

### 5.4 The move library (all used in the intro unless marked)
| Move | When | Recipe |
|---|---|---|
| **Breathe** | Any held pose | `stand(...)`, a different `ph` per character |
| **Walk** | Background life, entering | `walk(...)`: arms ±58°, legs ±48°, lean −8, side tilt ±7, bob 0.22, speed 4.5 studs/s × scale |
| **Snap to a new pose** | The key word of the shot | `k = snap(t, WT[i] - shot_start)`, then `mix(poseA, poseB, k)` for arms, lean and head; swap the face when `k > 0` |
| **Wave** | Greeting, "look at me" | Arm `(10, 140 + osc(T, 2.5, 18))`. Raise arms **outward**, not forward: a forward raise covers the face |
| **Proud announce** | A claim, a lie, a speech | One arm `(10, 138)`, the other `(20, 34)`, lean back 5, look up 10, `smug`, with a speech bubble |
| **Crossed arms** | Judging, sulking | Both arms `(46, -30)`, face `stern` or `angry` |
| **Look up in awe** | Something huge | `head=(0, 30)`, lean back 6, `shock`, one arm pointing `(128, 8)` (fine from behind or the side) |
| **Head turn** | Noticing, reacting | `head=(mix(26, -34, k), …)` on a snap |
| **Excited bounce** | Joy, impatience | Add `abs(osc(T, 1–2, 0.1)) × scale` to z |
| **Clap** | A baby, applause | Both arms `(58, -12 + osc(T, 3, 10))` |
| **Size change** | Shrinking, growing | Stretch 5% up before the word, snap to the new size in 0.16 s, squash 10% for 0.22 s, a decaying wobble on `tilt`, face → `shock`, camera shake, then a tag on the next word |
| **Giant steps** | A huge character | Steps at 1.3 Hz, `tilt = 5 × step`, arms out `(20 ± 14, 52)`, a camera thud on each footfall |
| **Hop out / hop over** | Entering from a door or box | Move over 0.3 s with `smooth`, add `sin(π × k) × 0.12` to z |
| **Point** (side views only) | Accusing, showing | Arm `(78, 10)`, lean forward. From the front it hides the face |
| **Cower** (look test only) | Fear | Arms `(-20, 24)`, lean forward 8, head down 8, `scared` |
| **Hands up** (not used in a shot yet) | Panic, cheering | Both arms `(10, 145)`: the tested wave, on both sides, so the face stays clear |

### 5.5 Feeling → pose and face
| Feeling | Body | Face | Camera |
|---|---|---|---|
| Lying, bragging | Chest out, lean back, one arm high | `smug` | Slow push-in |
| Caught, hit by the rule | Snap: arms drop, body wobbles | `shock` | Punch-in + shake |
| Proud, honest, kind | Upright, waving | `happy` | Low angle, looking up |
| Angry, jealous | Arms crossed, head turned away | `angry` → `stern` | Level, medium |
| Scared | Lean forward, arms tight, small bounce | `scared` | Close, slightly high |
| Sad, alone | `head=(0, -14)`, arms still, small in the frame | `sad` | Wide, dusk |
| Deciding to act | Feet apart, lean forward 4, head up | `determined` | Push-in from low |
| Laughing at someone | Lean back, bounce, one arm pointing | `laugh` | Over the victim's shoulder |
| Crowd reacts | Everyone the same pose, different phases, one outlier | `shock` or `happy` | From behind the crowd |

Rows that are not in the move library are starting points: check them on a still before animating.

### 5.6 Rules for every shot
- **One event per shot**, on a spoken word: a pose snap, a tag pop, an entrance, a size change.
- **Something moves in every frame**: breathing on every character, a drifting camera, a bounce or wave on one.
- **Readable silhouette**: arms away from the face and torso, characters not overlapping, the hero unobstructed.
- **Two or three characters act; the rest breathe.** Background people never do something bigger than the lead.
- **No slow blends.** Poses change in 0.14–0.16 s or not at all. Only the camera moves smoothly.
- Characters off duty are parked far away each frame (the `frame()` loop does it), so set every visible character's
  place, size and pose inside the shot function.

**Not built yet** (build and show a test first): sitting, running, falling, carrying or holding things, hugging,
crying, turning around while walking. There are no elbows or knees, so these need to read from the pose of whole
limbs and the lean of the body.

---

## 6. Camera and light

### 6.1 Lenses
`shot(pos, target, fov, key_w=0)`. The sensor fits vertically, so `fov` is the **vertical** angle.

| Shot size | fov | Distance for a 5.3-stud person | Use |
|---|---|---|---|
| Close-up (face) | 30–44 | 5–8 studs from the face | Reactions, the key emotion |
| Medium (one or two people) | 46–56 | 10–15 studs | Talk, gestures, tags over heads |
| Wide (street, crowd, giant) | 56–70 | 40–90 studs | The world, scale, crowds |

Frame height at distance `d` = `2 · d · tan(fov / 2)`; frame width = 0.5625 × that. The frame is narrow: at 12
studs and fov 50 it is only 6.3 studs wide, so **two people must stand within about 3 studs of each other**, and
trees or lamps beside them will crowd the frame.

### 6.2 Proven camera set-ups (from the intro)
| Set-up | Camera | Aim | fov |
|---|---|---|---|
| Aerial street opener | `(8, −52, 52)` → `(6, −30, 40)` | `(0, 80, 6)` | 56 |
| Person at a wall (stands at x = 19.3 facing −X) | 10 studs out, z 3.7 | chest-to-head, z 4.9 | 50 |
| Reaction punch-in | 6.7 studs out, z 4.7 → 4.3 | z 5.0 → 4.5 | 42 |
| Line-up dolly | 12 studs out, z 3.3, slides 13 studs sideways | 0.6 ahead of the camera, z 3.9 | 56 |
| Low-angle two-shot (tall vs small) | 15 studs out, **z 1.5** | z 6.0 | 54 |
| Giant from the ground (scale 9) | on the road, z 2.4, about 95 studs away | z 19 → 24 | 60 |
| Face close-up | 8 studs from the face, 0.6 to one side | just under the eyes | 34–36 |
| Tiny thing (scale 0.11) | 6 → 3 studs out, z 1.7 → 0.8 | the tiny head | 38 |

### 6.3 Camera moves (one per shot, always)
| Move | Recipe |
|---|---|
| Push-in (default) | Camera position `mix(a, b, smooth(t / d))`, moving 5–20% closer |
| Dolly along a line | Slide camera and aim together |
| Crane down | Start high and far, end lower and closer (the opener) |
| Punch-in | On the key word, `mix(camA, camB, snap(...))` to a closer position |
| Shake | Add `exp(-6·dt) · sin(40·dt) × 0.12–0.16` studs to the camera after an impact |
| Footfall thud | Add `abs(step) ** 6 × 0.25` to camera z under a giant |

### 6.4 Framing for TikTok
- Captions sit at 60–72% of the height. **Faces, tags and bubbles go in the top 55%.**
- Nothing important in the bottom 20% or the right 15% (TikTok buttons and text).
- Eyes on the upper third. Leave head room for a tag (0.8 studs above the head at scale 1).
- Never cut between two shots of the same size and angle; change size or side on every cut.
- Scene changes get a whoosh sound, not a visual transition. Cuts only.

### 6.5 Light
`shot()` always brings the sun from behind the camera's left, so faces are lit from any angle. At night add the
camera's own lamp with `key_w` (420 for a close-up, 900 for a group). Eevee with ray tracing, 32 samples for final
frames, 12 for stills. No motion blur, no depth of field (the tiny-scale shots would be the first place to try it).

---

## 7. From script to shots

### 7.1 Timing comes from the voice
1. `script.txt`: one sentence per line. Word numbers are 0-based over the whole file, split on spaces.
2. Narration → `vo/voice.wav` → whisper word times → `vo/words.json`. The word count must equal the script's.
   If it differs, find where it drifts (numbers, "$10", hyphens, quotes) and fix those tokens by hand; never shift
   the whole list.
3. Every shot starts at `cut(i)` for the word that names its picture.

### 7.2 Cutting rules
- **One shot per clause.** A new picture each time the narrator names a new thing.
- **Hook (first 12 s): 0.7–2.0 s per shot.** The intro has 9 shots in 11.1 s (0.8, 1.0, 1.2, 1.0, 1.9, 1.5, 1.2,
  0.7, 1.6 s).
- **Story: 1.2–2.5 s per shot.** Never over 2.5 s. A longer line gets a second angle or a punch-in.
- A full 125 s episode is about 70–90 shots. Reusing a staging with a new camera angle counts as a new shot and
  is cheap; a new place or prop is expensive.
- The first shot shows the whole town and the rule within the first second.
- The last shot holds its final pose for 0.5 s after the last word.

### 7.3 What each kind of line looks like
| Script beat (from `PROMPTS.md` prompt 2) | Picture |
|---|---|
| 1. The rule ("In this town, …") | Aerial street with life → the rule happening to one person, with a tag for the number |
| 2. "You see," + consequences | One gag per shot: a line-up, a winner next to a loser, the most extreme case, each with a sign or tag |
| 3. The underdog ("My name is …") | Hero close-up with a name tag, then a wide that shows why the rule hurts them |
| 4. Personal stakes | The loved one, in a new place, at dusk; two-shot; the threat shown as an object or sign |
| 5. Exploit in 3 steps | The same staging three times, closer each time, a tag with the new number on each |
| 6. Pushback / cost | Authority figure from a low angle, crowd turning, night |
| 7. The twist | Stop the bustle: one slow push-in on one object or face, then the reveal on a snap |
| 8. Button | The callback object from beat 3, hero's final face, hold 0.5 s |

### 7.4 The shot plan (write this before any code)
One row per shot, approved before building:

| # | Cut word | Words covered | Place | Who (size, face) | Start pose → event on word → end pose | Camera (size, set-up, move) | Tag / bubble | Sound |
|---|---|---|---|---|---|---|---|---|

The intro's plan, as the model:

| # | Cut word | Words | Picture | Event | Camera |
|---|---|---|---|---|---|
| 1 | In | In this town, | Street from above, 9 people of different sizes walking | – | Wide, crane down |
| 2 | every | every lie you tell | Man at the HEIGHT CHECK wall, teacher watching | "lie": arm up, bubble "I NEVER LIE!" pops | Medium, push-in |
| 3 | makes | makes you one inch shorter. | Same man, closer | "one": snaps shorter, shock, shake; "inch": red "−1 INCH" | Close, punch-in |
| 4 | You | You see, everyone here is | 7 people along the wall with height tags | Two of them wave | Wide-ish dolly |
| 5 | exactly | exactly as tall as they are honest. | 7 ft 5 kid waves down at a 2 ft 8 boy | "tall": green tag; "honest": red tag, boy turns away | Low two-shot |
| 6 | Babies | Babies are the tallest people in town. | Giant baby toddles down the street, crowd looks up | Footfalls | Wide from the ground |
| 7 | They | They can't lie yet. | Baby's face | "can't": laughs, claps | Close-up |
| 8 | Car | Car salesmen | HONEST AL'S CARS lot, a red car | – | Medium, push toward the ground |
| 9 | live | live in shoeboxes. | A shoebox house on the sidewalk | Tiny salesman hops out, waves; "shoeboxes": tag "7 in" | Macro push-in |

---

## 8. Text on screen

| Kind | Made with | Rules |
|---|---|---|
| **Tag** (a number or name over a head) | `card(["7 ft 5"], size, colour)` + `put()` | Faces the camera. Yellow = neutral, green = good, red = bad. Pops with a `snap` on its word. 0.8 studs above the head. Size 0.6–0.85 at scale 1 so it reads on a phone |
| **Speech bubble** | `card(["I NEVER", "LIE!"], 0.62, bubble=True)` | Max 2 lines, 8 characters a line, CAPS. Only for a quoted line in the script |
| **Sign** (part of the world) | `text()` on a board | Max 3 words a line, glowing yellow on navy |
| **Caption** | `blockworld/finish.py` → ASS subtitles | One word at a time, yellow `#FFE23B`, black outline 11, Inter Display Black 112, centred at 66% height, a 0.13 s pop, no punctuation |

Each word changes at its spoken time minus 0.03 s. Numbers the story depends on appear **as tags in the world**, so
the caption stays one plain word.

---

## 9. Sound

**Voice.** Follow `docs/VOICE.md`. Current free setting: Kokoro blend `af_jessica:3,am_puck:2`, speed 1.3,
+3 semitones, about 250 words a minute. The rule line slightly slower (speed 1.22), pauses 0.18–0.28 s between
lines. If `voice_match.py` is available on the machine, score the final take and report the number (the intro scored 0.847; the bar for
"usable" is 0.85). Never clone the reference clips.

**Sound effects** (bundled with HyperFrames, free, offline: `~/.npm/_npx/*/node_modules/hyperframes/dist/skills/media-use/audio/assets/sfx/`):

| Event | File | Volume |
|---|---|---|
| Ordinary cut | `whoosh-short.mp3`, 0.1 s before the cut | 0.22 |
| Scene change, camera travel | `whoosh.mp3` / `whoosh-cinematic.mp3` | 0.32–0.38 |
| Bubble or small thing appears | `pop.mp3` | 0.5–0.55 |
| The rule hits, a big impact, a giant | `impact-bass-1.mp3` / `impact-bass-2.mp3` | 0.8–0.85 |
| A loss tag ("−1 INCH", red tag) | `pop.mp3` + `error.mp3` | 0.5 + 0.28 |
| A good tag (green) | `ping.mp3` | 0.4 |
| Delight, magic | `sparkle.mp3` | 0.32 |
| Also available | `chime`, `click`, `notification`, `riser`, `glitch-1…3`, `typing`, `key-press` | – |

One cue per event, on the word. Voice at 1.0, everything mixed and levelled to −14 LUFS. No music in the file.

---

## 10. Build steps (stop for approval after each)

| Stage | What is made | Shown for approval |
|---|---|---|
| 1. Plan | World sheet, cast sheet, shot plan for the whole script (prompts 2–4) | The three sheets, with 2–3 options where there is a creative choice |
| 2. Voice | `vo/voice.wav`, word times, match score | The audio and the score |
| 3. New designs | New characters, props, faces | One still each, next to a known character |
| 4. Stills | Two half-size stills of **every** shot (30% and 85% through) | A contact sheet |
| 5. Hook | The first 10–15 s rendered and finished | The clip |
| 6. Full render | All frames (in the background), captions, sound | The final file + the checklist in section 11 |

Commands (from the skill folder; `EP` is the episode folder):
```bash
# a new face, only when one was added (needs Pillow)
python3 blockworld/faces.py blockworld/faces
# narration, then word times
python3 blockworld/vo.py EP
python3 blockworld/words.py EP
# stills, then frames. Nothing here runs except through run.py
blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- EP check
blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- EP stills
blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- EP render
blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- EP resume
# captions only, then the final file once frames exist
python3 blockworld/finish.py EP --captions
python3 blockworld/finish.py EP
```

**Time and space.** About 4.5 s per final frame on this laptop: 2.3 minutes of rendering per second of video, so a
125 s episode is about 4.7 hours, run in the background. Frames take about 180 KB each (650 MB an episode); the
disk had 12 GB free on 2026-11-11, so delete old frame folders after the final file is approved. After a fix,
re-render only the changed frames (`frame = seconds × 30`).

---

## 11. Checks before showing anything

**Every still**
- [ ] Every face visible, lit, with the right expression; no arm, tag or prop covering it.
- [ ] Faces, tags and bubbles in the top 55%; nothing important in the bottom 20% or right 15%.
- [ ] The hero is the brightest, clearest thing; no lamp pole or tree in front of the subject.
- [ ] Tags readable at phone size; signs not cut by the frame edge.
- [ ] Nobody sinks into the ground or floats (sidewalk z = 0.5, road z = 0.1; a character's position is its feet).
- [ ] The picture shows the words being said in that shot.

**The cut**
- [ ] No shot over 2.5 s; every cut lands just before a word; no two neighbouring shots look alike.
- [ ] Something moves in every frame.
- [ ] Captions match the voice word for word; no punctuation; none hidden behind a tag.
- [ ] One sound per event; the voice is always clearly the loudest thing.
- [ ] Voice match score reported. No music in the file. No reference clip or downloaded footage in the file.
- [ ] Watched and **listened to** from start to finish before calling it done; say so plainly if it was not.

---

## 12. Not good enough yet (known gaps on 2026-11-11)

- **Voice**: closest free match only (0.847), not the niche voice itself. The likely real source is TikTok's or
  CapCut's built-in narrator; a test line exported from there can be scored.
- **Fonts**: signs use DejaVu Sans Bold and captions Inter Display Black. The reference uses a rounded cartoon
  font, which needs a download the user has to approve.
- **Bodies are stiff**: no elbows or knees, no sitting or running yet, hands cannot hold things.
- **One street only**: no interiors, no second location.
- **Small tags** in the line-up shot pass too fast to read.
- **Code layout**: the kit in this folder is the reusable code. New episodes copy `examples/ep01-intro`.

## 13. Mistakes already made once (do not repeat)

- Raising an arm **forward** covers the face from the front: raise it outward (`(10, 140)`).
- A body `tilt` on a giant swings the head out of a close-up: keep tilt near 0 in close-ups of big characters.
- A lamp pole or tree lands in front of the subject: check the still, move the camera or the people.
- Two people do not fit the narrow frame unless they stand within 3 studs: stage them close, or go lower and wider.
- Guessing coordinates around a rotated prop: use the prop's own coordinates.
- Blender's Python has no Pillow: faces are drawn by the system `python3 -I faces.py`.
- Hex colours not converted to linear look washed out: always `mat()` / `lin()`.
- Clouds lit by the sun turn grey at night: they are emission-only and hidden at night.
- Blender cannot pick a face from a `.ttc` font collection: use a `.ttf` file.
