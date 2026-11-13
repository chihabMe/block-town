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
# Run it in the background if your commands time out. The bake is kept in EPISODE/threejs/ (delete it when done).
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
echo "$(date +%H:%M:%S) bake frames $F0-${F1:-end} at $BT_FPS fps ($MODE, life layer: $BT_LIFE)"
BT_TJ_OUT="$DATA" BT_FRAME_DIR="$DATA/unused" blender -b --factory-startup --python-exit-code 1 \
  -P "$SKILL/blockworld/threejs/bake.py" -- "$EP" render "$F0" ${F1:+"$F1"} > "$DATA/bake.log" 2>&1 \
  || { echo "bake failed: see $DATA/bake.log"; tail -20 "$DATA/bake.log"; exit 1; }
grep -E "^TJ" "$DATA/bake.log" || true
if [ -z "$F1" ]; then
  F1=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['f1'])" "$DATA/anim.json")
fi
# capture.mjs skips frames that already exist. After a fix those are stale, so clear F0..F1 first;
# BT_RESUME=1 keeps them (to finish a run that was stopped part way).
if [ "${BT_RESUME:-0}" != 1 ] && [ -d "$FRAMES" ]; then
  python3 -c "import sys,pathlib; d=pathlib.Path(sys.argv[1]); [p.unlink() for p in d.glob('f_*.jpg') if int(sys.argv[2]) <= int(p.stem[2:]) <= int(sys.argv[3])]" "$FRAMES" "$F0" "$F1"
fi
echo "$(date +%H:%M:%S) draw frames"
TJ_DATA="$DATA" TJ_FRAMES="$FRAMES" node "$SKILL/blockworld/threejs/capture.mjs"
echo "$(date +%H:%M:%S) done: $FRAMES ($(ls "$FRAMES" | grep -c '^f_.*\.jpg$') frames)"
