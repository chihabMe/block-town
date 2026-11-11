# Voice

Every episode uses the same narrator. The locked free setting is already in `examples/ep01-intro/vo_config.json`:

| | |
|---|---|
| Engine | Local Kokoro, offline (`blockworld/vo.py`) |
| Blend | `af_jessica:3,am_puck:2` |
| Pitch | +3 semitones, once, on the joined track |
| Speed | 1.3, about 250 words a minute. The rule line (line 1) is 1.22 |
| Pauses | 0.18 s by default, a little longer between the early lines |

`blockworld/vo.py` writes `vo/voice.wav`. `blockworld/words.py` writes `vo/times.json`. Shots and captions read those times. Do not shift the word list by hand to force a match: fix the script token that drifted (a number, "$10", a hyphen) and run `words.py` again.

The intro narration scored **0.847** against the niche voice. Usable starts at 0.85. If this machine has `voice_match.py`, score the take and report the number. Do not clone anyone's voice, and do not put a reference clip in the video.

A `voice.wav` made somewhere else can be dropped into `vo/` and timed with `words.py`. The script text is the caption text either way.
