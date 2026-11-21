# Writing the story

An "In this town / In this world" video is one strange rule and one story it causes, told by a fast narrator over
pictures that change every second.

**Length: 90-120 seconds, about 360-470 words** (the voice reads about 237 words a minute, docs/VOICE.md). Aim for
about 105 s (~410 words). A light comedy can be 70-90 s (~280-350 words). **Never under 61 s**: TikTok's Creator
Rewards only pays for videos over one minute, and `preflight.py` and `post_kit.py` flag anything shorter.

Why (research, Nov 2026): the 20 million-view niche stories we measured run 56-155 s with a 116 s median; the big
Roblox story channels make 1:45-2:30; the French horror hits run 88-196 s. A 60 s script has no room to build the
town, plant the clues and land the twist (`research/skill-gaps-2026-11-21/REPORT.md`).

## 1. The rule

The first words are exactly "In this town," or "In this world,", then the rule. Test every candidate:

| Test | Question |
|---|---|
| Self-insertion | Will viewers comment what *they* would do, or how they'd do under it ("my Wi-Fi would be dead")? |
| Loophole | Is there a gap people will argue about in the comments? |
| Class system | Does it make winners and losers (rich/poor, tall/short, loud/quiet)? |
| Twistable | Can it mean something else at the end, fairly? |
| Sayable | Is it 10 words or fewer, concrete, and something you can **show** as a landmark? |

Show the user five ideas in at least three moods (comedy, horror, heart, meta), each with its landmark idea and a
recommended pick (`docs/RESEARCH.md` has the table). Never reuse a rule,
joke or twist from another creator's video.

## 2. The shape (8 beats, with what the top videos add)

Times are a share of the whole video, with the second it falls on in a 105 s video.

| Beat | When (105 s) | What happens |
|---|---|---|
| 1 Hook | 0:00 | Two lines. Line 1: the rule, one sentence, said to "you". Line 2: the contrast, one person on the losing side or what's about to go wrong. The landmark and the official sign are on screen in the first second. See the hook check below. |
| 2 How it works | 5 % (0:05) | "You see," then 3–4 fast, concrete, funny consequences with numbers ("stream movies in 4K"). |
| Everyone obeys | 12 % (0:13) | A list of three: "Nobody honks. Nobody cuts in line. Not even the bus driver." |
| Punished first | 18 % (0:19) | Show the punishment on someone else before the hero ("his phone froze for three whole days"). |
| 3 Underdog | 25 % (0:26) | "My name is ___" and why the rule hurts them. Plant a word or object that comes back at the end. |
| 4 Stakes | 35 % (0:37) | Someone they love needs them. Hide the twist's clue here, in plain sight. |
| 5 Tries | 50 % (0:53) | Three escalating attempts with ticking numbers, each failing ("I held fifty doors. Zero bars."). In a 105 s video each try gets its own small scene, and the second one can be a false win. |
| 6 Cost | 70 % (1:14) | The system pushes back (a poster, a new law, friends turn away). |
| 7 Twist | 80 % (1:24) | The rule meant something else all along, and it was fair from the first line. |
| 8 Button | 95 % (1:40) | Two lines at most: the callback, now funny, or one quotable line. Then stop. In a series part, the button is the new danger instead (section 5). |

Style:
- 4–10 words a sentence, one idea each, **every sentence something the camera can show**.
- At least six numbers. Short dialogue, max 8 words, said by the narrator.
- The longer length is for more story, not slower story: keep the pace (237 words a minute) and the 0.7-2.5 s shots.
  Use the extra time to show the town under the rule, plant the clues and give each try its own scene.
  Open a new question at least every 15-20 s.
- Kid-level words, no swearing or gore, English for ages 10–16.
- One sentence per line in `script.txt`: the narration is one take, and the lines only help planning.

### The hook check (the first two lines)

From Kallaway's "4 hook mistakes" video (Nov 2026). A hook has two jobs: the viewer knows at once what the video is
about, and wants to know what happens next. Test the first two lines on all four:

| Mistake | Test | Bad → good |
|---|---|---|
| Delay | Line 1 starts with the rule; its picture is on screen within 1 s. No warm-up line. | "This is the weirdest town ever…" → "In this town, you pay your parents rent." |
| Confusion | Line 1 is ≤ 12 kid-level words, active voice, and can only be read one way. Read it alone: could anyone picture it wrong? | "phones photograph whoever watches you sleep" → "at 3 AM, your phone photographs whoever is watching you sleep" |
| Irrelevance | The rule says "you" or "your", so viewers picture their own life under it. | "kids pay rent to their parents" → "you pay your parents rent" |
| Disinterest | Line 2 sets up a contrast (what the viewer expects against what the rule does to one person) and opens a question they must stay to answer. | "You see, rich kids get big rooms…" → "Max is three weeks late. Tonight, Mom changed the locks." |

After the hook, keep the loop going: open the next question before answering the last one. The caption with one CAPS
word and the first picture must tell the same hook for viewers watching with the sound off.

## 3. Options and the critic check

Write **three full scripts** (A, B, C) for the chosen idea, each a real alternative: a different twist, tone or
underdog, not the same story reworded. Score every one, 1–10 on each point below, and fix anything under 8 before
showing them (or say why a lower score is on purpose). Mark the recommended one; "go with yours" means that one:

1. Opens with "In this town" / "In this world".
2. Rule ≤ 10 words, concrete, visual.
3. Self-insertion. 4. A loophole to argue about.
5. Underdog by ~25 % and hurt by the rule. 6. Stakes by ~40 %.
7. Escalation with ticking numbers. 8. Twist reinterprets the rule, with its clue hidden earlier.
9. The ending. A single video: ends within two lines, nothing left open. A series part that isn't the last: a real
   result first, then one new danger in the last lines (section 5). 10. A callback from the first 30 s.
11. Short, visual sentences. 12. Length: 90-120 s, about 360-470 words (comedy 70-90 s); never under 61 s.
13. The hook check: no delay, no confusion, relevant, curious (score each; rewrite the first two lines until all four
    are 8 or more).

Write it all into `EPISODE/SCRIPT.md` (`examples/ep05-wifi/SCRIPT.md` is the pattern) and put the chosen version in
`EPISODE/script.txt`.

## 4. From script to shots (gate 5)

- **One shot per spoken clause**, 0.7–2.5 s each; about 40 shots a minute (about 70 for 105 s). Split any line
  over 2.5 s.
- **The picture shows the exact words being said**: "4K" → a "4K" tag pops on the word; "froze" → a frozen phone.
- Cut 0.04 s before a word: `wcut(i)` with the word's index in `script.txt` (0-based).
- Pop tags and faces on the word: `wpop(i)` returns 0 → 1 over 0.14 s when word `i` is spoken.
- Phone screens, posters and signs are **inserts**: a close shot of the object, often while the line says it.
- Every few shots, a wide shot of the street or the landmark so the viewer knows where they are.
- **A motion graphic at least every 8 seconds** (the user's rule, Nov 2026): a `comic()` word that pops and shakes,
  a `timecard()` that slides in, a `pop()` or the `endcard()`, on a word the narration says ("FREEZE!", "SINCE
  TUESDAY", "RUN?!"). Plain tags (`card`/`put`) don't count. `examples`: `episodes/ep-freeze-hook/episode.py`.
- Pop-up graphics (name tags, meters, "+1" pops, comic words, time cards, the top bar, the end card) come from
  `blockworld/overlay.py`. House style: "Roblox game UI" (outlined text on a see-through dark plate) with yellow comic
  words, picked by the user in Nov 2026. Its docstring lists every call.

## 5. Series (Part 1, Part 2, ...)

A series is a story told in 2-3 videos, each 90-120 s. On our channel it is what works best: Hush Part 1 kept growing
for days while single videos stopped after a day, and "Part 2" videos had a 672k median in the Nov 4 scrape (small
sample). But only about 1 in 9 Hush Part 1 viewers found Part 2, so every part has to stand alone and point clearly
to the next one.

**When.** Offer it at gate 1 for any idea with a mystery or a monster (horror, creature rules, "who is it?"), and
mark which of the five ideas would work as a series. The user decides. A comedy rule is usually a single video.

**Plan the whole series before writing Part 1.** At gate 2, write Part 1 in full and a 3-line outline of each later
part (what happens, the result it gives, the new danger it ends on). Part 1's last danger must be one the outline
pays off.

**The series bible.** One `SERIES.md` beside the part folders (`episodes/ep20-hushers/SERIES.md`, parts in `part1/`,
`part2/`, ...), written at gate 2 and read before every later part's script, designs and shots:
- the rule, word for word as Part 1 says it;
- the cast: who, their outfit and face, their voice settings if they speak;
- the places and the landmark (with their `place()` calls);
- the creature or prop designs that must not change (file and function names);
- what each part showed and what it left open (update it after each part is posted);
- the look: mood, grade, sounds that repeat (a chant, a knock).

**series.json** in every part folder, read by `preflight.py` and `post_kit.py`:

```json
{"name": "The Hushers", "part": 1, "parts": 3, "bible": "../SERIES.md", "playlist": "The Hushers"}
```

**Part 1 script.**
- The normal 8 beats, but the button is the new danger: give a real result first (the power comes back, the try
  works), then open one new danger in the last 2-3 lines. "Wait for Part 2" with nothing solved is weak.
- The last spoken line points to the next part: "Part two is on my page."
- Score critic item 9 on the series rule, not the single-video one.

**Part 2 and later.**
- Line 1 is the same rule, word for word (the search hook and the sound-off hook stay the same).
- Line 2 is a one-line recap that is also a hook ("And last night, one of them was breathing our chant at our
  window."). Most Part 2 viewers come from the For You feed and never saw Part 1, so it has to make sense alone.
- Pay off Part 1's danger in the first third, then open the next one. The last part ends like a single video.
- Same cast, places, designs and sounds as the bible. Don't switch looks between parts.

**On screen** (`overlay.py`):
- `hud(None, "PART 1")` top right for the hook (first ~3 s) and for the last ~5 s.
- The last ~2 s: `timecard("PART 2", t, dur=2.0, sub="ON MY PROFILE")`. In the last part: an `endcard()` question
  instead.

**Posting** is in the post kit (`post_kit.py`, gate 9): the order, the gap between parts (3-6 h), the playlist, the
pinned comments and the video reply that links Part 2 from Part 1's comments.
