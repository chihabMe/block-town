"""Captions and sound for one episode.

    python3 blockworld/finish.py EPISODE_DIR --captions
    python3 blockworld/finish.py EPISODE_DIR
    python3 blockworld/finish.py EPISODE_DIR --music ~/Music/numbers.mp3     (same as "music" in finish.json)

--captions writes captions.ass and prints each sound cue. It does not encode.
The full command needs frames/f_####.jpg and vo/voice.wav, and writes EPISODE_DIR/<folder-name>.mp4.

cues.json entries, times in seconds:
    {"sfx": "pop.mp3", "word": 4, "volume": 0.55}
    {"sfx": "whoosh-short.mp3", "shot": "liar", "offset": -0.1, "volume": 0.25}
word is the 0-based script word (its spoken start, from vo/times.json).

finish.json (optional) picks the caption style:
    {"captions": "word"}       one big yellow word at a time (default, the block look)
    {"captions": "karaoke"}    groups of up to 3 white words, the word being spoken turns yellow (the Roblox look)
    "music": "/path/song.mp3"  a music bed under the whole video, looped, faded out at the end. The kit has no music
                               in it: use a file you have the right to use. With music, two files are written:
                               <name>.mp4 (no music: post it and add the song from TikTok's sound picker) and
                               <name>_music.mp4 (music mixed in, like the top creators do; their videos can be muted
                               or claimed for it).
    "music_db": -4             music loudness against the voice (the top "Numbers" videos measure -3 to -4 dB)
    "music_start": 0           seconds into the song to start from
    "music_loop": 20.5         loop only this many seconds of the song (from music_start). The top "Numbers" videos
                               loop the song's first 20.5 s, its instrumental intro, for the whole video
shot is a name from shots.json. offset is added to that time. volume is linear, voice stays at 1.0.
"""
import json, re, subprocess, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SFX = SKILL / "sfx"
FONTS = Path(__file__).resolve().parent / "fonts"


def ts(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def esc(path):
    return str(path).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def load(ep):
    script = (ep / "script.txt").read_text().split()
    times = json.loads((ep / "vo" / "times.json").read_text())
    if len(times) != len(script):
        sys.exit(f"times.json has {len(times)} words, script.txt has {len(script)}. Run words.py again.")
    shots = {s["name"]: s["start"] for s in json.loads((ep / "shots.json").read_text())}
    cues = json.loads((ep / "cues.json").read_text()) if (ep / "cues.json").exists() else []
    return script, [w["t0"] for w in times], [w["t1"] for w in times], shots, cues


def write_captions(ep, script, start, stop):
    ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Cap,Inter Display Black,112,&H003BE2FF,&H003BE2FF,&H00000000,&H99000000,1,0,0,0,100,100,0,0,1,11,5,5,60,60,0,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for i, word in enumerate(script):
        a = start[i] - 0.03
        if i + 1 < len(script) and start[i + 1] - start[i] < 0.9:
            b = start[i + 1] - 0.03
        else:
            b = min(stop[i], start[i] + 0.6) + 0.25
        clean = re.sub(r"[^\w']", "", word)
        ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\pos(540,1267)\\fscx82\\fscy82\\t(0,70,\\fscx108\\fscy108)\\t(70,130,\\fscx100\\fscy100)}}{clean}")
    path = ep / "captions.ass"
    path.write_text("\n".join(ass) + "\n")
    return path


def write_karaoke(ep, script, start, stop):
    """Groups of up to 3 words (a group also ends at . , ! ? : ;). The spoken word is yellow, the rest white."""
    ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Kar,Inter Display Black,88,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,1,0,0,0,100,100,0,0,1,9,4,5,60,60,0,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    groups, cur = [], []
    for i, word in enumerate(script):
        cur.append(i)
        if len(cur) == 3 or re.search(r"[.,!?:;]$", word) or i == len(script) - 1:
            groups.append(cur)
            cur = []
    clean = [re.sub(r"[^\w'$%-]", "", w) for w in script]
    for g, idx in enumerate(groups):
        g0 = start[idx[0]] - 0.03
        nxt = groups[g + 1][0] if g + 1 < len(groups) else None
        if nxt is not None and start[nxt] - stop[idx[-1]] < 0.9:
            g1 = start[nxt] - 0.03
        else:
            g1 = stop[idx[-1]] + 0.3
        for k, i in enumerate(idx):
            a = g0 if k == 0 else start[i] - 0.03
            b = start[idx[k + 1]] - 0.03 if k + 1 < len(idx) else g1
            words = " ".join(("{\\c&H003BE2FF&}" + clean[j] + "{\\c&H00FFFFFF&}") if j == i else clean[j] for j in idx)
            pop = "\\fscx90\\fscy90\\t(0,80,\\fscx100\\fscy100)" if k == 0 else ""
            ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Kar,,0,0,0,,{{\\pos(540,1267){pop}}}{words}")
    path = ep / "captions.ass"
    path.write_text("\n".join(ass) + "\n")
    return path


def cue_time(cue, start, shots):
    if "word" in cue:
        t = start[cue["word"]]
    elif "shot" in cue:
        t = shots[cue["shot"]]
    else:
        raise SystemExit(f"cue needs word or shot: {cue}")
    return t + float(cue.get("offset", 0))


def mean_db(path, seconds=60):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-t", str(seconds), "-i", str(path), "-af", "volumedetect",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"mean_volume: (-?[\d.]+) dB", out)
    if not m:
        sys.exit(f"could not measure the loudness of {path}")
    return float(m.group(1))


def encode(ep, out, ass, voice, resolved, music=None):
    frames = ep / "frames" / "f_%04d.jpg"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", str(frames), "-i", str(voice)]
    filters, extra = [], []
    for i, (src, t, vol) in enumerate(resolved):
        cmd += ["-i", str(src)]
        ms = max(0, int(t * 1000))
        filters.append(f"[{i + 2}]adelay={ms}|{ms},volume={vol}[s{i}]")
        extra.append(f"[s{i}]")
    if music:
        path, gain_db, start, length, loop = music
        cmd += ["-stream_loop", "-1", "-ss", str(start), "-i", str(path)]
        k = len(resolved) + 2
        looped = (f"aresample=48000,atrim=0:{loop:.3f},asetpts=N/SR/TB,aloop=loop=-1:size={int(loop * 48000)},"
                  if loop else "")
        filters.append(f"[{k}]{looped}atrim=0:{length:.3f},volume={gain_db:.2f}dB,"
                       f"afade=t=out:st={max(0.0, length - 0.6):.3f}:d=0.6[m]")
        extra.append("[m]")
    mix = "[1]apad,volume=1.0[v];" + "".join(f + ";" for f in filters) + "[v]" + "".join(extra) + \
          f"amix=inputs={len(extra) + 1}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"
    cmd += ["-filter_complex", f"[0]ass={esc(ass)}:fontsdir={esc(FONTS)}[vid];" + mix,
            "-map", "[vid]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-shortest", str(out)]
    subprocess.run(cmd, check=True)
    print("wrote", out)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ep = Path(sys.argv[1]).resolve()
    captions_only = "--captions" in sys.argv
    script, start, stop, shots, cues = load(ep)
    conf = json.loads((ep / "finish.json").read_text()) if (ep / "finish.json").exists() else {}
    style = conf.get("captions", "word")
    if style not in ("word", "karaoke"):
        sys.exit(f"finish.json captions must be 'word' or 'karaoke', not {style!r}")
    ass = (write_karaoke if style == "karaoke" else write_captions)(ep, script, start, stop)
    resolved = []
    for cue in cues:
        t = cue_time(cue, start, shots)
        src = SFX / cue["sfx"]
        if not src.exists():
            sys.exit(f"missing sound effect {src.name} (looked in {SFX})")
        resolved.append((src, t, float(cue["volume"])))
        print(f"  {t:6.2f}s  {cue['volume']:4.2f}  {cue['sfx']}")
    print("wrote", ass, "|", len(script), "caption words,", len(resolved), "sound cues")
    if captions_only:
        return
    voice = ep / "vo" / "voice.wav"
    if not (ep / "frames" / "f_0000.jpg").exists():
        sys.exit(f"no frames in {ep / 'frames'}. Render first, or use --captions.")
    if not voice.exists():
        sys.exit(f"no narration at {voice}")
    encode(ep, ep / f"{ep.name}.mp4", ass, voice, resolved)
    if "--music" in sys.argv:
        conf["music"] = sys.argv[sys.argv.index("--music") + 1]
    if conf.get("music"):
        song = Path(conf["music"]).expanduser()
        song = song if song.is_absolute() else ep / song
        if not song.exists():
            sys.exit(f"music file not found: {song}")
        start = float(conf.get("music_start", 0))
        length = len(list((ep / "frames").glob("f_*.jpg"))) / 30
        gain = mean_db(voice) + float(conf.get("music_db", -4)) - mean_db(song)
        print(f"music: {song.name}, {gain:+.1f} dB to sit {conf.get('music_db', -4)} dB under the voice")
        encode(ep, ep / f"{ep.name}_music.mp4", ass, voice, resolved,
               (song, gain, start, length, float(conf.get("music_loop", 0))))


if __name__ == "__main__":
    main()
