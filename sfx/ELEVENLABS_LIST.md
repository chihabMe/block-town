# ElevenLabs sound effects: draft list

Draft, 2026-11-12. Nothing has been generated yet. The narration is not affected: it stays `vo/voice.wav` from
`vo.py`. These are only effect files that `finish.py` mixes under it through `cues.json`.

## How to generate
- **Plan:** Starter ($6/month, 30,000 credits, includes the commercial licence). About 200 credits per generation.
- **Budget:** 46 sounds (38 core + 8 for ep05) × 3 tries ≈ 138 generations ≈ 27,600 credits. That just fits one
  Starter month. Later episodes
  reuse the library and only pay for a few new sounds.
- **Per sound:** set the duration (column below). Make 3 versions and keep the best one. Trim silence at the start,
  so the hit lands on the word.
- **Loudness:** normalise every file to the same peak (−1 dBFS). `cues.json` sets each cue's volume under the voice.
- **Names:** `el-<name>.mp3`, next to the Pixabay files. Add each file to `CREDITS.md` and `manifest.json`.
- **Never copy a famous sound** (the Roblox "oof", iPhone ringtones, TV-show stings). Describe the kind of sound.

## 1. Core library (reused in every episode)

### Phone and Wi-Fi (this channel's world)
| File | Prompt | Length | Use |
|---|---|---|---|
| el-signal-up | Bright rising digital chirp, three quick ascending blips like signal bars filling up, clean and cheerful | 0.8 s | Bars go up, "nice" moments |
| el-signal-down | Three descending digital blips that fade out, a sad deflating "no signal" sound, cartoonish | 1.0 s | Bars drop, "zero bars" |
| el-no-signal | Short dull double buzz, a phone error that is mildly annoying, not harsh | 0.6 s | "Zero bars", failed calls |
| el-spinner-loop | Soft rhythmic ticking of a loading wheel, quiet digital clicks, steady 4 per second, seamless loop | 3.0 s | Under every loading spinner |
| el-searching | Faint hopeful digital ping repeated with long gaps, like a phone searching for a network | 2.5 s | "Searching…" screens |
| el-buffering-stall | Digital stutter that freezes mid-sound, a video buffering and getting stuck | 1.2 s | Frozen phone, slow loading |
| el-message-in | Short friendly two-tone message pop, warm and bubbly, not a real phone brand tone | 0.5 s | Texts arriving |
| el-heart-pops | Rapid series of soft bubbly pops rising in pitch, like dozens of heart emojis appearing | 1.5 s | Emoji floods |
| el-wifi-zap | Sparkly electric zap with a shimmering tail, magical energy beam, not scary | 1.2 s | Signal beams, the tower firing |
| el-tower-hum-loop | Low warm electrical hum with a gentle pulsing shimmer, seamless loop | 4.0 s | Under tower shots |
| el-power-up | Upbeat ascending magical power-up whoosh with sparkles, video-game style | 1.5 s | Someone gets stronger Wi-Fi |
| el-power-down | Descending power-down tone, like a gadget running out of battery, comedic | 1.5 s | Someone loses Wi-Fi |

### Graphics on screen
| File | Prompt | Length | Use |
|---|---|---|---|
| el-tag-pop | Crisp cartoon pop with a tiny bounce, a sticker appearing | 0.3 s | Tags and icons popping in |
| el-bubble-pop | Soft round pop, a speech bubble appearing, light and quick | 0.3 s | Speech bubbles |
| el-text-slam | Short punchy thud with a paper flap, a big word stamping onto the screen | 0.5 s | Big words ("4K", "FROZEN") |
| el-stamp-x | Rubber stamp thump plus a short "wrong" buzz | 0.6 s | Red ✕ marks |
| el-counter-tick | Fast mechanical counter ticking up, like an odometer rolling | 1.0 s | Numbers counting |
| el-ding-correct | Bright cheerful ding, a correct answer on a quiz show (generic, not a known show) | 0.7 s | Good news |

### Comedy stingers
| File | Prompt | Length | Use |
|---|---|---|---|
| el-bonk | Cartoon bonk, a hollow knock on a head, comedic | 0.4 s | Small failures |
| el-sad-trombone | Short three-note sad brass "wah wah wah" falling | 1.6 s | Punchlines of failure |
| el-record-scratch | Vinyl record scratch that stops the music | 0.6 s | "And the worst part?" moments |
| el-gasp-crowd | Small crowd of people gasping together in surprise | 1.0 s | Shocking reveals |
| el-crickets | Awkward silence, crickets chirping | 2.0 s | Nobody reacts |
| el-cartoon-boing | Springy cartoon boing | 0.5 s | Jumps, surprise reactions |
| el-tiny-cheer | Small group of people cheering briefly, happy | 1.5 s | Wins |

### Cuts and impacts
| File | Prompt | Length | Use |
|---|---|---|---|
| el-whoosh-cut | Very short airy whoosh for a fast camera cut, clean, no tail | 0.35 s | Most shot cuts |
| el-whoosh-zoom | Whoosh that rises in pitch, a quick zoom-in toward the camera | 0.6 s | Punch-ins to a face |
| el-impact-boom | Deep cinematic boom with a short tail, dramatic but not scary | 1.5 s | Big reveals |
| el-riser-short | Short tension riser that builds for 2 seconds and cuts off | 2.0 s | Before the twist |
| el-reveal-shimmer | Soft magical shimmer swell, warm and emotional | 2.0 s | Heartwarming twist |

### Town ambience and foley (quiet beds under shots)
| File | Prompt | Length | Use |
|---|---|---|---|
| el-street-day-loop | Calm suburban street ambience: distant birds, light breeze, faint far-away traffic, seamless loop | 8.0 s | Under every street shot, very low |
| el-crowd-murmur-loop | Friendly crowd murmur outdoors, indistinct, no clear words, seamless loop | 6.0 s | Group shots, queues |
| el-footsteps-sneakers | Quick light footsteps of a kid walking on pavement in sneakers | 2.0 s | Walking shots |
| el-car-pass | A small car drives past from left to right, gentle | 2.5 s | Cars in shot |
| el-bus-idle | Big bus engine idling, then a short air-brake hiss | 2.5 s | Bus shots |
| el-door-open | Wooden front door opening with a soft creak | 1.0 s | Door scenes |
| el-pigeon-coo | A pigeon cooing softly, a couple of coos | 1.5 s | The pigeon |
| el-paper-rustle | Large paper map being unfolded and rustled | 1.5 s | Paper map |

### Night and horror (first used in ep07)
| File | Prompt | Length | Use |
|---|---|---|---|
| el-phone-buzz | A phone vibrating on a hard wooden table, two short buzzes, close and clear | 0.9 s | Phones buzzing, the 3 AM text |
| el-text-tone-eerie | A soft single message tone, slightly detuned and eerie, quiet room, not a real phone brand tone | 0.6 s | A message arriving at night |
| el-light-off | A light switch clicking off with a tiny electric hum cutting out | 0.4 s | Windows going dark |
| el-clock-tick | One deep heavy tick of a big old clock | 0.5 s | Clock hands moving |
| el-clock-bong | One deep clock bell strike with a long fading ring, dark and slow | 2.0 s | 3:00 strikes |
| el-blanket-rustle | A thick blanket quickly pulled up over someone's head, soft fabric rustle | 0.8 s | Hiding under blankets |
| el-lantern-creak | The metal handle of an old lantern creaking as it swings | 1.0 s | The watchman walking |
| el-dog-whimper | A small dog whimpering softly, scared but cute | 0.8 s | A scared pet |
| el-night-crickets-loop | Quiet suburban night: crickets, a faint distant breeze, seamless loop | 8.0 s | Under night street shots, very low |
| el-drone-low-loop | Low dark ambient drone, uneasy, slowly pulsing, no melody, seamless loop | 6.0 s | Under scary moments, very low |

## 2. ep05 extras (only for this episode)
| File | Prompt | Length | Use |
|---|---|---|---|
| ep05-4k-sparkle | Glossy bright sparkle swoosh, a super sharp HD image snapping into focus | 1.0 s | "4K" (words 25 and 246) |
| ep05-baby-giggle | Cartoon-style baby giggle, short and cute | 1.0 s | Babies have the fastest internet (word 37) |
| ep05-honk-held-back | A car horn that starts and is cut off instantly, comedic | 0.6 s | "Nobody honks" (s11) |
| ep05-yell | Muffled angry grown-up shout, no clear words, cartoonish | 0.8 s | The man yells (word 66) |
| ep05-lunch-tray | Lunchbox snapping shut and handed over | 0.8 s | Gave away my lunch (word 152) |
| ep05-mayor-poster | Big poster unrolled and slapped onto metal with a clang | 1.2 s | Face on the tower (word 168) |
| ep05-repair-laugh | Single friendly adult chuckle, short | 1.0 s | The repairman laughed |
| ep05-wifi-river | Long flowing shimmer, like a river of sparkles traveling far away | 3.0 s | Every bar going to Grandma's street (word 202) |

## 2b. ep07 extras (only for this episode)
| File | Prompt | Length | Use |
|---|---|---|---|
| ep07-icecream-jingle | A distant music-box ice-cream van tune, simple original melody, slightly out of tune and eerie at night | 3.0 s | The truck still playing music; ice-cream music at night |
| ep07-bin-rattle | A metal bin rattling hard with dozens of phones buzzing inside it | 1.5 s | "At 3 AM, the bin buzzed." |
| ep07-heartbeat | Two slow heavy heartbeats, tense | 1.2 s | Her finger on send |

## 3. ep05: current cue → new sound
| Moment (cues.json) | Now | New |
|---|---|---|
| Shot cuts s02 s05 s15b s16 s28 s30 s37 | whoosh-short | el-whoosh-cut (el-whoosh-zoom on face punch-ins) |
| word 8 "nicer" | sparkle | el-power-up |
| word 25 "4K" | ping | ep05-4k-sparkle + el-signal-up |
| word 29 "ten" (minutes) | error | el-buffering-stall |
| word 37 "fastest" | notification | ep05-baby-giggle + el-signal-up |
| words 44 54 60 87 141 152 157 228 254 (pops) | pop | el-tag-pop (el-bubble-pop on speech bubbles) |
| word 66 "yelled" | impact-bass-1 | ep05-yell + el-impact-boom |
| word 72 "froze" | glitch-1 | el-buffering-stall |
| words 74 91 133 143 153 161 (zero / fail) | error | el-no-signal; el-sad-trombone on the last "Still zero" (161) |
| words 100 237 "Searching" | click-soft | el-searching + el-spinner-loop under the phone shot |
| word 109 "And the worst part?" | impact-bass-2 | el-record-scratch |
| word 168 "face" (on the tower) | impact-bass-1 | ep05-mayor-poster + el-impact-boom |
| word 172 "Meanest" | whoosh | el-gasp-crowd |
| word 195 "zero." (it wasn't zero) | impact-bass-2 | el-impact-boom |
| word 199 "strongest" | sparkle | el-power-up |
| word 202 "I was just giving every bar away" | whoosh-cinematic | ep05-wifi-river |
| word 213 "Three hundred and twelve" | chime | el-counter-tick + el-ding-correct |
| word 218 "When I was six" | riser | el-riser-short |
| words 243 251 (messages) | notification | el-message-in |
| word 243 "forty-seven" | notification | el-heart-pops |
| word 258 "pigeon." | sparkle | el-pigeon-coo + el-tiny-cheer |
| **New:** under all street shots | none | el-street-day-loop, very low |
| **New:** tower shots s01 s02 s05 | none | el-tower-hum-loop + el-wifi-zap on the rings |
| **New:** s15b paper map | none | el-paper-rustle |
| **New:** s13 bus | none | el-bus-idle |

## Open questions
- Ambience beds under the narration: keep them very low (they compete with "Numbers" when it is added on TikTok).
- `finish.py` plays a file once per cue. Loops (spinner, hum, street) need a small change: a cue with a length that
  repeats the file.
