# World v2 (branch `world-v2`)

A richer town, more expressive faces, dressed characters, a camera pack and a film-like picture. Old episode code runs
unchanged and gets the new look; the new pieces are opt-in calls.

World v2 was made on branch `world-v2` (folder `block-town-video-v2`, a git worktree) and merged into `main` on
2026-11-13, together with the research / five ideas / opening variants / draft-and-final flow from `roblox-look`.
`build_town(..., detail=False)` and `TJ_QUERY="post=0"` still give the v1 street and picture (see Switches).

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
