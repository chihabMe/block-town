# Voice

Every episode uses the same narrator. `blockworld/vo.py` reads `vo_config.json` and writes `vo/voice.wav`;
`blockworld/words.py` then writes `vo/times.json`, which the shots and captions follow.

## Fish Audio "Roblox" (recommended)

The voice the top "in this town" creators use, as the Fish Audio community voice "Roblox", called through OpenRouter.
It scores **0.95–0.97** against the niche voice (the top creators score 0.95–0.99 against each other).

```json
{"engine": "fish", "voice": "eb4bcc6dbb634e9eaee239c94266935e", "model": "fish-audio/s2.1-pro-free:free"}
```

- **One take.** The whole script goes in one request, so it sounds like one recording. No pitch or speed change.
- **Made to sound like the top videos.** Measured on 8 of them: their narrations have almost no pauses (0–9%
  silence) and a brighter tone. `vo.py` cuts every pause to 0.05 s (`"tighten": true`) and lifts the treble
  (`"presence_db": 4.5`). That takes the Fish voice from 208 to about 253 words a minute and from 0.940 to 0.953.
- **Key.** `OPENROUTER_API_KEY` from the environment or `~/.env`. It is never printed or written into the episode.
- **Free for tests, paid to post.** `:free` costs nothing. Fish Audio's terms limit free use to non-commercial work,
  so make the take you post with `"model": "fish-audio/s2.1-pro"` (about $0.04 for a two-minute script). Ask the
  user before spending money.
- **Names.** `"say": {"Nia": "Nee-ah"}` respells a word for the voice only. `script.txt` stays as written.
- **Every take is different.** If a take sounds wrong, run `vo.py` again. Run `words.py` after every new take.
- The voice is a community upload; who owns the original voice is unknown. The user decides whether to post with it.

## Kokoro (free, offline)

```json
{"blend": "af_jessica:3,am_puck:2", "pitch_semitones": 3, "default_speed": 1.3, "default_pause": 0.18,
 "speed": {"1": 1.22}, "pause": {"1": 0.28}}
```

Local Kokoro, no account, no internet. It scores about 0.85–0.88: close, but not the niche voice. `speed` and `pause`
keys are 1-based line numbers. Speed 1.3 is about 250 words a minute; use about 1.1 for a slow, scary script.

## Either way

A `voice.wav` made somewhere else can be dropped into `vo/` and timed with `words.py`. The script text is the caption
text. Do not shift the word list by hand to force a match: fix the script token that drifted (a number, "$10", a
hyphen) and run `words.py` again. If `voice_match.py` is on the machine, score the take and report the number. Never
clone anyone's voice from their videos, and never put a reference clip in a video.

# Music

The song the top creators use under almost every video is **"Numbers" by TEMPOREX** (6 of the 9 creators whose music
could be identified). Scary episodes use a quiet, eerie track instead. The kit contains no music.

- **To post safely:** post `<episode>.mp4` (no music) and add "Numbers" from TikTok's sound picker.
- **To match the top creators:** put a copy of the song you got yourself next to the episode and add
  `"music": "numbers.mp3"` to `finish.json` (or pass `--music <file>`). `finish.py` then also writes
  `<episode>_music.mp4` with the song under the voice. Settings measured on the top videos:
  `"music_loop": 20.5` (they loop the song's first 20.5 seconds, its instrumental intro, for the whole video) and
  `"music_db": -4` (a steady 3–5 dB under the voice, never ducked). On our voice -9 keeps the words clearer;
  the example uses -9.
  The top creators mix it in this way, and a video with a copyrighted song in it can be muted or claimed.
