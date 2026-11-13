#!/usr/bin/env bash
# Render an episode's final frames with the Three.js renderer (the normal way since ep05).
#   bash SKILL/blockworld/render_threejs.sh EPISODE            every frame -> EPISODE/frames/
#   bash SKILL/blockworld/render_threejs.sh EPISODE F0 F1      only frames F0..F1 (the hook, a re-done shot)
# Two steps: Blender poses every frame from the episode code and records it (bake, ~0.1 s a frame plus ~1 min to build
# the town), then Three.js draws the frames in headless Chrome (~0.1-0.15 s a frame). A 66 s episode takes ~10 min.
# BT_LIFE=1 (the default here) adds the life layer (blockworld/life.py); BT_LIFE=0 turns it off.
# Run it in the background if your commands time out. The bake is kept in EPISODE/threejs/ (delete it when done).
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
EP="$(cd "$1" && pwd)"
export BT_LIFE="${BT_LIFE:-1}"
# finish.json "render_fps" (e.g. 240 with "blur": 4 -> a 60 fps video with motion blur); default 30
export BT_FPS="${BT_FPS:-$(python3 -c "import json,sys,os; p=sys.argv[1]; print(json.load(open(p)).get('render_fps', 30) if os.path.exists(p) else 30)" "$EP/finish.json")}"
if [ ! -f "$EP/shots.json" ]; then
  blender -b --factory-startup --python-exit-code 1 -P "$SKILL/blockworld/run.py" -- "$EP" check >/dev/null
fi
LAST=$(python3 -c "import json,math,sys; s=json.load(open(sys.argv[1])); print(math.ceil(s[-1]['start']*int(sys.argv[2]))-1)" "$EP/shots.json" "$BT_FPS")
F0="${2:-0}"
F1="${3:-$LAST}"
if [ ! -d "$SKILL/blockworld/threejs/node_modules/three" ]; then
  echo "first run: installing three and puppeteer-core in $SKILL/blockworld/threejs"
  (cd "$SKILL/blockworld/threejs" && npm install --no-audit --no-fund)
fi
DATA="$EP/threejs"
mkdir -p "$DATA"
echo "$(date +%H:%M:%S) bake frames $F0-$F1 at $BT_FPS fps (life layer: $BT_LIFE)"
BT_TJ_OUT="$DATA" BT_FRAME_DIR="$DATA/unused" blender -b --factory-startup --python-exit-code 1 \
  -P "$SKILL/blockworld/threejs/bake.py" -- "$EP" render "$F0" "$F1" > "$DATA/bake.log" 2>&1 \
  || { echo "bake failed: see $DATA/bake.log"; tail -20 "$DATA/bake.log"; exit 1; }
grep -E "^TJ" "$DATA/bake.log" || true
echo "$(date +%H:%M:%S) draw frames"
TJ_DATA="$DATA" TJ_FRAMES="$EP/frames" node "$SKILL/blockworld/threejs/capture.mjs"
echo "$(date +%H:%M:%S) done: $EP/frames ($(ls "$EP/frames" | grep -c '^f_.*\.jpg$') frames)"
