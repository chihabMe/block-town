# Research and ideas (gate 0 and gate 1)

Gate 0 is optional: it finds what is working in the niche right now, so gate 1's ideas start from evidence and not
from a guess. Run it for a new video when the newest trends file is more than about a week old, or when the user
asks. Skip it when the user brings their own idea.

The data belongs to the user's project, not to this kit. In the TikTok project it lives in
`research/in-this-world/`: `TRENDS_<date>.md` (the findings), `raw/<date>/` (the scraped JSON), `ANALYSIS.md` and
`REPORT.md` (the first big study), and `ideas/RULE_BANK.md` (every rule idea so far, used ones ticked). Ask for the
folder if a project has none.

## Gate 0: research

1. **Read what is already known.** Read the newest `TRENDS_*.md` and `RULE_BANK.md` first, so the scrape only answers
   what is new and the ideas don't repeat old ones.
2. **Plan the scrape and say what it costs.** Apify costs money, so get the user's yes before every run:
   - The actor used so far is `clockworks/tiktok-scraper` (search queries, hashtags, profiles, comments). Look up
     its current price with the Apify MCP (`fetch-actor-details`) and estimate the run's cost from the number of
     results.
   - For scale: on 2026-11-12, 250 videos plus 800 comments cost about $3.6.
   - Typical input: `research/in-this-world/input.json` (search "in this town / world / city ..." with the
     `/video` section, 40 a page). Never download videos, covers or avatars: metadata, captions and comments only.
   - Tell the user the queries, the result count and the cost, then wait for the yes.
3. **Run it**:
   - With the Apify MCP: `call-actor`, then `get-dataset-items`.
   - If the Apify server needs sign-in, tell the user to authorise it with `/mcp`. Don't ask for the token in chat.
   - Save the raw JSON to `raw/<date>/`. Keep each video's id, URL, caption, author handle, views, likes, comments,
     shares, length and date. For comments, keep only the text and the like count, never the commenter's name.
4. **Analyse.** Mark every number as measured or estimated, and say what the sample can't show: search results are
   not every upload, so "no hits" for an idea doesn't prove that nobody has made it.
   - Rank the videos by views, and by likes, comments and shares per view.
   - Group the top videos by rule family (economy, horror, school, body, meta, viewers choose), mood and form, and
     look at their hooks (the exact first line) and their length.
   - Read the top comments: what viewers argue about, ask for, or quote.
   - Make a "taken" list: rules other creators have already made. These are never reused, translated or reworded.
5. **Write `TRENDS_<date>.md`** with:
   - what changed since the last file
   - the patterns that are winning, each with view counts
   - what is saturated
   - the taken list
   - openings that are working, as hook shapes (not copied lines)

## Gate 1: ideas

Show **five ideas** by default (the user can ask for another number), as one table plus a recommended pick. Each idea:

| Field | What |
|---|---|
| Rule | as spoken, 10 words or fewer, starting "In this town," or "In this world," |
| Mood | comedy, horror, heart, meta, ... (mix them) |
| Story | two sentences: the underdog, what they try, the twist |
| Landmark | the big thing on screen in the first 2 s that shows the rule |
| Why now | the pattern from gate 0 it rides on, with a number ("horror rules: 5 of the top 10 this month") |
| Fresh | not on the taken list and not in `RULE_BANK.md`'s used rules |
| Score | docs/SCRIPT.md's five tests, x/5 |

Rules for the ideas:
- Ideas are new. Study other videos for craft (hook shape, pacing, form), never for their rule, joke, twist or
  script.
- Use at least three moods across the five.
- At least one idea uses a form that is winning right now (viewers choose, meta), if gate 0 found one.
- Add all five to `RULE_BANK.md` (marked with the date), so ideas the user passed on stay for later.

When the user picks one (by number, or "go with yours" = the recommended one), go on to gate 2.
