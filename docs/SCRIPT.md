# Writing the story

An "In this town / In this world" video is one strange rule and one story it causes, told by a fast narrator over
pictures that change every second. Target a **60-second Short: about 240 words**, which the voice reads in about
60 s (docs/VOICE.md).

## 1. The rule

The first words are exactly "In this town," or "In this world,", then the rule. Test every candidate:

| Test | Question |
|---|---|
| Self-insertion | Will viewers comment what *they* would do, or how they'd do under it ("my Wi-Fi would be dead")? |
| Loophole | Is there a gap people will argue about in the comments? |
| Class system | Does it make winners and losers (rich/poor, tall/short, loud/quiet)? |
| Twistable | Can it mean something else at the end, fairly? |
| Sayable | Is it 10 words or fewer, concrete, and something you can **show** as a landmark? |

Show the user three rules in different moods (comedy, horror, heart), each with its landmark idea. Never reuse a rule,
joke or twist from another creator's video.

## 2. The shape (8 beats, with what the top videos add)

| Beat | Time (60 s) | What happens |
|---|---|---|
| 1 Rule | 0:00 | The rule, one sentence. The landmark and the official sign are on screen in the first 2 s. |
| 2 How it works | 0:03 | "You see," then 3–4 fast, concrete, funny consequences with numbers ("stream movies in 4K"). |
| Everyone obeys | ~0:12 | A list of three: "Nobody honks. Nobody cuts in line. Not even the bus driver." |
| Punished first | ~0:17 | Show the punishment on someone else before the hero ("his phone froze for three whole days"). |
| 3 Underdog | ~0:22 | "My name is ___" and why the rule hurts them. Plant a word or object that comes back at the end. |
| 4 Stakes | ~0:30 | Someone they love needs them. Hide the twist's clue here, in plain sight. |
| 5 Tries | ~0:40 | Three escalating attempts with ticking numbers, each failing ("I held fifty doors. Zero bars."). |
| 6 Cost | ~0:48 | The system pushes back (a poster, a new law, friends turn away). |
| 7 Twist | ~0:52 | The rule meant something else all along, and it was fair from the first line. |
| 8 Button | ~0:57 | Two lines at most: the callback, now funny, or one quotable line. Then stop. |

Style:
- 4–10 words a sentence, one idea each, **every sentence something the camera can show**.
- At least six numbers. Short dialogue, max 8 words, said by the narrator.
- Kid-level words, no swearing or gore, English for ages 10–16.
- One sentence per line in `script.txt`: the narration is one take, and the lines only help planning.

## 3. Options and the critic check

Write the main script (option A) and a second ending (option B: a different twist or tone). Then score option A,
1–10 each, and fix anything under 8 before showing it (or say why a lower score is on purpose):

1. Opens with "In this town" / "In this world".
2. Rule ≤ 10 words, concrete, visual.
3. Self-insertion. 4. A loophole to argue about.
5. Underdog before ~0:25 and hurt by the rule. 6. Stakes before 0:50.
7. Escalation with ticking numbers. 8. Twist reinterprets the rule, with its clue hidden earlier.
9. Ends within two lines, no unresolved cliffhanger. 10. A callback from the first 30 s.
11. Short, visual sentences. 12. About 240 words (60 s).

Write it all into `EPISODE/SCRIPT.md` (`examples/ep05-wifi/SCRIPT.md` is the pattern) and put the chosen version in
`EPISODE/script.txt`.

## 4. From script to shots (gate 5)

- **One shot per spoken clause**, 0.7–2.5 s each; about 40 shots for 60 s. Split any line over 2.5 s.
- **The picture shows the exact words being said**: "4K" → a "4K" tag pops on the word; "froze" → a frozen phone.
- Cut 0.04 s before a word: `wcut(i)` with the word's index in `script.txt` (0-based).
- Pop tags and faces on the word: `wpop(i)` returns 0 → 1 over 0.14 s when word `i` is spoken.
- Phone screens, posters and signs are **inserts**: a close shot of the object, often while the line says it.
- Every few shots, a wide shot of the street or the landmark so the viewer knows where they are.
