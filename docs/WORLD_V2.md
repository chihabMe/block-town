# World v2

A richer town, more expressive faces, dressed characters, a camera pack and a film-like picture. Old episode code runs
unchanged and gets the new look. The places and the cast live in this same skill folder.

World v2 was built on branch `world-v2` and merged into `main` on 2026-11-13, together with the research, five ideas,
opening variants and draft-and-final flow. `build_town(..., detail=False)` and `TJ_QUERY="post=0"` still give the v1
street and picture (see Switches). The place list, marks and cameras are in `docs/PLACES.md`.

## What changed

| Area | v1 | v2 |
|---|---|---|
| Picture (`threejs/scene.html`) | plain render | contact shading (GTAO), glow on lit things (bloom), background blur (depth of field), distance haze, softbox reflections on the plastic, a wider and sharper shadow map, a light grade with darker corners |
| Town (`world2.py`) | bare street | bright houses with window frames, shutters, flower boxes, porches and chimneys; picket fences, paths, mailboxes, bushes and flowers; zebra crossings, hydrants, benches, bins, parked cars; a dressed town hall and shops; more trees (pine, blossom), a back row of roofs, hills all round, clouds in every direction |
| Faces (`rlook_tex.py`) | 12 small faces | 24 bigger faces with glossy eyes; new: `cry`, `wink`, `love`, `wow`, `dizzy`, `worried`, `evil`, `sideeye`, `shy`, `talk`, `proud`, `disgust`; everyone blinks (life layer) |
| Clothes (`roblox.py`) | plain shirt with folds | chest prints for the cast (star, number, dungarees, cardigan, shirt, open jacket, hoodie), collars and sleeve rims on everyone; 10 overlay prints for new characters (`top="tee_bolt"` ...) |
| Cameras (`shots.py`) | 7 presets | + `wide`, `extreme`, `pov`, `orbit`, `crash`, `dutch`, `top_down`, `follow`, `two_shot`, `whip`; `shot(..., roll=)` |
| Moves (`anim.py`) | stand, walk | + `sprint`, `fall`, `sit`, `clap`, `cheer`, `gasp`, `look_up`, `drum`, `juggle`, `magic`, `see_through` |

## Switches

- `build_town(..., style="roblox", detail=False)`: the plain v1 street and v1 clothes on this branch.
- Background blur: a shot that calls `focus(character)` blurs by distance on its own (close-ups a lot, wides not at
  all). `dof(0)` switches it off for a shot, `dof(1)` forces full blur.
- Renderer tests: `TJ_QUERY="post=0"` draws the plain v1 picture; `ao=0`, `bloom=0`, `dof=0`, `fog=0`, `grade=0`,
  `studio=0` switch one effect off. `TJ_ONLY=0,150,300` draws only those frames of a bake.

## Where the street stays clear

World v2 keeps props out of the lanes episodes use: the road between x = -8 and 8, and the sidewalk between
|x| = 14 and 19. Fences run at |x| = 21.7, benches and bins at |x| = 20, hydrants at |x| = 13.3 beside the lamp
posts, parked cars at |x| = 9.2 (y = -52, -28, 6, 172). `check` still reports anything within 1 stud of the lens.

## The world library

Places are modules in `blockworld/places/`. An episode calls `place(name, ...)` for each place the story uses, and the
others stay unloaded. `build_town(...)` is `place("street", ...)`. People who are not one of the eight recurring
characters come from `blockworld/cast.py` (`cast.get`, `cast.role`, `cast.crowd`). Marks, cameras, parking spots and
the words that change per video are in `docs/PLACES.md`.

Meshes come from unit templates (`town.prim`), not one primitive call each. The street builds in about 2.5 seconds.
Saving a place to `places/cache/` is off, because building is faster than loading. `BT_PLACE_CACHE=1` turns the cache on.
