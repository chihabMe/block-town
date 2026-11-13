# Rendering: Three.js, the life layer, tags and pictures

## Why Three.js

Blender EEVEE drew each 1080x1920 frame in 3-6 s on the laptop this was made on (32 samples, raytracing): a 66 s
episode took about 3 hours. Three.js draws the same frame in about 10-20 ms on the same laptop; with saving the JPEG it
is 0.1-0.15 s a frame. Measured on ep05: the same 5 s looked nearly identical (PSNR 25-30 dB against Blender), with
slightly lighter shadows and a little less bounce light in corners.

Nothing was rebuilt for Three.js. Blender still builds the town and runs every shot function; it only stops rendering.

## How it works

`render_threejs.sh EPISODE [F0 F1]` runs two steps:

1. **Bake (Blender, `blockworld/threejs/bake.py`).** It runs the episode's normal render loop, but where a frame would
   be rendered it records every object's world matrix, visibility and material slots, plus the camera, sun, key light,
   sky colours, glow strengths and street lamps. On the first frame it exports the geometry (`scene.glb`, Z up, text
   converted to meshes); on the last it writes `materials.json` (a recipe per material) and `anim.json` + `anim.bin`
   (the moving objects' matrices, float32). About 1 minute to build the town, then about 0.1 s a frame.
2. **Draw (Three.js, `blockworld/threejs/scene.html` via `capture.mjs`).** Headless Chrome loads the bake, rebuilds every
   material from its recipe, and for each frame sets the matrices, the camera, the sun and its shadow box, the sky,
   then renders twice: the world, then (on top, after clearing depth) the tags and bubbles. Frames go to
   `EPISODE/frames/f_####.jpg`, numbered from F0, so a partial render drops into place.

### Materials Three.js understands

`bake.py` reads each Blender material's node tree and writes a recipe. Three.js rebuilds:

| Recipe | Blender material | Three.js |
|---|---|---|
| `flat` | a colour (with roughness, specular level, glow) | MeshStandardMaterial |
| `banded` | `banded()` clapboard siding (world-Z stripes) | a shader stripe |
| `brick` | `brick()` (Blender brick texture) | a shader brick pattern |
| `decal` | faces: skin colour + face picture by alpha (UV, or the Roblox-look head projection) | a shader decal |
| `multiply` | printed clothes (`print_mat`) | colour x picture |
| `image` | a picture on a UV quad (paper, posters) | map |
| `emit_img` | a lit picture (`lit_picture`: phone screens) | emissive map, black base: exact colours |

A material the bake can't read shows as its base colour and is counted as `missing` in the `CHECK` line. If you write
a new shader in Blender, either keep it to one of these shapes or add a recipe to `bake.py` and `scene.html`.

What is **not** carried over: fog and rain (the roblox fog/rain hooks), animated text bodies (a text object's words
must not change during a span: use two cards and swap them), and image changes on a material (swap the material
instead, as faces do).

### Speed and memory

- 66 s ep05: bake 5.5-6.5 min, draw 3-5 min, finish 1-2 min.
- `anim.bin` is about 75 MB for 66 s (600 moving objects). Fine; keep longer videos in one file anyway.
- Something else rendering at the same time (another Blender, a big Chrome) slows everything and can stall the bake
  for minutes on a 14 GB machine. Render one thing at a time.

## The life layer (`blockworld/life.py`, `BT_LIFE=1`)

Added on top of every shot after the shot function runs, so shots never need to be rewritten for it:

| Part | What moves |
|---|---|
| characters | breathing (squash/stretch), weight shift, glances and nods, arm sway, a squash-and-settle on every cut |
| camera | a tiny handheld wobble, a 7 % punch-in at every cut, a slow creep in |
| scene | trees sway, clouds drift |
| props by tag | `"spin"` spinner dots turn, `"pulse"` Wi-Fi rings ripple, `"bar"` lit signal bars bounce, `"xmark"` the X throbs |
| cards | tags and bubbles float; they are lifted above hair, kept inside the safe area, and drawn on top of everything |

`BT_LIFE_AMOUNT=0.5` (calmer) to `1.5` (livelier) scales it all. Give a new prop one of the custom properties above
and it moves the same way (see `rprops.big_phone`, `rprops.bars`, `rprops.wifi_tower`).

Safe area for tags: x 5-85 % of the width (TikTok's buttons are on the right), y from 40 % (above the captions at
about 34 % from the bottom) to 93 %. Hearts (`♥` cards) are left where the shot puts them.

## Tags, bubbles and tokens

- Make cards once before the shots (`card`, `bars`, `bar_token`), show them with `put(card, loc, k)` inside a shot.
  Every frame starts with all cards hidden.
- Over a head: `put(tag, over(c, 0.4), 0.55)`. The life layer lifts it if the character's hair reaches higher.
- Two tags in one shot: keep them apart yourself (the layer does not move tags away from each other yet).
- To show something being given, lost or counted, move the thing: `bar_token(i)` flies out of a `bars` tag; swap
  `bars(4) -> bars(3) -> ... -> bars(0, x_mark=True)` as it empties (ep05 s34).

## Pictures on props (`blockworld/pictures.py`)

Phone screens, the hand-held lock screen and the paper map are drawn pictures, not 3D text:

```json
{
 "search": {"kind": "wifi_search", "status": "Searching...", "hint": ["No networks found nearby", "Be nice to get signal"]},
 "call": {"kind": "calling", "name": "Grandma", "who": "gran"},
 "signal": {"kind": "hotspot", "big": "100%", "count": "312 phones", "names": ["Grandma's tablet"], "more": "+ 311 more"},
 "msg": {"kind": "chat", "name": "Grandma", "who": "gran", "bubbles": [["time", "6:02 PM"], ["text", ["Hi!"]], ["hearts", 21, "x47"]]},
 "warn": {"kind": "notice", "title": "Wi-Fi", "big": "0 BARS", "lines": ["You were rude", "to a grandma"]}
}
```

Save it as `EPISODE/pictures.json`, run `python3 -I SKILL/blockworld/pictures.py EPISODE`, look at the PNGs, then use
them: `big_phone(x, -380, 8, screen="search")`, `paper_map("map")` (the kit's map, or your own `town_map` entry),
`picture_quad(...)` with `lit_picture(name)` (glows) or `paper_picture(name)` (printed) on any prop. Kinds and options
are in the file's docstring. Add a new kind there (a Python function drawing on 1080x2216) when a story needs one.

Rules that came from review:
- A phone screen is lit: `lit_picture` (black base, emission = the picture) so light greys don't wash out.
- Phone pictures on hand-held phones are flipped (`flip=True` in `phone_in_hand`): the hand turns the phone over.
- A printed map is held at chest height, tilted back ~30 degrees, so the face stays in view and the map stays above
  the captions.
- Big phones have a hand (`hand="#C98A5A"`, Max's skin): a floating phone in the sky looks fake.

## Comparing with Blender

`BT_TJ_REF=1 BT_FRAME_DIR=/some/dir blender ... -P SKILL/blockworld/threejs/bake.py -- EPISODE render F0 F1` also
renders the Blender frame for each baked frame, for side-by-side checks.
