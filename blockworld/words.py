"""Word timings: when is each word of script.txt spoken in vo/voice.wav?  ->  EPISODE_DIR/vo/times.json

    python3 words.py EPISODE_DIR                 transcribe vo/voice.wav with whisper, then line the words up
    python3 words.py EPISODE_DIR --json FILE     use an existing whisper.cpp JSON (made with: -ml 1 -sow -oj)

Whisper is found in this order:
  1. whisper.cpp:  $WHISPER_CLI or `whisper-cli` on PATH, with the model at $WHISPER_MODEL
  2. Python package faster-whisper   (pip install faster-whisper)
  3. Python package openai-whisper   (pip install openai-whisper)
What whisper hears never matches the script exactly (numbers, names, "$10"). The script is the truth: every script
word gets a time; words whisper misheard get a time spread between their neighbours and are listed at the end.
"""
import difflib, json, os, re, shutil, subprocess, sys
from pathlib import Path


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))


def from_whisper_cpp_json(path):
    out = []
    for w in json.loads(Path(path).read_text())["transcription"]:
        if w["text"].strip():
            out.append((w["text"].strip(), w["offsets"]["from"] / 1000, w["offsets"]["to"] / 1000))
    return out


def transcribe(wav, work):
    home = Path.home()
    cli = os.environ.get("WHISPER_CLI") or shutil.which("whisper-cli")
    guess = home / ".cache/hyperframes/whisper/whisper.cpp/build/bin/whisper-cli"
    if not cli and guess.exists():
        cli = str(guess)
    if cli:
        model = os.environ.get("WHISPER_MODEL") or str(home / ".cache/hyperframes/whisper/models/ggml-small.en.bin")
        if not Path(model).exists():
            sys.exit(f"whisper model not found at {model}: set WHISPER_MODEL to a ggml model file (ggml-small.en.bin)")
        w16 = work / "v16.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ar", "16000", "-ac", "1", str(w16)], check=True)
        env = dict(os.environ, LD_LIBRARY_PATH=str(Path(cli).parent) + os.pathsep + os.environ.get("LD_LIBRARY_PATH", ""))
        subprocess.run([cli, "-m", model, "-f", str(w16), "-ml", "1", "-sow", "-oj", "-of", str(work / "words"), "-np"],
                       check=True, env=env, stdout=subprocess.DEVNULL)
        return from_whisper_cpp_json(work / "words.json")
    try:
        from faster_whisper import WhisperModel
        segs, _ = WhisperModel("small.en", compute_type="int8").transcribe(str(wav), word_timestamps=True)
        return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    except ImportError:
        pass
    try:
        import whisper
        res = whisper.load_model("small.en").transcribe(str(wav), word_timestamps=True)
        return [(w["word"].strip(), w["start"], w["end"]) for s in res["segments"] for w in s["words"]]
    except ImportError:
        sys.exit("no whisper found: install whisper.cpp (set WHISPER_CLI and WHISPER_MODEL), "
                 "or `pip install faster-whisper`, or `pip install openai-whisper`")


def align(script, heard):
    """script: list of words. heard: list of (text, t0, t1). Returns [(t0, t1, exact)] for every script word."""
    a, b = [norm(w) for w in script], [norm(w) for w, _, _ in heard]
    out = [None] * len(script)
    for tag, i0, i1, j0, j1 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i1 - i0):
                out[i0 + k] = (heard[j0 + k][1], heard[j0 + k][2], True)
        elif tag == "replace":                       # misheard: share the heard time span by word length
            t0, t1 = heard[j0][1], heard[j1 - 1][2]
            lens = [max(len(w), 1) for w in a[i0:i1]]
            acc = 0
            for k, ln in enumerate(lens):
                out[i0 + k] = (t0 + (t1 - t0) * acc / sum(lens), t0 + (t1 - t0) * (acc + ln) / sum(lens), False)
                acc += ln
    end = heard[-1][2] if heard else 0.0
    i = 0
    while i < len(out):                               # words whisper skipped: spread between the neighbours
        if out[i] is None:
            j = i
            while j < len(out) and out[j] is None:
                j += 1
            t0 = out[i - 1][1] if i else 0.0
            t1 = out[j][0] if j < len(out) else end
            for k in range(i, j):
                out[k] = (t0 + (t1 - t0) * (k - i) / (j - i), t0 + (t1 - t0) * (k - i + 1) / (j - i), False)
            i = j
        else:
            i += 1
    fixed, last = [], 0.0
    for t0, t1, ok in out:                            # never go backwards
        t0 = max(t0, last)
        fixed.append((round(t0, 3), round(max(t1, t0), 3), ok))
        last = t0
    return fixed


def unswallow(script, times):
    """Whisper often stretches the word before a pause and squeezes the next word into a few hundredths of a
    second ("after" 1.81-2.60, "eight." 2.60-2.62). Give the long word a normal length and start the squeezed
    word right after it."""
    out = list(times)
    for i in range(1, len(out)):
        (a0, a1, aok), (b0, b1, bok) = out[i - 1], out[i]
        if b1 - b0 < 0.06 and a1 - a0 > 0.5:
            est = 0.12 + 0.06 * len(norm(script[i - 1]))
            nb0 = round(min(a0 + est, b0), 3)
            out[i - 1] = (a0, nb0, aok)
            out[i] = (nb0, round(max(b1, nb0 + 0.12 + 0.06 * len(norm(script[i]))), 3), bok)
            print(f"  re-timed: word {i} {script[i]!r} {b0:.2f} -> {nb0:.2f} s (whisper squeezed it after a pause)")
    return out


def fit_tail(times, wav):
    """Whisper sometimes stretches the last sentence past the end of the speech. If it did, squeeze the words after
    the last pause into the real speech (from the end of that pause to where the sound stops)."""
    import re, subprocess
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", "silencedetect=n=-38dB:d=0.06", "-f", "null",
                          "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    dur = float(re.findall(r"Duration: (\d+):(\d+):([\d.]+)", out)[0][2]) + 60 * float(
        re.findall(r"Duration: (\d+):(\d+):([\d.]+)", out)[0][1])
    speech_end = starts[-1] if starts and (len(ends) < len(starts) or ends[-1] >= dur - 0.05) else dur
    if times[-1][1] <= speech_end + 0.1:
        return times
    gaps = [e for e in ends if e < speech_end - 0.3]
    if not gaps:
        return times
    g = gaps[-1]
    j = min(range(len(times)), key=lambda i: abs(times[i][0] - g))
    a, b = times[j][0], times[-1][1]
    k = (speech_end - g) / (b - a)
    fixed = list(times[:j]) + [(round(g + (t0 - a) * k, 3), round(g + (t1 - a) * k, 3), ok) for t0, t1, ok in times[j:]]
    print(f"  re-timed the last {len(times) - j} words into the speech: they ran to {b:.2f} s, speech ends {speech_end:.2f} s")
    return fixed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ep = Path(sys.argv[1]).resolve()
    script = (ep / "script.txt").read_text().split()
    vo = ep / "vo"
    heard = from_whisper_cpp_json(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--json" else transcribe(vo / "voice.wav", vo)
    times = fit_tail(unswallow(script, align(script, heard)), vo / "voice.wav")
    (vo / "times.json").write_text(json.dumps([{"w": w, "t0": t0, "t1": t1} for w, (t0, t1, _) in zip(script, times)], indent=0))
    loose = [(i, w, t[0]) for i, (w, t) in enumerate(zip(script, times)) if not t[2]]
    print(f"{len(script)} script words, {len(heard)} heard, {len(script) - len(loose)} matched exactly, {len(loose)} placed by guess")
    for i, w, t0 in loose:
        print(f"  guessed: word {i} {w!r} at {t0:.2f} s")
    if len(loose) > len(script) * 0.15:
        print("WARNING: more than 15% of the words were guessed. Listen to the narration: it may not match script.txt.")
    print("wrote", vo / "times.json")
