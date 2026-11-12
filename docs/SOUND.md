# Sound: effects, the steady-voice mix, music

The narration (`vo/voice.wav`, see `docs/VOICE.md`) is never changed by any of this: effects and music are separate
files that `finish.py` mixes under it.

## Sound effects

Two sources, both listed per cue in `EPISODE/cues.json`:

- **Pixabay set** (`sfx/*.mp3` without a prefix, `sfx/CREDITS.md`): free, generic (pop, whoosh, error, sparkle...).
- **ElevenLabs** (`sfx/el-*.mp3` for the reusable library, `sfx/epNN-*.mp3` for one episode): made to order from a
  text prompt, so each moment gets its own sound. The prompts live in `sfx/ELEVENLABS_LIST.md` (a 38-sound library plus
  ep05's own). Add new ones as table rows there: `| file | prompt | length | use |`.

### Generating with ElevenLabs

1. The user needs a paid plan with a commercial licence (Starter, $6/month, 30,000 credits) and an API key saved
   outside the project: `~/.config/elevenlabs/env` with `ELEVENLABS_API_KEY=...` (or the environment variable). Never
   ask for the key in chat.
2. `python3 -I SKILL/blockworld/sfx_gen.py --credits` shows what is left.
3. Generate only what the episode's cues use: `python3 -I SKILL/blockworld/sfx_gen.py el-tag-pop el-whoosh-cut ...`.
   About 200 credits a sound. Files that already exist are skipped (`--redo name` makes a new version). The script
   refuses if fewer than 2,000 credits (`--reserve`) would be left.
4. It trims the silence before the sound and normalises every file to -1 dBFS peak, so cue volumes mean the same thing
   for every file.
5. Listen if you can; if you can't, say so and check lengths and loudness instead.

Prompt rules: describe the kind of sound and how it should feel; give a length; never name a famous sound (the Roblox
"oof", phone brand ringtones, TV stings). Loops end in `-loop` and are generated as loops.

### Cue rules

```json
{"sfx": "el-tag-pop.mp3", "word": 44, "volume": 0.45}
{"sfx": "el-whoosh-cut.mp3", "shot": "s05", "offset": -0.08, "volume": 0.22}
{"sfx": "el-street-day-loop.mp3", "shot": "s01", "length": 66.1, "volume": 0.07}
```

- `word` is the script word index (its spoken start), `shot` a shot name; `offset` shifts it.
- `length` loops the file for that many seconds with soft edges (street, crowd, tower hum, a spinner under a phone).
- One sound per moment. Don't stack two "error" sounds within half a second (ep05's 19 s "froze ... three" glitch +
  error was the one sound the user called bad). Prefer short sounds; a 2.6 s glitch under one word is too long.
- Write cues by word, not by hand-typed word numbers: a spec with `"say": "froze"` (and `"after"`, `"nth"`,
  `"until"` for beds), then `python3 -I SKILL/blockworld/cues.py EPISODE cues_spec.json` writes `cues.json` and prints
  every cue's time. A word missing from the script stops it with a clear error. ep05's full ElevenLabs set is
  `examples/ep05-wifi/cues_elevenlabs_spec.json` (resolved: `cues_elevenlabs.json`; the example's `cues.json` stays on
  the Pixabay set until the `el-*` sounds exist).

## The steady-voice mix

The user heard the voice "lower down" after 17 s in ep05. Two causes, two settings in `finish.json`:

```json
{"captions": "karaoke", "voice": "vo/voice_level.wav", "loudness": "static", "music_loop": 20.5, "music_db": -9}
```

- `level_voice.py` levels the narration sentence by sentence (at most ±4 dB, ramped in the pauses) into
  `vo/voice_level.wav`. ep05 went from 2.2 LU to 0.8 LU loudness range. Run it after every new take.
- `"loudness": "static"` replaces the one-pass loudnorm (which turned the whole mix down for seconds after every loud
  effect) with gentle syllable-level compression on the voice and one fixed gain for the whole file, plus a limiter.
  In this mode each cue's volume is relative to the voice: 0.5 puts the effect's loudest moment 4 dB under the voice's
  speaking level, 0.25 puts it 10 dB under, 1.0 puts it 2 dB over.
- Check: integrated about -14 LUFS, short-term within ±1 dB for the whole video (ep05: ±0.5, LRA 0.9 LU).

Without these two keys `finish.py` behaves as before (older episodes are unchanged).

## Music

See `docs/VOICE.md`. `finish.json` `"music": "/path/file"` makes `<name>_music.mp4` next to the clean `<name>.mp4`. The
music sits `music_db` under the voice, with the static mix too. Post the clean file and add the song in TikTok; a copy
of the song cut from another creator's video is for review only and the `_music.mp4` made with it must not be posted.
