# Block town

A skill for making vertical block-style "in this town" videos. You give a coding agent the idea and the script. The agent builds the episode from this folder: the street, the eight characters, the poses, the camera, the captions, and the sound.

It does not need the earlier experiments. `examples/ep01-intro` is a finished 9-shot intro (about 11 seconds) that shows the pattern. `docs/GUIDE.md` is the manual. `SKILL.md` is what the agent follows.

People are original block characters drawn from boxes. This kit does not use Roblox models or catalog items.

## What a friend installs

Blender 4.2 or newer (tested on 5.2), ffmpeg, and Python 3.11+. Pillow is only needed when adding a face. The narration step needs a local [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) install; a `voice.wav` you already made can be dropped into the episode instead. Word timing uses whisper.cpp, `faster-whisper`, or `openai-whisper`, whichever is on the machine.

Sound effects in `sfx/` are from Pixabay and are free to use. See `sfx/CREDITS.md`. The sign font is DejaVu Sans Bold. The caption font is Inter Display Black. Both licenses are in `blockworld/fonts/`.

## Install the skill

Claude Code reads `~/.claude/skills/<name>/SKILL.md`. Codex reads `~/.codex/skills/<name>/SKILL.md`.

```bash
git clone https://github.com/chihabMe/block-town.git ~/.claude/skills/block-town
git clone https://github.com/chihabMe/block-town.git ~/.codex/skills/block-town
```

Use one clone and a link if you would rather not keep two copies:

```bash
git clone https://github.com/chihabMe/block-town.git ~/block-town
ln -s ~/block-town ~/.claude/skills/block-town
ln -s ~/block-town ~/.codex/skills/block-town
```

A zip of this folder also works. Unzip it and tell the agent to read `SKILL.md`. A zip does not get later fixes; `git pull` inside the clone does.

## Ask the agent

```
Make a block-style video.
Idea: In this town, every secret you keep turns your hair blue.
Script: episodes/ep02-secrets/script.txt
Follow the block-town skill. Stop after each stage.
```

The agent should stop after the plan, the voice, any new designs, the stills, the first 10–15 seconds, and then the full video.

## Run the intro yourself

From this folder:

```bash
blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep01-intro check
blender -b --factory-startup --python-exit-code 1 -P blockworld/run.py -- examples/ep01-intro stills
```

`check` renders nothing and prints the nine shots. `stills` writes two pictures of each shot into `examples/ep01-intro/stills/`. The example already contains `vo/voice.wav` and `vo/times.json`, so the pictures line up with the narration.

Rendering the whole intro is `render` instead of `stills` (333 frames, on the order of 25 minutes on the machine this was built on). Then:

```bash
python3 blockworld/finish.py examples/ep01-intro
```

That writes `examples/ep01-intro/ep01-intro.mp4` with one-word captions and the sound effects. There is no music in the file.

## New episode

Copy `examples/ep01-intro`. Replace `script.txt`, write new shot functions in `episode.py`, and list the sound effects in `cues.json`. Make a new narration only when the words changed:

```bash
python3 blockworld/vo.py EPISODE
python3 blockworld/words.py EPISODE
```

Kokoro setup, once, if `vo.py` cannot find it:

```bash
uv venv ~/.venvs/kokoro
~/.venvs/kokoro/bin/pip install kokoro-onnx soundfile numpy
```

Put `kokoro-v1.0.onnx` in `~/.cache/hyperframes/tts/models/` and `voices-v1.0.bin` in `~/.cache/hyperframes/tts/voices/`. `vo.py` also honours `$KOKORO_PYTHON`.

## Two looks

The block look is the default. The Roblox look (round heads, printed clothes, plastic, fog and rain, karaoke captions) is
switched on per episode with `build_town(..., style="roblox")`. See `docs/ROBLOX_LOOK.md` and `examples/ep00-roblox-look`.

## What is not built yet

Rooms, sitting, running, falling, and holding an object. The guide lists them. A script that needs one gets a test still before any shot uses it.
