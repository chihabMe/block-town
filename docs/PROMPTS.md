# Prompts

Paste a prompt into Claude Code or Codex with the block-town skill installed. `{…}` are yours to fill in. The skill
folder is `SKILL`; the episode folder is `EPISODE` (for example `~/videos/ep06-shadows`). Rules and numbers come from
`SKILL.md`, `docs/SCRIPT.md`, `docs/ROBLOX_LOOK.md` and `docs/VOICE.md`. The block-look prompts that used to be here
are in `docs/GUIDE.md`.

## 1. Make the whole video (the master prompt)

```
Make an "In this world / In this town" video with the block-town skill, in the Roblox look.
Idea: {a rule, a theme, or "pick one"}
Episode folder: {EPISODE}
Follow SKILL.md's seven gates and stop after each one for my answer:
1 three rules, 2 script (two options + critic scores), 3 voice (free Fish take + voice_check numbers),
4 design sheet, 5 contact sheet of every shot, 6 the first ~15 s finished, 7 the full video.
Offer 2-3 options wherever there is a real creative choice and say which you recommend.
Don't spend money (paid voice) or download anything without asking me first.
```

## 2. Rule ideas (gate 1)

```
Give me three "In this world / In this town" rules for {theme or "anything"}, each in a different mood (comedy,
horror, heart). For each: the rule as spoken (10 words or fewer), the underdog it hurts, the comment loophole, a twist
that is fair from the first line, and the landmark that shows the rule (big, simple, one strong colour). Score each
on docs/SCRIPT.md's five tests. Don't reuse any rule, joke or twist from other creators.
```

## 3. Script (gate 2)

```
Write the script for rule: {rule}. Follow docs/SCRIPT.md: 60 seconds, about 240 words, one sentence a line,
the 8 beats with "everyone obeys" (a list of three) and "punished first", a callback and a fair twist whose clue is
hidden in beat 4. Write option A in full and option B as a different ending, score A on the 12-point critic list,
fix anything under 8, and write it all to EPISODE/SCRIPT.md (pattern: examples/ep05-wifi/SCRIPT.md).
Put A in EPISODE/script.txt. List what the pictures need: landmark, signs, props, tags, cast roles.
```

## 4. Voice (gate 3)

```
Make the narration for EPISODE with the free Fish model: copy examples/ep05-wifi/vo_config.json, run vo.py,
words.py and voice_check.py. Tell me the length, words a minute, the voice_check table, and any guessed words
other than numbers. Send me vo/voice.wav. Don't use the paid model.
```

## 5. Design sheet (gate 4)

```
Build every new piece this script needs (landmark, signs, posters, props, costumes, tags, new characters) in
EPISODE/design/episode.py (pattern: examples/ep05-wifi/design). Use rprops.py and roblox.py pieces where they fit.
Render the design stills, look at them, fix anything cut off or hidden, and send me DESIGN_SHEET.jpg with one line
per piece. Offer 2-3 options for any piece where the design is a real choice.
```

## 6. Shots and stills (gate 5)

```
Write EPISODE/episode.py: one shot per clause (0.7-2.5 s), cut with wcut(word index), tags and faces popping on
the word with wpop(index), the landmark in the first 2 s, a wide shot every 6-10 shots
(docs/ROBLOX_LOOK.md section 5; pattern: examples/ep05-wifi/episode.py). Run check until it passes with no
shot over 2.5 s. Render stills in groups of about 12 shots, look at every one against docs/ROBLOX_LOOK.md section 6,
fix and re-render the bad ones (at least two rounds), then send me the contact sheet with a line per group of shots
and a list of anything still weak.
```

## 7. Hook (gate 6)

```
Render the first ~15 s of EPISODE with render_threejs.sh EPISODE 0 F1 (F1 just before a cut), write the sound
cues for it (docs/SOUND.md: ElevenLabs sounds from sfx/ELEVENLABS_LIST.md if I have a key, tell me the credit cost
first; Pixabay otherwise), then finish.py with finish.json {"captions": "karaoke", "voice": "vo/voice_level.wav",
"loudness": "static", "music_loop": 20.5, "music_db": -9} and my music file {path or "none"}.
Rename the MP4s to *_hook*.mp4. Check frames across it (every tag visible, nothing static, screens real) and that the
short-term loudness stays within ±1 dB of -14 LUFS, and tell me what you could not check.
```

## 8. Full video (gate 7)

```
Render every frame of EPISODE with render_threejs.sh in the background (~10 min), then finish.py (clean file +
music file). Check the length, the loudness (about -14 LUFS, short-term within ±1 dB) and one frame per shot. If I
approve posting, ask me before making the paid voice take; after it, run words.py, level_voice.py, check,
render_threejs.sh and finish again.
```

## 9. Notes on a cut

```
Notes on EPISODE: {shot numbers from the contact sheet and what is wrong}. Fix only those shots, re-render their
stills, show me before/after, and don't touch other shots.
```
