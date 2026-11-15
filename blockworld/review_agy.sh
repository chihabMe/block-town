#!/usr/bin/env bash
# Video quality review by agy (Antigravity / Gemini): it watches the video and lists problems. Use it for every test
# reel, draft and final instead of pulling frames by hand (the user's rule, Nov 2026: it saves Claude tokens).
#   bash blockworld/review_agy.sh VIDEO.mp4 BRIEF.txt [OUT.md]
# BRIEF.txt says what the video is for and what each shot should show, with timestamps. The review goes to OUT.md
# (default: next to the video, <name>.review.md). agy may only read the video; it must not run commands or edit files.
set -euo pipefail
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 VIDEO.mp4 BRIEF.txt [OUT.md]" >&2
  exit 2
fi
AGY_BIN="$(command -v "${AGY_BIN:-agy}")"
VIDEO="$(realpath "$1")"
BRIEF="$(cat "$2")"
OUT="$(realpath -m "${3:-${VIDEO%.*}.review.md}")"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO" 2>/dev/null | cut -d. -f1)
size=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "$VIDEO" 2>/dev/null)
PROMPT="You are reviewing a video for a small animation team. Do NOT run any shell/terminal commands and do NOT create or edit any files; only open the video with your file-reading tool and reply in text.

VIDEO: $VIDEO (${dur} seconds, ${size}).

CONTEXT: we make TikTok story videos in a Roblox-style blocky 3D town (classic blocky characters with no elbows or knees, rendered with Three.js).

$BRIEF

YOUR JOB: watch it carefully and list every problem you can see: body parts passing through each other or through the ground, characters floating when they should stand, broken or unreadable poses, a move or shot not showing what it should, bad framing (people cut off, something blocking the view), jitter or popping, unreadable or cut-off text and graphics, anything that would look wrong or cheap to a TikTok viewer. For each problem give the timestamp (m:ss.s), the shot, what exactly is wrong and how bad it is (high / medium / low). Then list what looks good. Be specific and honest; don't invent problems you can't see. End with a short priority table."
REVIEW_TMP="$(mktemp -d)"
trap 'rm -rf "$REVIEW_TMP"' EXIT
cd "$REVIEW_TMP"
timeout 900 "$AGY_BIN" --model "${AGY_MODEL:-gemini-3.8-flash-high}" --sandbox --mode accept-edits --print-timeout 880s \
  -p "$PROMPT" > "$OUT" 2>&1
echo "review: $OUT ($(wc -l < "$OUT") lines)"
