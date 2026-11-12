# Block town

A skill for Claude Code and Codex that makes vertical "In this town / In this world" rule-story videos in a
Roblox-style 3D town, from an idea to a finished 1080x1920 MP4. You give the agent an idea; it writes the script,
makes the narrator voice, builds the world and the characters in Blender from code, plans the shots, and finishes the
video with karaoke captions, sound effects and the music bed. It stops after every step for your answer.

Everything in the picture is built in code. The kit uses no Roblox models, no downloaded footage and no music.

`examples/ep05-wifi` is a finished 61-second episode made with it ("In this world, your Wi-Fi gets stronger the nicer
you are"): 42 shots, its script options, design sheet and all settings.

## What to install

| Tool | Why | Notes |
|---|---|---|
| [Blender](https://www.blender.org/download/) 4.2 or newer | builds and poses the town | tested on 5.2; `blender` must be on the PATH |
| [Node.js](https://nodejs.org) 20+ and Chrome or Chromium | draws the final frames (Three.js) | `npm install` runs by itself on the first render; `CHROME=/path` if Chrome is somewhere unusual |
| ffmpeg | captions, sound, the MP4 | with libass (most builds have it) |
| Python 3.11+ with `numpy` and `Pillow` | voice check, contact sheets, face drawing | `pip install numpy pillow` |
| whisper.cpp, `faster-whisper` or `openai-whisper` | word timing for cuts and captions | whichever is easiest; `words.py` finds it |
| An [OpenRouter](https://openrouter.ai) key | the narrator voice (Fish Audio "Roblox") | free model for tests; about $0.04 per posted episode |

Put the key in your environment or in `~/.env`:

```bash
echo 'OPENROUTER_API_KEY=sk-or-...' >> ~/.env
```

No key? `vo.py` also runs Kokoro offline (see `docs/VOICE.md`); it is close to the niche voice but not the same.

Sound effects made to order (optional): an [ElevenLabs](https://elevenlabs.io) plan with a commercial licence
(Starter or higher) and its API key in `~/.config/elevenlabs/env` (`ELEVENLABS_API_KEY=...`). Without it the kit uses
its free Pixabay set. See `docs/SOUND.md`.

Music is not included. The top videos use "Numbers" by TEMPOREX; either add it in TikTok's sound picker when you
post, or give the agent a copy you got yourself (`docs/VOICE.md`).

## Install the skill

```bash
git clone https://github.com/chihabMe/block-town.git ~/block-town
ln -s ~/block-town ~/.claude/skills/block-town      # Claude Code
ln -s ~/block-town ~/.codex/skills/block-town       # Codex
```

Update later with `git -C ~/block-town pull`.

## Make a video

Paste this into the agent (prompt 1 in `docs/PROMPTS.md`):

```
Make an "In this world / In this town" video with the block-town skill, in the Roblox look.
Idea: pick one
Episode folder: ~/videos/ep06
Follow SKILL.md's seven gates and stop after each one for my answer.
```

The seven gates: three rules → the script → the voice → a design sheet → a still of every shot → the first 15 seconds
finished → the full video. Blender builds and poses every frame and Three.js draws it: a 66-second episode takes
about 10–12 minutes from frames to finished MP4 on a laptop (Blender's own renderer took about 3 hours).

## Try it without making anything new

```bash
cd ~/block-town
blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep05-wifi check
blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep05-wifi stills s01 s16 s42
python3 -I blockworld/voice_check.py examples/ep05-wifi
```

`check` prints the 42 shots against the narration; `stills` renders three of them into `examples/ep05-wifi/stills/`.

## What's where

`SKILL.md` is what the agent follows. `docs/SCRIPT.md` (story), `docs/ROBLOX_LOOK.md` (world, cast, props, shots),
`docs/RENDER.md` (the Three.js renderer, the life layer, phone screens), `docs/SOUND.md` (sound effects, ElevenLabs,
the steady-voice mix), `docs/VOICE.md` (voice and music), `docs/PROMPTS.md` (a prompt per step), `docs/GUIDE.md` (the original block-look
manual). Sound effects in `sfx/` are from Pixabay (`sfx/CREDITS.md`); fonts are DejaVu Sans and Inter
(licences in `blockworld/fonts/`).
