# The Roblox look

A second look for the same town: round heads, layered hair, printed clothes, shiny plastic, fog and moving rain,
3-word karaoke captions. It is closer to what the most-watched "in this town" videos look like. The block look is
still the default, and episodes made in it render exactly as before.

Everything is still built in code from simple shapes. No Roblox models, catalog items or footage are used.

## Turn it on

```python
from anim import *
from roblox import giant_clock, puddles, rule_sign      # landmarks for this look

build_town("HOME BY 8", ("CLOCK SHOP", "EARLY BIRD"), style="roblox")
...
run(SHOTS, tod="rain")                                    # mood: "sun", "fog", "rain", "dusk", "night"
```

and put `{"captions": "karaoke"}` in the episode's `finish.json`. `examples/ep00-roblox-look` is the pattern:
five shots, about 8 seconds, every piece of this look in use.

What `style="roblox"` changes:

| | Block look | Roblox look |
|---|---|---|
| Heads | cube, flat face | round, anime face (same face names: `pose(c, face="scared")`) |
| Hair | boxes | spikes, buns, pigtails, long hair, caps, beanies (same style names) |
| Clothes | flat colour | printed: folds, hem, belt; `top="jacket"` / `"hoodie"`, `legs="jeans"` |
| Surfaces | matte | plastic with a soft highlight, rounded edges |
| Moods | day, dusk, night | + `sun`, `fog`, `rain` (falling rain, wet road, distance fog) |
| Captions | one big yellow word | up to 3 white words, the spoken word turns yellow |

The eight recurring characters are rebuilt in the new look with the same colours, hair styles and clothes details,
so `NIA`, `MAN` and the rest keep working in shot code. `character(...)` builds new people in the new look too,
and takes two extra keywords: `top` and `legs`. `restyle(MAN, top="jacket", legs="jeans")` dresses one cast member
differently for one episode.

## What to build in every episode (what the top videos do)

1. **The rule is a thing you can see.** One big landmark that is the rule (a giant clock for a curfew, a scale for
   a weight rule, a counter, a statue) plus the official red-and-white `rule_sign(...)`. Both are on screen in the
   first 2 seconds and come back often. Keep sign text above the caption band (the top 62% of the frame).
2. **Story shape.** The rule → how it works (one concrete detail) → everyone obeys, said as a list of three ("not
   kids, not grandmas, not even the mailman") → a newcomer who doesn't know → someone else is punished first → the
   hero breaks the rule → one reaction per shot → a twist that flips the rule. End on a cliffhanger or an ironic line.
3. **Mood matches the story.** Comedy: `sun`, fast narration (`default_speed` 1.3, about 280 words a minute).
   Scary: `rain` or `fog`, slower narration (about 1.1, about 200 words a minute), one strong colour against grey.
4. **The picture changes every second.** A hard cut every 1–2.5 s, and inside a shot the camera travels: push in,
   glide past a crowd, sweep up to the landmark. Low camera angles for anything big or threatening.
5. **Big, readable acting.** Running crowds (`walk(..., speed=7.5)` with `"scared"`), a face that snaps on the key
   word, close-ups for every feeling.
6. **The niche voice and "Numbers".** Narrate with the Fish Audio "Roblox" voice and put "Numbers" (TEMPOREX)
   under the whole video, about 4 dB under the voice. See `docs/VOICE.md` for both, and for what is safe to post.

## Pieces (blockworld/roblox.py)

| Function | What it does |
|---|---|
| `rchar(name, skin, shirt, pants, hair_style, hair_col, top=, legs=, cuff=, ...)` | A new person (or use `character`) |
| `restyle(c, **change)` | Rebuild one character with changes, in place |
| `giant_clock(x, y, hours, minutes, yaw)` | Example landmark: a three-storey alarm clock on a plinth |
| `rule_sign(x, y, big, small, yaw, lift)` | The official rule sign on two posts |
| `puddles([(x, y, r), ...])` | Mirror puddles for rain shots |
| `plastic(hex, rough)`, `rbox(...)`, `blob(...)`, `cone(...)`, `disc(...)` | Building blocks for new props and landmarks |

Faces and clothes prints are pictures drawn by `python3 -I blockworld/rlook_tex.py` into `blockworld/rlook/`.
Add a face by adding one row to `FACES` in that file.

## Costs and limits

- About **6.6 s per final frame in rain or fog and 4.8 s in sun** on the machine this was built on (block look:
  about 4.5 s). A two-minute rainy episode is about 6.5 hours of rendering.
- Not built yet: rooms, sitting, falling, holding things, door animations. Say so in the plan and test a still first.
- Rain is drawn around the camera. In very high aerial shots it only covers the ground area.
