#!/usr/bin/env bash
# Render an episode's frames with the Three.js renderer (the normal way since ep05).
#   bash SKILL/blockworld/render_threejs.sh EPISODE                 final: every frame -> EPISODE/frames/
#   bash SKILL/blockworld/render_threejs.sh EPISODE F0 F1           only frames F0..F1 (the hook, a re-done shot)
#   bash SKILL/blockworld/render_threejs.sh EPISODE --draft [F0 F1] draft: 540x960, 30 fps -> EPISODE/frames_draft/
# The draft is for review rounds: same shots, life layer and tags, a quarter of the pixels, no 240 fps pass, a lighter
# shadow map and smaller JPEGs. Then `finish.py EPISODE --draft` makes <name>_draft.mp4. The final render (no --draft)
# uses finish.json's "render_fps" and full 1080x1920. Draft and final frames live in different folders.
# Two steps: Blender builds only the places the episode names (a few seconds), poses every frame and records it
# (bake), then Three.js draws the frames in headless Chrome. The bake runs to the end of the episode when F1 is
# omitted, and it writes shots.json, so there is no separate check run.
# BT_LIFE=1 (the default here) adds the life layer (blockworld/life.py); BT_LIFE=0 turns it off.
# Run it in the background if your commands time out. The bake is kept in EPISODE/threejs/ (and threejs_b/ for the
# second half of a split whole-episode render); delete them when done.
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
DRAFT=0
ARGS=()
for a in "$@"; do
  if [ "$a" = "--draft" ]; then DRAFT=1; else ARGS+=("$a"); fi
done
EP="$(cd "${ARGS[0]}" && pwd)"
export BT_LIFE="${BT_LIFE:-1}"
if [ "$DRAFT" = 1 ]; then
  export BT_FPS=30
  export TJ_SCALE="${BT_DRAFT_SCALE:-0.5}"
  export TJ_JPEG="${TJ_JPEG:-85}"
  FRAMES="$EP/frames_draft"
else
  # finish.json "render_fps" (e.g. 240 with "blur": 4 -> a 60 fps video with motion blur); default 30
  export BT_FPS="${BT_FPS:-$(python3 -c "import json,sys,os; p=sys.argv[1]; print(json.load(open(p)).get('render_fps', 30) if os.path.exists(p) else 30)" "$EP/finish.json")}"
  export TJ_SCALE=1
  FRAMES="$EP/frames"
fi
F0="${ARGS[1]:-0}"
F1="${ARGS[2]:-}"
if [ ! -d "$SKILL/blockworld/threejs/node_modules/three" ]; then
  echo "first run: installing three and puppeteer-core in $SKILL/blockworld/threejs"
  (cd "$SKILL/blockworld/threejs" && npm install --no-audit --no-fund)
fi
DATA="$EP/threejs"
mkdir -p "$DATA"
MODE=$([ "$DRAFT" = 1 ] && echo "draft ${TJ_SCALE}x" || echo "final")

bake() {   # bake DATA F0 [F1]: pose and record frames F0..F1 (to the end when F1 is empty)
  local data="$1" a="$2" b="${3:-}"
  mkdir -p "$data"
  BT_TJ_OUT="$data" BT_FRAME_DIR="$data/unused" blender -b --factory-startup --python-exit-code 1 \
    -P "$SKILL/blockworld/threejs/bake.py" -- "$EP" render "$a" ${b:+"$b"} > "$data/bake.log" 2>&1 \
    || { echo "bake failed: see $data/bake.log"; tail -20 "$data/bake.log"; return 1; }
  grep -E "^TJ" "$data/bake.log" || true
}
clear_frames() {   # capture.mjs skips frames that already exist; after a fix they are stale. BT_RESUME=1 keeps them.
  if [ "${BT_RESUME:-0}" != 1 ] && [ -d "$FRAMES" ]; then
    python3 -c "import sys,pathlib; d=pathlib.Path(sys.argv[1]); [p.unlink() for p in d.glob('f_*.jpg') if int(sys.argv[2]) <= int(p.stem[2:]) <= int(sys.argv[3])]" "$FRAMES" "$1" "$2"
  fi
}
draw() {   # draw DATA: Three.js draws every frame of that bake into FRAMES
  TJ_DATA="$1" TJ_FRAMES="$FRAMES" node "$SKILL/blockworld/threejs/capture.mjs"
}
last_of() { python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['f1'])" "$1/anim.json"; }

# Speed: a whole-episode render is split in two. The second half is baked (Blender, CPU) while the first half is
# drawn (Chrome, GPU), so the two steps overlap. The split point comes from shots.json (any frame inside the episode
# works). Off by default: on a 12-core laptop Blender and the JPEG threads fight for the CPU (311 s vs 316 s on
# the 10 s test), so BT_SPLIT=1 turns it on for machines with spare cores.
MID=""
if [ -z "$F1" ] && [ "${BT_SPLIT:-0}" = 1 ] && [ -f "$EP/shots.json" ]; then
  MID=$(python3 -c "import json,sys; s=json.load(open(sys.argv[1])); end=s[-1]['start']*int(sys.argv[2]); m=int(end*0.45); print(m if m-int(sys.argv[3])>=120 else '')" "$EP/shots.json" "$BT_FPS" "$F0")
fi

if [ -n "$MID" ]; then
  DATA2="$EP/threejs_b"
  echo "$(date +%H:%M:%S) bake frames $F0-$((MID-1)) at $BT_FPS fps ($MODE, life layer: $BT_LIFE)"
  bake "$DATA" "$F0" "$((MID-1))"
  echo "$(date +%H:%M:%S) bake frames $MID-end in the background; draw frames $F0-$((MID-1))"
  bake "$DATA2" "$MID" > "$EP/.bake_b.out" 2>&1 &
  BPID=$!
  clear_frames "$F0" "$((MID-1))"
  draw "$DATA"
  wait "$BPID" || { cat "$EP/.bake_b.out"; exit 1; }
  cat "$EP/.bake_b.out"; rm -f "$EP/.bake_b.out"
  F1=$(last_of "$DATA2")
  echo "$(date +%H:%M:%S) draw frames $MID-$F1"
  clear_frames "$MID" "$F1"
  draw "$DATA2"
else
  echo "$(date +%H:%M:%S) bake frames $F0-${F1:-end} at $BT_FPS fps ($MODE, life layer: $BT_LIFE)"
  bake "$DATA" "$F0" "$F1"
  [ -z "$F1" ] && F1=$(last_of "$DATA")
  clear_frames "$F0" "$F1"
  echo "$(date +%H:%M:%S) draw frames"
  draw "$DATA"
fi
echo "$(date +%H:%M:%S) done: $FRAMES ($(ls "$FRAMES" | grep -c '^f_.*\.jpg$') frames)"
