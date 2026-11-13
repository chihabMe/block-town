# Prompts

Paste a prompt into Claude Code or Codex with the block-town skill installed. `{…}` are yours to fill in. The skill
folder is `SKILL`; the episode folder is `EPISODE` (for example `~/videos/ep06-shadows`). Rules and numbers come from
`SKILL.md`, `docs/RESEARCH.md`, `docs/SCRIPT.md`, `docs/ROBLOX_LOOK.md` and `docs/VOICE.md`. The block-look prompts
that used to be here are in `docs/GUIDE.md`.

## 1. Make the whole video (the master prompt)

```
Make an "In this world / In this town" video with the block-town skill, in the Roblox look.
Idea: {a rule, a theme, or "research and pick"}
Episode folder: {EPISODE}
Research folder: {e.g. ~/Documents/projects/tiktok-videos/research/in-this-world, or "skip research"}
Follow SKILL.md's gates and stop after each one for my answer:
0 research (tell me the Apify cost first), 1 five ideas, 2 three scripts, 3 voice (free Fish take),
4 design sheet, 5 contact sheet, 6 {4} opening variants as drafts, 7 a fast draft of the whole video and fix rounds,
8 the final full-quality render once I approve the draft.
Mark your recommended pick at every choice; if I say "go with yours", take it.
Don't spend money (Apify, paid voice, ElevenLabs) or download anything without asking me first.
```

## 2. Research (gate 0)

```
Research the "In this town / In this world" niche for new ideas. Follow docs/RESEARCH.md.
Read {research folder}'s newest TRENDS_*.md and ideas/RULE_BANK.md first.
Plan an Apify run (clockworks/tiktok-scraper, no video downloads): the queries, how many results, and the cost.
Wait for my yes, then run it, save the raw JSON under raw/{date}/, and write TRENDS_{date}.md: what changed, what
is winning (with numbers), what is saturated, the taken rules, the hook shapes that work. Give me the findings in
about 10 lines.
```

## 3. Ideas (gate 1)

```
Give me {5} "In this world / In this town" ideas for {theme, "anything", or "what the research says"}, following
docs/RESEARCH.md: rule as spoken (10 words or fewer), mood (at least three moods across them), a two-line story
(underdog, tries, twist), the landmark, why now (a pattern from the research, with a number), fresh (not taken,
not in RULE_BANK.md), and a score on docs/SCRIPT.md's five tests. One table, then your recommended pick and why in
one line. Add all of them to RULE_BANK.md with today's date.
```

## 4. Scripts (gate 2)

```
Write three scripts for idea {n}. Follow docs/SCRIPT.md: 60 seconds, about 240 words, one sentence a line,
the 8 beats with "everyone obeys" (a list of three) and "punished first", a callback and a fair twist whose clue is
hidden in beat 4. A, B and C must differ in twist, tone or underdog. Score each on the 12-point critic list, fix
anything under 8, and write all three to EPISODE/SCRIPT.md (pattern: examples/ep05-wifi/SCRIPT.md) with a beat table
for each. Recommend one. Put my pick (or yours, if I say "go with yours") in EPISODE/script.txt and list what the
pictures need: landmark, signs, props, tags, cast roles.
```

## 5. Voice (gate 3)

```
Make the narration for EPISODE with the free Fish model: copy examples/ep05-wifi/vo_config.json, run vo.py,
words.py, voice_check.py and level_voice.py. Tell me the length, words a minute, the voice_check table, and any
guessed words other than numbers. Send me vo/voice.wav. Don't use the paid model.
```

## 6. Design sheet (gate 4)

```
Build every new piece this script needs (landmark, signs, posters, props, costumes, tags, new characters) in
EPISODE/design/episode.py (pattern: examples/ep05-wifi/design). Use rprops.py and roblox.py pieces where they fit.
Render the design stills, look at them, fix anything cut off or hidden, and send me DESIGN_SHEET.jpg with one line
per piece. Offer 2-3 options for any piece where the design is a real choice.
```

## 7. Shots and stills (gate 5)

```
Write EPISODE/episode.py: one shot per clause (0.7-2.5 s), cut with wcut(word index), tags and faces popping on
the word with wpop(index), focus() in every shot, the landmark in the first 2 s, a wide shot every 6-10 shots
(docs/ROBLOX_LOOK.md section 5; pattern: examples/ep05-wifi/episode.py). Run check until it passes with no
shot over 2.5 s and still_check.txt is clean. Render stills in groups of about 12 shots, look at every one against
docs/ROBLOX_LOOK.md section 6, fix and re-render the bad ones (at least two rounds), then send me the contact sheet
with a line per group of shots and a list of anything still weak.
```

## 8. Opening variants (gate 6)

```
Run preflight.py on EPISODE and fix anything missing. Then make {4} opening variants of the first ~15 s with
openings.py new (same words; different first image, landmark reveal, camera or first action, one line each on what
differs). For each: cut its episode.py down to the hook shots and change them, run check until still_check.txt is
clean, render_threejs.sh VARIANT --draft, cues for the hook (Pixabay, or ElevenLabs only after telling me the
credit cost), finish.py VARIANT --draft. Then openings.py grid. Look at frames from every variant before sending.
Send me the grid and each draft, and say which you recommend and why.
```

## 9. Draft of the whole video (gate 7)

```
Move opening {X}'s shots into EPISODE/episode.py, run check, and delete openings/. Then render the whole video as a
draft: render_threejs.sh EPISODE --draft (in the background), cues for the whole video, finish.py EPISODE --draft.
Check one frame per shot (every tag visible, nothing static, screens real) and the loudness (short-term within
±1 dB of -14 LUFS), and tell me what you could not check. Send me <name>_draft.mp4.
```

## 10. Notes on a draft (gate 7, each review round)

```
Notes on EPISODE's draft: {times or shot numbers and what is wrong}. Fix only those shots, re-render just their
frames with render_threejs.sh EPISODE --draft F0 F1, run finish.py EPISODE --draft, show me before/after stills of
the fixed shots and the new draft. Don't touch other shots.
```

## 11. Final render (gate 8)

```
The draft is approved. Run preflight.py EPISODE --final. Ask me whether to make the paid voice take (if yes: vo.py
with the paid model, words.py, level_voice.py, check, and one more draft for me to approve). Then set finish.json
"render_fps": 240, "blur": 4 (and the grade if the story has a turn), run render_threejs.sh EPISODE in the
background and finish.py EPISODE with my music file {path or "none"}. Check the length, the loudness and one frame
per shot, then send me both MP4s. After I accept, delete threejs/, frames/ and frames_draft/.
```
