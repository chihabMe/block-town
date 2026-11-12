---
name: block-town
description: >
  Build a vertical block-style "in this town" video from an idea and a script.
  The skill contains the Blender town, the eight characters, the poses, the camera,
  the captions and the sound. Use when the user says make a block-style video,
  "in this town", block town, the town kit, or /block-town. Also when they ask
  to animate a script in the block look, add a character or prop to that town,
  or finish captions and sound for one of these episodes.
---

# Block town

An idea and a script are enough. This folder is the whole kit: the street, the people, how they move, and how a script becomes a vertical video. `docs/GUIDE.md` is the law for every number. `docs/PROMPTS.md` is the prompt pack. Read both before building.

The skill folder is the directory that contains this file. Call it `SKILL` below. Do not look for an older test folder. Do not invent a second town.

## What you never do

- No Roblox catalog items, downloaded models, or footage from another creator. People are built in code by `character()`, in either look.
- No paid APIs. Blender, Kokoro, and the sound effects in `sfx/` are the toolchain. Ask before downloading anything, including a font.
- No music in the file. No reference voice clip in the file.
- Do not change the eight recurring characters' colours, hair, or clothes. They are defined once in `blockworld/town.py`.
- If the script needs something `docs/GUIDE.md` lists as not built yet (a room, sitting, running, falling, holding an object), say so in the plan and show one test still before using it.

## Two looks

The town has two looks. **Block** (the default) is the original: cube heads, flat colours. **Roblox** is closer to the
most-watched videos: round heads, printed clothes, shiny plastic, fog and rain, 3-word karaoke captions. Read
`docs/ROBLOX_LOOK.md` and copy `examples/ep00-roblox-look` for it: `build_town(..., style="roblox")`,
`run(SHOTS, tod="rain")`, and `{"captions": "karaoke"}` in `finish.json`. Ask the user which look when they don't say.
Never switch an episode that is already in progress to the other look.

## Make an episode

Copy `examples/ep01-intro` (block look) or `examples/ep00-roblox-look` (Roblox look) to the episode folder the user named. Replace `script.txt`, `episode.py`, and `cues.json`. Keep `vo_config.json` unless the user asked for a different voice.

`episode.py` dresses the town with `build_town(rule_big, shop_signs)`, adds only the props and extra people this script needs, and ends with `run(SHOTS)`. `examples/ep01-intro/episode.py` is the pattern. Run it only through `blockworld/run.py`.

Work in six stages. Stop after each one and wait for the user.

1. **Plan.** Write `PLAN.md` in the episode folder: the world sheet, the cast sheet, and one row per shot (prompts 2–4 in `docs/PROMPTS.md`). Give two or three options where there is a real choice.
2. **Voice.** `python3 SKILL/blockworld/vo.py EPISODE`, then `python3 SKILL/blockworld/words.py EPISODE`. Play the audio. If more than 15% of the words were guessed, say so.
3. **New designs.** One still of each new character, prop, or face, next to Nia or Man.
4. **Stills.** Two half-size stills of every shot. Look at the images. Fix them against the checklist in `docs/GUIDE.md` section 11 before showing a contact sheet.
5. **Hook.** Render and finish the first 10–15 seconds.
6. **Full render.** Render the rest, then `python3 SKILL/blockworld/finish.py EPISODE`. Watch and listen to the file before calling it done, and say plainly if you did not.

## Commands

From any directory, with `SKILL` and `EPISODE` as absolute paths:

```bash
python3 SKILL/blockworld/vo.py EPISODE
python3 SKILL/blockworld/words.py EPISODE
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE check
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE stills
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE frame 2.5
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE render
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE resume
python3 SKILL/blockworld/finish.py EPISODE --captions
python3 SKILL/blockworld/finish.py EPISODE
```

`check` renders nothing. It runs every shot and prints the shot table. `stills` writes two pictures per shot, at 30% and 85%, into `EPISODE/stills/`. `render` writes `EPISODE/frames/f_####.jpg` at 1080×1920. About 4.5 seconds per final frame on the machine this was built on, so a two-minute episode is several hours. Render it in the background. `resume` fills only the missing frames.

A final frame is a JPEG of about 180 KB. Delete `frames/` after the user accepts the video.

## One-shot pieces

Prompts 2–10 in `docs/PROMPTS.md` do one piece: the world sheet, the cast sheet, the shot plan, the shot functions, a new prop, a new character, a new face, a stills check, or notes on a cut. Use prompt 1 only when the user wants the whole video.

New faces are drawn with `python3 SKILL/blockworld/faces.py SKILL/blockworld/faces` (needs Pillow), then used by name in `pose()`.
