---
name: block-town
description: >
  Make a vertical "In this town / In this world" rule-story video in a Roblox-style 3D town, from an idea to a
  finished 1080x1920 MP4: rule, script, the niche narrator voice, world and characters built in Blender from code,
  shots, karaoke captions, sound effects and the music bed. Use when the user says make an "in this town" or
  "in this world" video, a Roblox story, block town, the town kit, or /block-town; or asks to write such a script,
  make its voice, animate it, add a character, prop or landmark to the town, or finish captions and sound.
---

# Block town

This folder is the whole kit: the town, the cast, how they move, the voice, the music settings, and the steps from an
idea to a finished vertical video. The skill folder is the directory that contains this file; it is called `SKILL`
below. Episodes live outside it (the user names the folder), called `EPISODE` below. Use absolute paths.

Read before building: `docs/ROBLOX_LOOK.md` (the world, the cast, the props, how shots are made),
`docs/SCRIPT.md` (how the story is written), `docs/VOICE.md` (voice and music). `docs/PROMPTS.md` has a prompt for
each stage. `docs/GUIDE.md` is the original block-look manual: the map, `pose()`, the moves and camera rules still
apply to both looks.

## Never

- No Roblox catalog items, downloaded models, or footage, stories or audio from other creators. Everything in the
  picture is built in code. Viral videos may be studied for craft, never reused.
- No paid API calls without the user's yes for that call. The free Fish Audio model is for tests; the posted take uses
  the paid one (about $0.04 per episode) only after the user approves. Ask before downloading anything.
- No music and no reference voice clips in this kit. Music goes in only from a file the user supplies.
- Do not change the eight recurring characters (colours, hair, clothes): `blockworld/town.py`.
- Do not switch an episode that is already in progress to another look.

## The look

New episodes use the **Roblox look**: `build_town(..., style="roblox")`. Round heads with anime faces, layered hair,
printed clothes, shiny plastic, sun / fog / rain moods, 3-word karaoke captions. The older **block look** (cube heads,
flat colours) is still there for episodes that started in it: `build_town(...)` without `style` gives the block look,
so always write `style="roblox"` in a new episode.

## Make an episode: seven gates

Stop after every gate, show the result, and wait for the user. Where there is a real creative choice, offer two or
three options and say which you recommend.

| Gate | What you make | Show the user |
|---|---|---|
| 1 Rule | Three rules (from the user's idea or `docs/SCRIPT.md` tests), each with a mood and a landmark idea | a table |
| 2 Script | `EPISODE/script.txt` (one sentence a line) and `EPISODE/SCRIPT.md`: option A and B, beat table, critic scores | the script |
| 3 Voice | `vo.py`, `words.py`, `voice_check.py` (free Fish take) | `vo/voice.wav`, its numbers |
| 4 Designs | `EPISODE/design/episode.py`: one still of every new landmark, prop, costume and character | `DESIGN_SHEET.jpg` |
| 5 Stills | `EPISODE/episode.py` with every shot; `check`; stills; fix; `contact_sheet.py` | `CONTACT_SHEET.jpg` |
| 6 Hook | the first ~15 s rendered and finished | the MP4 |
| 7 Full video | all frames, `finish.py` (clean file + music file); on approval, the paid voice take | both MP4s |

Gate details are in `docs/PROMPTS.md` (prompt 1 runs the whole thing). Copy `examples/ep05-wifi` to start: it is a
finished 61-second episode made exactly this way, with its design sheet, 42 shots, cues and settings.

A paid final take is a new recording: run `words.py` again, then `check`, and re-render (the shots follow the word
times). So approve the free take's timing at gate 3, but make the paid take before gate 6 if the user wants to post.

## Commands

```bash
# voice (gate 3)
python3 SKILL/blockworld/vo.py EPISODE                 # one take in the Fish "Roblox" voice (vo_config.json)
python3 SKILL/blockworld/vo.py EPISODE --post-only     # redo tighten / presence / tempo on the saved take, no new call
python3 SKILL/blockworld/words.py EPISODE              # word times -> vo/times.json
python3 -I SKILL/blockworld/voice_check.py EPISODE     # pace, pauses, brightness against the viral ranges

# pictures (gates 4-7); run with --factory-startup, always through run.py
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE check
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE stills [shot ...]
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE frame 12.5
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE render F0 F1
bash SKILL/blockworld/render_all.sh EPISODE            # every missing frame, restarting Blender if it stops
python3 -I SKILL/blockworld/contact_sheet.py EPISODE   # one numbered still per shot -> CONTACT_SHEET.jpg

# finishing (gates 6-7)
python3 SKILL/blockworld/finish.py EPISODE                       # captions + sound effects -> EPISODE/<name>.mp4
python3 SKILL/blockworld/finish.py EPISODE --music /path/numbers.mp3   # also <name>_music.mp4
```

- `check` renders nothing: it runs every shot, prints the shot table and warns about shots over 2.5 s.
- `stills` writes two half-size pictures per shot (30% and 85% through) into `EPISODE/stills/`. Render them in groups
  of about 12 shots if your commands have a time limit. **Look at every still** before showing any.
- Final frames are 1080x1920 JPEGs, about 3.5 s each in sun, about 6.6 s in rain or fog on the machine this was made on:
  a 60-second sunny episode is about 1.5–2 hours. Run `render_all.sh` in the background. Something else on the
  machine may stop Blender; `render_all.sh` resumes from the last frame.
- The hook: `render 0 F1` where `F1` is the frame just before the first cut after ~15 s, then `finish.py`
  (it uses the frames that exist), and rename the MP4 so the full video does not overwrite it.
- Watch and listen to the final file before calling it done. If you cannot listen, say so plainly.
- Delete `frames/` after the user accepts the video (about 180 KB a frame).

## What goes where

| Path | What |
|---|---|
| `blockworld/town.py` | the street, the cast, `pose()`, light, camera, `build_town(style=...)` |
| `blockworld/roblox.py` | the Roblox look: `rchar`, plastic, moods, `rule_sign`, `giant_clock`, `puddles` |
| `blockworld/rprops.py` | ready props: signal-bar tags, phones and phone inserts, poster, sash, top hat, bus, door, beam, pigeon, Wi-Fi tower |
| `blockworld/anim.py` | word timing helpers, cards (tags, bubbles), `stand`, `walk`, the runner |
| `blockworld/vo.py`, `words.py`, `voice_check.py` | voice, word times, voice check |
| `blockworld/finish.py` | captions, sound effects, music, the MP4 |
| `sfx/` | free sound effects (Pixabay licence, `sfx/CREDITS.md`) |
| `examples/ep05-wifi` | the full worked episode (Roblox look) |
| `examples/ep00-roblox-look`, `examples/ep01-intro` | short demos of the Roblox look and the block look |
