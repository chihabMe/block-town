"""Gate 9: everything needed to post a finished episode, in EPISODE/POST.md.

    python3 -I SKILL/blockworld/post_kit.py EPISODE                 check post.json, pick cover frames, write POST.md
    python3 -I SKILL/blockworld/post_kit.py EPISODE --video F.mp4   use this file instead of the one it finds

The first run, if there is no EPISODE/post.json yet, writes a starter post.json from script.txt (and series.json)
and stops. Fill in the caption, the CAPS word and the pinned comment (docs/POSTING.md), then run it again.

post.json:
    caption         the TikTok caption. Line 1 is the search hook: "In this town, ..." (series: "PART 2: In this town,
                    ..."), with one CAPS word somewhere. Hashtags go in "hashtags", not here.
    hashtags        3-6 tags, one of them #inthistown or #inthisworld
    pinned_comment  the comment to pin right after posting (a question people will answer)
    yt_title        optional YouTube Shorts title (default: line 1 of the caption); " #Shorts" is added
    file            "clean" (default: <name>.mp4, add "Numbers" by TEMPOREX in TikTok's sound picker) or "music"
    cover_times     optional extra cover frames, in seconds
    ai_label        true or false: whether to switch on TikTok's AI-generated label (the user's choice)

Writes EPISODE/post/cover_*.jpg (cover candidates: the hook, the twist, the grade's turn, any cover_times) and
EPISODE/POST.md. Exit code 1 if a check fails; POST.md is written either way, with the failures at the top.
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

MIN_LEN = 61.0                       # TikTok Creator Rewards: videos over one minute
NOT_AFFILIATED = "Fan-made animation, not affiliated with Roblox."


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def duration(path):
    r = run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path))
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def find_video(ep, conf, pick):
    """The file to post: <name>.mp4 (clean) or <name>_music.mp4, else the newest MP4 that isn't a draft."""
    if "--video" in sys.argv:
        return Path(sys.argv[sys.argv.index("--video") + 1]).expanduser().resolve()
    want = ep / (f"{ep.name}_music.mp4" if pick == "music" else f"{ep.name}.mp4")
    if want.exists():
        return want
    others = [p for p in ep.glob("*.mp4") if "_draft" not in p.name and "_plain" not in p.name]
    return max(others, key=lambda p: p.stat().st_mtime) if others else None


def script_lines(ep):
    f = ep / "script.txt"
    return [l.strip() for l in f.read_text().splitlines() if l.strip()] if f.exists() else []


def word_times(ep):
    f = ep / "vo" / "times.json"
    return json.loads(f.read_text()) if f.exists() else []


def starter(ep, series):
    """A post.json to fill in, made from the script's first line."""
    lines = script_lines(ep)
    hook = lines[0] if lines else "In this town, ..."
    if series and series.get("part", 1) > 1:
        hook = f"PART {series['part']}: {hook}"
    nxt = ""
    if series:
        p, n = series.get("part", 1), series.get("parts", 1)
        nxt = f"Part {p + 1} is on my page 👀" if p < n else ""
        if p > 1:
            nxt = (nxt + " " if nxt else "") + "Part 1 is on my page."
    caption = "\n\n".join(x for x in [hook + "  <- add one CAPS word and an emoji",
                                      "<2-3 lines: the rule's world, then what goes wrong, without the twist>",
                                      (nxt + " " if nxt else "") + "<a question for the comments> 👇",
                                      "A Roblox story from our town. Follow for more \"In this town\" stories 🏙️"] if x)
    niche = "#inthisworld" if "in this world" in hook.lower() else "#inthistown"
    return {"caption": caption, "hashtags": [niche, "#roblox", "#robloxstory", "#<genre: #robloxhorror, ...>"],
            "pinned_comment": "<a question people will answer> 👇",
            "yt_title": "", "file": "clean", "cover_times": [], "ai_label": None}


def covers(ep, video, length, times, lines, conf, extra):
    """Cover candidates: the end of the hook line, the grade's turn, 80 % (the twist), any extra times."""
    picks = []
    if times and lines:
        n = len(lines[0].split())
        if n <= len(times):
            picks.append(("hook", times[n - 1]["t1"] + 0.3))
    word = (conf.get("grade") or {}).get("word")
    if isinstance(word, int) and times and word < len(times):
        picks.append(("turn", times[word]["t0"] + 0.4))
    picks.append(("twist", 0.8 * length))
    picks += [(f"t{t:g}", float(t)) for t in extra]
    out = ep / "post"
    out.mkdir(exist_ok=True)
    for old in out.glob("cover_*.jpg"):
        old.unlink()
    made = []
    for i, (why, t) in enumerate(picks, 1):
        t = max(0.0, min(t, length - 0.1))
        f = out / f"cover_{i}_{why}.jpg"
        run("ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-q:v", "2", str(f))
        if f.exists():
            made.append((f, why, t))
    return made


def checks(post, series, length, video):
    """(ok, what, fix) rows."""
    out = []
    cap = post.get("caption", "")
    first = cap.strip().splitlines()[0] if cap.strip() else ""
    out.append((video is not None, f"video file: {video.name if video else 'none found'}",
                "run finish.py EPISODE, or pass --video FILE"))
    if length is not None:
        out.append((length > MIN_LEN, f"length {length:.1f} s (over {MIN_LEN:.0f} s for Creator Rewards; target "
                    "90-120 s)", "lengthen the script (docs/SCRIPT.md), or post it knowing it can't earn"))
    out.append(("<" not in cap and ">" not in cap, "caption filled in (no <...> placeholders left)", "edit post.json"))
    core = re.sub(r"^part\s*\d+\s*[:\-–]\s*", "", first, flags=re.I).lower()
    out.append((core.startswith(("in this town", "in this world", "in this city")),
                "caption line 1 starts with the rule (\"In this town, ...\")", "line 1 is the search hook"))
    caps = [w for w in re.findall(r"[A-Za-z']+", re.sub(r"#\w+", "", cap)) if len(w) >= 3 and w.isupper()
            and w not in ("PART",)]
    out.append((bool(caps), f"a CAPS word in the caption ({', '.join(list(dict.fromkeys(caps))[:3]) or 'none'})",
                "one CAPS word: captions with one had a 121k median vs 23k (Nov 4 scrape)"))
    out.append((len(cap) <= 4000, f"caption length {len(cap)} (TikTok's limit is 4000)", "shorten it"))
    tags = post.get("hashtags", [])
    good = all(t.startswith("#") and " " not in t and "<" not in t for t in tags)
    out.append((3 <= len(tags) <= 6 and good, f"{len(tags)} hashtags", "3-6 tags, each starting with #"))
    out.append((any(t.lower() in ("#inthistown", "#inthisworld") for t in tags), "#inthistown or #inthisworld",
                "add the niche tag"))
    pin = post.get("pinned_comment", "")
    out.append((bool(pin) and "<" not in pin, "pinned comment written", "a question people will answer"))
    out.append((post.get("ai_label") in (True, False), "AI label decided (true or false)",
                "ask the user; Hushers was posted with the label on"))
    if series:
        p, n = int(series.get("part", 1)), int(series.get("parts", 1))
        low = cap.lower()
        if p < n:
            out.append((f"part {p + 1}" in low, f"caption points to Part {p + 1}", f'add "Part {p + 1} is on my page"'))
        if p > 1:
            out.append(("part 1" in low or f"part {p - 1}" in low, f"caption points back to Part {p - 1}",
                        f'add "Part {p - 1} is on my page" for people who land here first'))
    yt = (post.get("yt_title") or core and first) + " #Shorts"
    out.append((len(yt) <= 100, f"YouTube title {len(yt)} characters (limit 100)", "set a shorter yt_title"))
    return out


def write_md(ep, post, series, video, length, rows, made, conf):
    bad = [r for r in rows if not r[0]]
    cap = post.get("caption", "").strip()
    tags = " ".join(post.get("hashtags", []))
    first = cap.splitlines()[0] if cap else ""
    yt_title = (post.get("yt_title") or first)[:91].rstrip() + " #Shorts"
    md = [f"# Post kit: {ep.name}", ""]
    if bad:
        md += ["**Not ready:**", ""] + [f"- {w} -> {fix}" for ok, w, fix in bad] + [""]
    md += ["## File", ""]
    if video:
        md.append(f"`{video.name}` ({length:.1f} s)" if length else f"`{video.name}`")
    if post.get("file", "clean") == "clean":
        md += ["", "Clean file (no music): in TikTok, tap Add sound and pick \"Numbers\" by TEMPOREX."]
    elif conf.get("music"):
        md += ["", "Music file. If the music was cut from another creator's video, TikTok may mute or flag it; post the "
               "clean file and add \"Numbers\" by TEMPOREX from the sound picker instead."]
    md += ["", "## TikTok caption (copy all of it)", "", "```", cap, "", tags, "```", "",
           "## Pinned comment (post it and pin it right away)", "", "```", post.get("pinned_comment", ""), "```", ""]
    if made:
        md += ["## Cover (Edit cover > Upload, or pick the same moment on the timeline)", ""]
        md += [f"- `post/{f.name}`: {why} at {t:.1f} s" for f, why, t in made] + [""]
    md += ["## Settings", "",
           f"- AI-generated label: {'on' if post.get('ai_label') else 'off' if post.get('ai_label') is False else 'decide'}",
           "- Who can watch: everyone; comments, Duet and Stitch: on", ""]
    if series:
        p, n = int(series.get("part", 1)), int(series.get("parts", 1))
        pl = series.get("playlist") or series.get("name", "")
        md += [f"## Series: {series.get('name', '')}, part {p} of {n}", "",
               f"1. Add it to the playlist \"{pl}\" (Profile > Playlists; make it with Part 1)."]
        if p < n:
            md += [f"2. Post Part {p + 1} 3-6 hours after this one (or the next morning), while this one is still "
                   "being pushed.",
                   f"3. When Part {p + 1} is up: reply to the top \"part {p + 1}?\" comment here with a video reply that "
                   f"links Part {p + 1}, and change this video's pinned comment to \"Part {p + 1} is up 👉 on my page\"."]
        if p > 1:
            md += [f"{'4' if p < n else '2'}. On Part {p - 1}: reply to its top \"part {p}?\" comment with a video "
                   f"reply that links this one."]
        md.append("")
    md += ["## YouTube Shorts (same file)", "", "```", yt_title, "```", "", "Description:", "", "```",
           (cap + "\n\n" + tags + "\n\n" + NOT_AFFILIATED), "```", "",
           "## Checks", "", "| | Check |", "|---|---|"]
    md += [f"| {'ok' if ok else 'XX'} | {w}{'' if ok else ' -> ' + fix} |" for ok, w, fix in rows]
    md += ["", "Afterwards: 48 hours after posting, send a screenshot of TikTok Studio's retention graph for this "
           "video, so the steepest drops can be matched to the shots."]
    (ep / "POST.md").write_text("\n".join(md) + "\n")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--video" in sys.argv:
        args = [a for a in args if a != sys.argv[sys.argv.index("--video") + 1]]
    if not args:
        sys.exit(__doc__)
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        sys.exit("needs ffmpeg and ffprobe")
    ep = Path(args[0]).resolve()
    series = json.loads((ep / "series.json").read_text()) if (ep / "series.json").exists() else None
    conf = json.loads((ep / "finish.json").read_text()) if (ep / "finish.json").exists() else {}
    pf = ep / "post.json"
    if not pf.exists():
        pf.write_text(json.dumps(starter(ep, series), indent=1, ensure_ascii=False) + "\n")
        print(f"wrote a starter {pf}: fill in the caption, a CAPS word, the hashtags, the pinned comment and "
              "ai_label (docs/POSTING.md), then run post_kit.py again")
        sys.exit(1)
    post = json.loads(pf.read_text())
    video = find_video(ep, conf, post.get("file", "clean"))
    length = duration(video) if video else None
    times, lines = word_times(ep), script_lines(ep)
    made = covers(ep, video, length, times, lines, conf, post.get("cover_times", [])) if video and length else []
    rows = checks(post, series, length, video)
    write_md(ep, post, series, video, length, rows, made, conf)
    for ok, what, fix in rows:
        print(f"  {'ok' if ok else 'XX'}  {what}" + ("" if ok else f"   -> {fix}"))
    bad = sum(1 for r in rows if not r[0])
    print(f"\n{ep / 'POST.md'}: " + ("ready to post" if not bad else f"{bad} to fix"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
