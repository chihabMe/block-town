# Posting (gate 9: the post kit)

After the final MP4 is approved, make `EPISODE/POST.md`: everything the user needs to post the video, in the order to
do it. The user posts; we never post for them.

```bash
python3 -I SKILL/blockworld/post_kit.py EPISODE     # first run: writes a starter post.json and stops
# fill in post.json (below), then:
python3 -I SKILL/blockworld/post_kit.py EPISODE     # checks, cover frames in EPISODE/post/, EPISODE/POST.md
```

The pattern is the Hushers posting guide (`episodes/ep20-hushers/POSTING.txt`, Nov 2026), which the user posted from.

## post.json

```json
{
 "caption": "In this town, monsters hunt anyone who goes quiet 🤫 HUSS HUSS HUSS 😨\n\nAll night the whole town ...\n\nPart 2 is on my page 👀 Could YOU huss until sunrise? 👇\n\nA Roblox horror story from our town. Follow for more \"In this town\" stories 🏙️",
 "hashtags": ["#inthistown", "#roblox", "#husshusshuss", "#robloxhorror", "#scarystory"],
 "pinned_comment": "Would you survive one night here? Could you chant until sunrise? 😰",
 "yt_title": "",
 "file": "clean",
 "cover_times": [],
 "ai_label": true
}
```

**Caption**
- **Line 1 is the search hook**: the rule as the script says it ("In this town, ..."), plus one emoji. In a later
  part: "PART 2: In this town, ...". TikTok search reads the caption, the spoken words and (some guides say) the text
  on screen; the rule is in all three.
- **One CAPS word** (the Nov 4 scrape: captions with one had a 121k median against 23k): the rule's key word or the
  sound ("HUSS", "LEARN", "YOU").
- Then 2-3 short lines: the rule's world, then what goes wrong. **Never the twist.**
- A question for the comments ("Could YOU huss until sunrise? 👇"). A series part points to the next one ("Part 2 is
  on my page 👀") and a later part also back ("Part 1 is on my page").
- Last line: "A Roblox {horror} story from our town. Follow for more "In this town" stories 🏙️".
- Hashtags in `hashtags`, not in the caption: 3-6, the niche tag (`#inthistown` or `#inthisworld`), `#roblox`, one
  genre tag (`#robloxhorror`, `#scarystory`, ...), one tag for the story's own word if it has one (`#husshusshuss`).

**Pinned comment**: a question people will answer, about them under the rule ("Would you survive one night here?")
or a guess ("Who is the 4th voice under the bed? Wrong answers only 👇").

**file**: `"clean"` (the default) is `<name>.mp4`; the user adds "Numbers" by TEMPOREX from TikTok's sound picker.
`"music"` is `<name>_music.mp4`. If its music was cut from another creator's video, say so: TikTok may mute it.

**ai_label**: ask the user. The narration is a generated voice; third-party guides say TikTok's label is mainly for
realistic AI pictures, and the Hushers were posted with it on.

## What the kit checks

`post_kit.py` fails (exit 1, the failures at the top of POST.md) if:
- the MP4 is 61 s or shorter (Creator Rewards pays only for videos over one minute; we aim for 90-120 s);
- the caption still has a `<...>` placeholder, line 1 doesn't start with the rule, or there is no CAPS word;
- there aren't 3-6 hashtags with the niche tag, or there is no pinned comment;
- the AI label isn't decided;
- a series part doesn't point to the next part (and, from Part 2 on, back to the previous one);
- the YouTube title with " #Shorts" is over 100 characters.

## Cover

`EPISODE/post/cover_N_*.jpg`: the frame just after the hook line, the frame where the grade turns (if `finish.json`
has one), the frame at 80 % (around the twist) and any `cover_times`. Look at them and recommend one: the rule
must be readable in it (the landmark, the creature, the sign) and a face should show the feeling. Don't pick a
frame that gives the twist away.

## Series

POST.md lists the steps for a series part (`series.json`): the playlist, when to post the next part (3-6 hours
later, while this one is still being pushed), the video reply on the previous part's top "part 2?" comment, and the
new pinned comment "Part 2 is up 👉 on my page". Only about 1 in 9 Hush Part 1 viewers found Part 2, so these steps
matter as much as the video.

## YouTube Shorts

The same MP4 goes on YouTube Shorts (up to 3 minutes). POST.md has the title (line 1 + " #Shorts") and the
description (the caption, the hashtags and "Fan-made animation, not affiliated with Roblox.").

## After posting

48 hours later, ask the user for a screenshot of TikTok Studio's retention graph (Content > the video > Audience
retention). Match the steepest drops to the shots and words at those seconds, and write what you learn into the
research folder for the next ideas and scripts.
