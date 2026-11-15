# Movement, creatures, effects and overlays

These modules extend the existing episode API. `from anim import *` exports their public helpers.
Build characters, props and creatures once, then pose them inside each shot function on every frame.

| Module | Features |
|---|---|
| `moves.py` | `dance`, `big_jump`, `panic`, `knock`, `point`, `hug`, `float_up`, `sink`, `tumble`, `run_pose`, `crowd_run` |
| `creatures.py` | `monster` and its poses, `penguin`/`waddle`, `frog`/`hop`, `lion`/`trot`, `swarm` |
| `fx.py` | `sparks`, `confetti`, `money_rain`, `poof`, `fire`, `ring`, `beam`, `flashback`, `flash` |
| `overlay.py` | `label`, `icon`, `pop`, `comic`, `timecard`, `hud`, `endcard` |
| `anim.py` | `mocap` playback of converted pose clips |

Each module's opening docstring lists signatures and examples. Prefer cartoon moves for readable
phone-sized action. Motion capture is optional; bundled clips and source information are in
[`blockworld/mocap/README.md`](../blockworld/mocap/README.md).

Inside a shot, for example:

```python
dance(NIA, (-5, 12, ROAD), 0, "happy", T, style="bop")
label("NIA", NIA, color="#FFFFFF")
pop("+1", NIA, t)
confetti((-5, 12, ROAD), t)
hud("ROUND 1", "SCORE 10")
```

Use world coordinates for effects. Overlays also accept a character or `("s", x, y)` screen
coordinates (0–1, measured from the top left). Call effects and overlays every frame they should
appear. They are baked into `anim.json` and drawn by Three.js; Blender stills do not show the final
2D graphics or particle rendering. Review a Three.js draft before accepting their placement.

Additional `run(tod=...)` moods: `sunset`, `neon`, `horror`, `apocalypse`.

## Optional video review

`bash blockworld/review_agy.sh VIDEO.mp4 BRIEF.txt [OUT.md]` sends the video path and a shot brief
to a locally installed `agy` command. It requires `ffprobe`, `timeout`, and a configured agy client.
Set `AGY_BIN` to an executable path or `AGY_MODEL` to choose a model. It returns a text review;
inspect its findings against the video. It is optional and does not replace the skill's user review gates.
