# Prompt pack: block-style videos

Prompts for building a video in the block look. They are written for any coding agent that has this skill (Claude Code, Codex, or Grok), and
every one of them relies on [`GUIDE.md`](GUIDE.md): the prompts say *what* to make, the guide
says *how it must look and move*. Replace the `{curly}` fields.

- **To make a whole video, use prompt 1 only.** It runs prompts 2–4 and 9 by itself and stops for approval at
  each stage.
- Prompts 2–10 are for doing or redoing one piece.
- The user supplies the script. Prompt 1 turns that script into the episode.

The shortest form that works:

```
Make a block-style video. Idea: {In this town, ...}. Script: {path or pasted text}.
Follow this file, prompt 1. The skill folder is the one that contains SKILL.md.
```

---

## 1. Make the episode (the master prompt)

```
Make a block-style episode.

RULE / IDEA: {In this town, ...}
SCRIPT: {paste it, or give the path to script.txt}
EPISODE FOLDER: episodes/{epNN-slug}/
HOW MUCH: {the whole script | only lines 1-N}
MOOD: {comedy | wholesome | horror}
HERO: {Nia | a new hero: name + one line}

Before anything else read docs/GUIDE.md (all of it) and docs/VOICE.md. The skill folder is the folder that contains SKILL.md. The guide is the law for the town, the characters, the
movement, the camera, the captions and the sound. If the script needs something
the guide lists as "not built yet", say so in the plan and show a test still of
it before using it.

Fixed rules:
- Free and offline only: Blender, the local Kokoro voice, the bundled sound
  effects. No paid tools or APIs. Ask before downloading anything.
- Our own designs only. Nothing copied from other creators' videos, no Roblox
  catalog items, no reference voice clips, no music in the file.
- Keep the recurring cast exactly as the guide's cast table describes them.
- Report honestly: the voice match score, anything not checked, anything that
  does not match the guide.

Work in these stages. Stop after each one, show me the result, and wait for
my OK. Where there is a creative choice, give me 2-3 options.

1. PLAN. Write three sheets into the episode folder as PLAN.md:
   a world sheet (prompt 2), a cast sheet (prompt 3) and a shot plan for every
   line (prompt 4).
2. VOICE. Make the narration with the settings in the guide, get the word
   times, run blockworld/words.py. If voice_match.py is on this machine, score the take and give me the number. Otherwise say the locked Kokoro settings were used (the intro scored 0.847) and give me the audio.
3. NEW DESIGNS. One still of every new character, prop and face, next to a
   known character.
4. STILLS. Two stills of every shot. Check each one against the guide's
   checklist yourself (prompt 9) and fix what fails before showing me a
   contact sheet.
5. HOOK. Render and finish the first 10-15 seconds.
6. FULL RENDER. Render the rest in the background, add captions and sound,
   check the final file against the guide's checklist, watch and listen to it,
   and tell me what you did not check.
```

---

## 2. World sheet (dress the town for this rule)

```
Write the world sheet for this episode, following section 3 of
docs/GUIDE.md.

RULE: {In this town, ...}
SCRIPT: {path}

The street itself never changes. Decide only:
1. RULE BILLBOARD: title "TOWN RULE" + the rule in 3-5 words.
2. TWO SHOP SIGNS that joke about the rule (max 3 words each). Give 3 options
   for each.
3. SET PIECES: every place or object the script names. For each one:
   name | script line that needs it | built from which boxes (5-25 parts) |
   size in studs next to a 5.3-stud person | the text on it (max 3 words a line) |
   where it stands (x, y) and which way it faces | which shots use it.
   Reuse one set piece for several lines wherever the script allows.
   Mark each as BUILT (already in the code), NEW, or NOT BUILT YET per the guide.
4. THE NUMBERS: every number in the script that must be seen (heights, money,
   ages, counts) and how it appears: a tag over a head, a sign, a counter.
   Tag colours: yellow neutral, green good, red bad.
5. TIME OF DAY per beat of the script: day, dusk or night, and why.
6. THE CALLBACK OBJECT: the thing from the underdog beat that returns in the
   last shot.

Keep the town muted and the signs bright. Output as tables.
```

## 3. Cast sheet

```
Write the cast sheet for this episode, following section 4 of
docs/GUIDE.md.

SCRIPT: {path}

1. List every person the script mentions, in order of first appearance.
2. Give each one to a recurring cast member if the role fits (the guide's cast
   table). Do not change a recurring character's look.
3. Only for a named person the cast cannot play, design a new character:
   name | role | skin | shirt (a colour nobody else on screen wears) | trousers |
   hair style and colour (a style nobody else on screen has) | sleeves |
   ONE clothing detail | ONE signature item | scale.
   Give 2 options for a new main character.
4. For every character: the faces they will need (from the guide's face list),
   and their size in each part of the story if size matters.
5. List any face that is missing from the face list and describe it in one line
   (eyes, brows, mouth).
6. Background people: which recurring characters fill the street and crowds.

Output as tables, plus the exact character(...) line for each new character.
```

## 4. Shot plan (script to shots)

```
Turn this script into a shot plan, following sections 5-8 of
docs/GUIDE.md.

SCRIPT: {path}       WORD TIMES: {vo/words.json, or "not made yet"}
WORLD SHEET and CAST SHEET: {PLAN.md}

Rules:
- One shot per clause: a new picture each time the narrator names a new thing.
  The picture shows exactly the words being said.
- First 12 seconds: 0.7-2.0 s per shot. After that: 1.2-2.5 s. Nothing over 2.5 s.
- Every shot starts on a word (the cut word). If the word times exist, give
  the start time; if not, estimate at 250 words a minute.
- Every shot has ONE event on a spoken word: a pose snap, a tag or bubble pop,
  an entrance, a size change. Name the word.
- Every shot has ONE camera move. Never two neighbouring shots with the same
  size and angle.
- Use only moves, faces and camera set-ups from the guide. If a shot needs
  something else, mark it NEW and describe it.
- Two or three characters act; everyone else only breathes.
- Faces, tags and bubbles in the top 55% of the frame.
- Reuse a staging with a new angle before inventing a new place.
- Follow the guide's table "what each kind of line looks like" for the 8 beats.

Output one row per shot:
| # | Cut word (number) | Words covered | Start-length (s) | Place | Who (size, face) |
| Start pose -> event on "word" -> end pose | Camera (close/medium/wide, set-up, move) |
| Tag / bubble / sign text | Sound | BUILT or NEW |

Then list: total shots, average shot length, the longest shot, every NEW item,
and the 3 shots you are least sure about with a second option for each.
```

## 5. Animate shots (write the shot functions)

```
Write the shot functions for shots {N-M} of episodes/{epNN-slug}/PLAN.md in
episode.py, following section 5 and 6 of docs/GUIDE.md and the
pattern of examples/ep01-intro/episode.py. Run it only through blockworld/run.py.

For each shot:
- A function f(t, d, T) that sets, on every frame: the size, place, pose and
  face of every visible character, the camera, and every tag or bubble.
- The event uses snap() on its word's time; the face changes when snap > 0.
- Held poses use stand() with a different phase per character.
- The camera always moves: mix() between two positions with smooth(t / d),
  a punch-in with snap(), or a shake after an impact.
- Arms are raised outward, never forward across the face.
- No slow blends on characters.

Then render two stills of each shot, look at every still, check it against the
guide's "every still" checklist, fix what fails, and show me the contact sheet
with a one-line note per shot on what you changed.
```

## 6. New prop or place

```
Build a new set piece for the block town, following section 3.6 of
docs/GUIDE.md.

WHAT: {e.g. a school bus stop | Nia's bedroom | a bank counter}
USED FOR: {the script lines / shots}
TEXT ON IT: {max 3 words a line, or none}

- Boxes only (cylinders only for wheels), 5-25 parts, one parent, front on -Y.
- Muted wall colours or greys from the guide's colour table; only the sign is
  bright.
- Sized against a 5.3-stud person.
- Give me 2 design options in one line each first if the shape is not obvious.
- Render one day still with Nia and Man standing next to it, from the camera
  position its shot will use, and show it to me before using it.
```

## 7. New character

```
Design a new character for the block cast, following section 4 of
docs/GUIDE.md.

WHO: {name, age, role in the story, one line about their personality}
APPEARS WITH: {which recurring characters share their shots}

Give 2-3 options as a table: skin | shirt | trousers | hair style + colour |
sleeves | one clothing detail | one signature item | scale.
The shirt colour and hair style must differ from everyone they appear with.
After I pick, write the character(...) line, render a front and a
three-quarter still next to Nia and Man, and show me.
```

## 8. New face

```
Add a face to blockworld/faces.py, following
section 4.5 of docs/GUIDE.md.

FEELING: {e.g. crying | sleepy | disgusted | sly wink}
USED BY: {character, shot}

Draw it with the existing helpers (eye_dot, eye_wide, eye_closed, brow, arc,
zigzag, blush) in the same style: thick black shapes, a white glint in the
eyes, features in the middle of the square. Add it to NAMES, regenerate the
sheet, and show me the new face next to "smile" and "shock" at head size.
```

## 9. Check the stills (run before showing me anything)

```
Check every still in {stills folder} against section 11 of
docs/GUIDE.md. Look at each image; do not judge from the code.

For each shot answer yes or no:
1. Is every face visible, lit, and wearing the right expression?
2. Is anything (arm, tag, pole, tree, prop) covering a face or the hero?
3. Are faces, tags and bubbles in the top 55%, and is the bottom 20% and the
   right 15% free of anything important?
4. Can the tag or sign be read at phone size?
5. Is anyone sinking, floating or overlapping another character?
6. Does the picture show the words spoken in that shot?
7. Does it differ in size or angle from the shot before and after?

Output a table: shot | pass or fail | what is wrong | the fix. Apply the fixes,
re-render only those stills, and check them again. Tell me which shots you
could not make pass.
```

## 10. Giving notes on a draft

Notes work best in this form (one line each):

```
Fix these in episodes/{epNN-slug}:
- shot 5: {what is wrong} -> {what you want instead}
- shot 12: {the tag is too small / too fast / wrong colour}
- all shots: {a rule to add, e.g. "push in faster"}
Follow docs/GUIDE.md. Re-render only the frames that change,
show me stills of the fixed shots first, and if a note changes a general
rule, update the guide as well.
```

---

## Worked example: the sheets for the ep01 intro (lines 1–4)

**World sheet**

| Item | Choice |
|---|---|
| Rule billboard | TOWN RULE / "1 LIE = 1 INCH", with a ruler strip |
| Shop signs | "TALL & SMALL", "HONEST PIES" |
| Set piece 1 | HEIGHT CHECK wall: a 30-stud ruler wall with foot marks on the right sidewalk at y = 60. Lines 1–2 (the liar, the line-up, tall vs small) |
| Set piece 2 | HONEST AL'S CARS: a sign on a pole with bunting, a red car with a "LIKE NEW!" sticker, at y = 120–126. Line 4 |
| Set piece 3 | A shoebox house (door, window, doormat, mailbox) on the left sidewalk. Line 4 |
| Numbers | Heights as tags over heads: green for tall, red for short. "−1 INCH" in red when the rule hits. "7 in" on the salesman |
| Time of day | Day throughout (rule and world-building) |

**Cast sheet**

| Script person | Played by | Size | Faces |
|---|---|---|---|
| A liar ("every lie you tell") | Man | 1.0 → 0.86 | smug → shock |
| A witness | Teacher | 0.85 | glasses |
| "Everyone here" | Tall 1.5, Gran 0.42, Dad 1.0, Boy 0.5, Teacher 0.85, Kid 1.25, Man 0.88 | – | happy, smug, smile, angry, stern |
| The honest one / the liar | Tall 1.4 / Boy 0.5 | – | happy / angry → stern |
| A baby (new) | Baby: all skin colour, white trousers, one curl | 9 | smile → happy |
| A car salesman (new) | Sal: blue shirt, yellow tie, black side part | 0.11 | smug → happy |

**Shot plan**: the 9-row table in section 7.4 of the guide.
