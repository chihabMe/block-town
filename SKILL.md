---
name: block-town
description: >
  Make a vertical "In this town / In this world" rule-story video in a Roblox-style 3D town, from research to a
  finished 1080x1920 MP4: viral-video research with Apify, five fresh ideas to pick from, three scripts, opening
  variants, fast draft renders for review and a final high-quality render; the niche narrator voice, world and
  characters built from code in Blender and
  rendered with Three.js, shots, the life layer, phone screens and props, karaoke captions, ElevenLabs or stock sound
  effects, a steady voice mix and the music file. Use when the user says make an "in this town" or "in this world"
  video, a Roblox story, block town, the town kit, or /block-town; or asks to write such a script, make its voice,
  animate it, add a character, prop, phone screen or landmark to the town, render it, or finish captions and sound;
  or asks for trending ideas, viral-video research or analytics for this niche.
---

# Block town

This folder is the whole kit: the town, the cast, how they move, the renderer, the voice, the sounds, the music
settings, and the steps from an idea to a finished vertical video. The skill folder is the directory that contains this
file; it is called `SKILL` below. Episodes live outside it (the user names the folder), called `EPISODE` below. Use
absolute paths.

Read before building: `docs/RESEARCH.md` (gate 0 research with Apify, gate 1's five ideas), `docs/ROBLOX_LOOK.md` (the world, the cast, the props, how shots are made),
`docs/RENDER.md` (the Three.js renderer, the life layer, tags, phone screens and printed props),
`docs/SCRIPT.md` (how the story is written), `docs/VOICE.md` (voice and music), `docs/SOUND.md` (sound effects,
ElevenLabs, the steady-voice mix). `docs/PROMPTS.md` has a prompt for each stage. `docs/GUIDE.md` is the original
block-look manual: the map, `pose()`, the moves and camera rules still apply.

## How a video is made (since ep05)

Blender builds and poses everything from the episode's Python code; **Three.js draws the final frames**. Blender's own
renderer is only for design sheets and shot stills.

```
episode.py ──(Blender: build the town, pose every frame, life layer)──> bake: scene.glb + anim.bin + materials.json
           ──(Three.js in headless Chrome)──> EPISODE/frames/f_####.jpg  (~0.1-0.15 s a frame)
           ──(finish.py: captions, levelled voice, sound effects, music)──> EPISODE/<name>.mp4 and <name>_music.mp4
```

A 66-second episode takes about **10-12 minutes** from frames to finished MP4s (Blender EEVEE took about 3 hours).

## Never

- No Roblox catalog items, downloaded models, or footage, stories or audio from other creators. Everything in the
  picture is built in code or drawn by `blockworld/pictures.py`. Viral videos may be studied for craft, never reused.
- No paid API calls without the user's yes. Fish Audio (voice), ElevenLabs (sound effects) and Apify (research)
  cost money: say what a run will cost first. `sfx_gen.py` checks the remaining credits and stops before the reserve; never raise the reserve
  or loop generations to "try again" without asking. Ask before downloading anything.
- No music and no reference voice clips in this kit. Music only from a file the user supplies, and only in the
  `_music.mp4` copy. If that file was cut out of another creator's video, say plainly that the `_music.mp4` must not
  be posted: post the clean `<name>.mp4` and add the song in TikTok's sound picker.
- Do not change the eight recurring characters (colours, hair, clothes): `blockworld/town.py`.
- Do not switch an episode that is already in progress to another look.
- No unexplained abstract graphics. A beam, a line or a glow between two small figures does not tell the viewer
  anything (ep05's "giving every bar away" beam read as "a blue line"). Show the thing itself: bars flying out of a
  tag, a counter going down, a phone screen that says it.

## The look

New episodes use the **Roblox look**: `build_town(..., style="roblox")`. Round heads with anime faces, layered hair,
printed clothes, shiny plastic, sun / fog / rain moods, 3-word karaoke captions. The older **block look** (cube heads,
flat colours) is still there for episodes that started in it: `build_town(...)` without `style` gives the block look,
so always write `style="roblox"` in a new episode.

## Quality bar (what the user rejected or asked for)

- **Nothing is ever static.** Render with the life layer (`BT_LIFE=1`, the default in `render_threejs.sh`): breathing,
  glances, weight shifts, a bounce on every cut, camera wobble and punch-ins, swaying trees, drifting clouds, floating
  tags, turning loading spinners, pulsing Wi-Fi rings, bouncing signal bars. A shot where only the camera creeps is a
  weak shot: give it its own action.
- **Tags and bubbles are never covered and never cut off.** The life layer draws them on top of everything, lifts them
  above hair, and keeps them inside the TikTok safe area (x 5-85 %, y above the captions). Check that two tags don't
  overlap each other (not automatic yet).
- **Every screen looks like a real phone**: `big_phone(screen=...)` with a picture from `pictures.py` (status bar,
  "No Service", app layout, a hand holding it), never a white box with 3D text. Hand-held phones show a lock screen.
- **Props read at phone size**: a paper map is a real drawn map (`paper_map()`), a sign is fully in frame (pull the
  camera back: a 10-stud sign needs ~25 studs of distance in 9:16).
- **The voice never dips.** `finish.json` `{"voice": "vo/voice_level.wav", "loudness": "static"}`: the narration
  is levelled sentence by sentence and the mix gets one fixed gain, so loud effects can't make the voice drop. Measure:
  short-term loudness should stay within ±1 dB of -14 LUFS for the whole video.
- **No stacked or harsh effects.** One sound per moment; nothing longer than the moment; no two "error" sounds within
  half a second.

## Make an episode: research, pick, draft, final

Stop after every gate, show the result, and wait for the user.
- Where there is a choice, show the options and mark the one you recommend.
- "Go with yours" (or "you pick") means the recommended one. Say which you took and why in one line, then go on.
- Don't decide for the user while they are away: a gate waits for their answer.

| Gate | What you make | Show the user |
|---|---|---|
| 0 Research (optional) | Apify scrape of the niche (cost first, the user's yes), analysis, `TRENDS_<date>.md`: `docs/RESEARCH.md` | the findings, in ~10 lines |
| 1 Ideas | **Five ideas** by default (the user may ask for more or fewer): rule, mood, two-line story, landmark, why now, score: `docs/RESEARCH.md` | a table + the recommended pick |
| 2 Script | **Three full scripts** for the chosen idea, each a different angle (twist, tone or underdog), all scored on the critic list: `EPISODE/SCRIPT.md`; the pick goes to `EPISODE/script.txt` | the three scripts + the recommended pick |
| 3 Voice | `vo.py`, `words.py`, `voice_check.py` (free Fish take), `level_voice.py` | `vo/voice.wav`, its numbers |
| 4 Designs | `EPISODE/design/episode.py`: one still of every new landmark, prop, costume and character; `EPISODE/pictures.json` and `pictures.py` for every phone screen and printed prop | `DESIGN_SHEET.jpg` + the screens |
| 5 Stills | `EPISODE/episode.py` with every shot; `check` until `still_check.txt` is clean; stills; fix; `contact_sheet.py` | `CONTACT_SHEET.jpg` |
| 6 Openings | `preflight.py`; **four opening variants** of the first ~15 s by default (the user may ask for fewer): `openings.py new`, each rendered as a draft, `openings.py grid` | the grid + each draft, recommended pick |
| 7 Draft | the chosen opening moved into `episode.py`, then the **whole video as a fast draft**: `render_threejs.sh EPISODE --draft`, cues, `finish.py EPISODE --draft`; then review rounds (fix the notes, re-render only the changed shots) | `<name>_draft.mp4` each round |
| 8 Final | on the user's approval only: `preflight.py --final`, the full-quality render (1080x1920, `render_fps` 240 + `blur` 4 = 60 fps with motion blur, the grade), `finish.py` (clean file + music file) | both MP4s |

Gate details are in `docs/PROMPTS.md` (prompt 1 runs the whole thing). Copy `examples/ep05-wifi` to start: it is a
finished episode made this way, with its design sheet, 42 shots, phone pictures, cues and settings.

**Opening variants** (gate 6):
- Each variant is a small episode folder in `EPISODE/openings/<name>/`. It has the hook lines, the same narration
  cut after them, and a copy of `episode.py` to cut down to the hook shots. Every normal command works on it.
- By default the variants share the words and differ in the pictures: the first image, the landmark reveal, the
  camera, the first action. Name the difference in one line per variant.
- A variant with different hook **words** needs its own voice take (free), and the chosen words then mean a new full
  take.
- After the pick: move its shots into `episode.py`, run `check`, and delete `openings/`.

**Draft vs final:**
- The draft is 540x960, 30 fps, no blur, no grade, a lighter shadow map and a fast encode, with the same shots, life
  layer, tags, captions and sound. It goes to `frames_draft/`. Measured on ep08 (2026-11-13): the draft draws a frame
  in 0.08 s against 0.165 s at full size, and the Blender bake (~1 min plus ~0.055 s a frame) is the same for both.
  For 66 s that is about 6 min for the draft, about 9 min for a full-size 30 fps render, and well over an hour for the
  240 fps motion-blur final.
- Review rounds happen on the draft: fix the notes, then re-render only the changed shots with
  `render_threejs.sh EPISODE --draft F0 F1`, and run `finish.py EPISODE --draft`.
- The final render happens once, after the user says the draft is right.

**The voice.** A paid take is a new recording: run `words.py` and `level_voice.py` again, then `check`, then a new
draft (the shots follow the word times). The user posts with the free take for now, so offer the paid take at gate 8
but don't push it. If they want it, make it before the final render and show one more draft.

## Commands

```bash
# voice (gate 3)
python3 SKILL/blockworld/vo.py EPISODE                 # one take in the Fish "Roblox" voice (vo_config.json)
python3 SKILL/blockworld/vo.py EPISODE --post-only     # redo tighten / presence / tempo on the saved take, no new call
python3 SKILL/blockworld/words.py EPISODE              # word times -> vo/times.json
python3 -I SKILL/blockworld/voice_check.py EPISODE     # pace, pauses, brightness against the viral ranges
python3 -I SKILL/blockworld/level_voice.py EPISODE     # every sentence at one level -> vo/voice_level.wav

# pictures for props (gate 4)
python3 -I SKILL/blockworld/pictures.py EPISODE        # EPISODE/pictures.json -> EPISODE/pictures/*.png

# shots (gates 4-5): Blender, always through run.py with --factory-startup
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE check
BT_LIFE=1 blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE stills [shot ...]
blender -b --factory-startup --python-exit-code 1 -P SKILL/blockworld/run.py -- EPISODE frame 12.5
python3 -I SKILL/blockworld/contact_sheet.py EPISODE   # one numbered still per shot -> CONTACT_SHEET.jpg

# ready to render? (gates 6 and 8)
python3 -I SKILL/blockworld/preflight.py EPISODE             # tools, keys (set or not), voice, times, pictures, shots, cues
python3 -I SKILL/blockworld/preflight.py EPISODE --final     # also music file, paid take, render_fps

# opening variants (gate 6)
python3 -I SKILL/blockworld/openings.py EPISODE new A B C D [--until 15]   # EPISODE/openings/A..D, the hook only
python3 -I SKILL/blockworld/openings.py EPISODE list                       # what each variant has
python3 -I SKILL/blockworld/openings.py EPISODE grid                       # the drafts in one compare video (2 side by side, 3-4 in 2x2)

# draft frames (gates 6-7): 540x960, 30 fps -> EPISODE/frames_draft/
bash SKILL/blockworld/render_threejs.sh EPISODE --draft          # the whole video
bash SKILL/blockworld/render_threejs.sh EPISODE --draft F0 F1    # only the shots a review round changed

# final frames (gate 8): Three.js, full size, finish.json render_fps
bash SKILL/blockworld/render_threejs.sh EPISODE              # every frame -> EPISODE/frames/ (~10 min for 66 s at 30 fps)
bash SKILL/blockworld/render_threejs.sh EPISODE F0 F1        # only F0..F1 (a re-done shot)
BT_RESUME=1 bash SKILL/blockworld/render_threejs.sh EPISODE  # finish a stopped run: without it, F0..F1 is cleared first

# sound effects (gates 6-7): see docs/SOUND.md
python3 -I SKILL/blockworld/sfx_gen.py --credits             # ElevenLabs credits left
python3 -I SKILL/blockworld/sfx_gen.py el-tag-pop ep07-...   # generate named sounds from sfx/ELEVENLABS_LIST.md
python3 -I SKILL/blockworld/cues.py EPISODE cues_spec.json   # cues by word ("say": "froze") -> EPISODE/cues.json

# finishing
python3 -I SKILL/blockworld/finish.py EPISODE --draft        # gates 6-7: frames_draft/ -> <name>_draft.mp4, fast encode
python3 -I SKILL/blockworld/finish.py EPISODE                # gate 8: captions + voice + effects (+ music) -> the MP4s
```

- `check` renders nothing: it runs every shot, prints the shot table and warns about shots over 2.5 s.
- **Automatic still checks** (`blockworld/stillcheck.py`, since ep08): call `focus(character, tag, ...)` in every
  shot. `check` and `stills` then report faces blocked (by a post, a person, a tag or the character's own arm), faces
  under the caption band, tags outside the safe area (x 5-85 %, between TikTok's top bar and the captions), tags
  covering each other, and anything within 1 stud of the lens. Results go to `EPISODE/still_check.txt`. Fix every line
  before showing stills, then still look at them: it does not judge framing or whether the picture tells the line.
- **60 fps with motion blur** (optional): `finish.json` `"render_fps": 240, "blur": 4` renders 240 frames a second
  and averages each 4 into one 60 fps frame. About 1.6 min of rendering per second of video.
- **Colour turn** (optional): `finish.json` `"grade": {"word": 24, "ramp": 0.5, "saturation": 0.6,
  "brightness": -0.05, "cool": 0.1, "vignette": true}` fades the picture colder, darker and flatter from that script
  word (the story's turn). Captions are not graded. `finish.py EPISODE --plain` also writes `<name>_plain.mp4`
  (30 fps, no blur, no grade) for a side-by-side.
- ep08 (`episodes/ep08-price-tags-10s`) is the 10-second test of these, with ~1 s shots.
- `stills` writes two half-size Blender pictures per shot (30 % and 85 % through) into `EPISODE/stills/`. Use
  `BT_LIFE=1` so tags are placed the way the final render places them. **Look at every still** before showing any.
- `render_threejs.sh` runs in the background if your commands time out (about 10 minutes for 66 s). It installs the
  two npm packages on first use (`blockworld/threejs/`) and needs Chrome or Chromium (`CHROME=/path` to choose).
  It keeps its bake in `EPISODE/threejs/`. After the user accepts the final video, delete that, `frames/`,
  `frames_draft/` and `openings/`.
- After any change to `episode.py`, a set piece or a picture: re-run `render_threejs.sh` (the bake reads the code).
  Frames in the range being rendered are deleted first, so nothing stale is kept. `BT_RESUME=1` keeps them, to finish
  a run that was stopped part way.
- Frame numbers depend on the frame rate: the draft is always 30 fps, the final uses `render_fps` (240 frames a second
  for motion blur), so a draft F0..F1 is not the same range in the final.
- `render_all.sh` (Blender EEVEE frames) is kept only for comparisons: about 3-6 s a frame.
- Watch frames across the whole video (one per shot at least) and measure the loudness before calling it done. If you
  cannot listen, say so plainly and list what you checked instead.

## What goes where

| Path | What |
|---|---|
| `blockworld/town.py` | the street, the cast, `pose()`, light, camera, `build_town(style=...)` |
| `blockworld/roblox.py` | the Roblox look: `rchar`, plastic, moods, `rule_sign`, `giant_clock`, `puddles` |
| `blockworld/rprops.py` | ready props: signal-bar tags and flying bar tokens, phones with real screens and a hand, lit and printed pictures, folded paper map, poster, sash, top hat, bus, door, beam, pigeon, Wi-Fi tower |
| `blockworld/pictures.py`, `blockworld/pictures/` | draws phone screens, lock screens and maps from `pictures.json`; the kit's default pictures |
| `blockworld/anim.py` | word timing helpers, cards (tags, bubbles), `stand`, `walk`, the runner |
| `blockworld/life.py` | the life layer (BT_LIFE=1): idle motion, camera, scene sway, spinners, tag placement |
| `blockworld/threejs/` | the renderer: `bake.py` (Blender side), `scene.html` + `capture.mjs` (Three.js side) |
| `blockworld/render_threejs.sh` | bake + draw, the normal way to make frames (`--draft` for the 540x960 review copy) |
| `blockworld/openings.py` | opening variants: make them, list them, the compare video |
| `blockworld/preflight.py` | the ready-to-render check |
| `docs/RESEARCH.md` | gate 0 research (Apify) and gate 1's five ideas |
| `blockworld/vo.py`, `words.py`, `voice_check.py`, `level_voice.py` | voice, word times, voice check, levelling |
| `blockworld/sfx_gen.py`, `sfx/ELEVENLABS_LIST.md` | ElevenLabs sound effects: the generator and the prompt list |
| `blockworld/finish.py` | captions, voice, sound effects (looping beds too), music, the steady mix, the MP4s |
| `blockworld/cues.py` | cue lists by word -> `cues.json` |
| `sfx/` | sound effects: the Pixabay set (`sfx/CREDITS.md`); ElevenLabs sounds land here as `el-*.mp3` / `epNN-*.mp3` once generated (none yet as of ep05) |
| `examples/ep05-wifi` | the full worked episode (Roblox look, Three.js renderer) |
| `examples/ep00-roblox-look`, `examples/ep01-intro` | short demos of the Roblox look and the block look |
