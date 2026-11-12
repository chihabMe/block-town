#!/usr/bin/env bash
# Render every missing final frame of an episode, restarting Blender if it stops (out of memory, another job,
# a tool time limit). Safe to run again at any time: finished frames are never redone.
#   bash SKILL/blockworld/render_all.sh EPISODE [MAX_TRIES]
# Agents whose commands time out after a few minutes: start it in the background and check frames/ for progress.
set -u
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
EP="$(cd "$1" && pwd)"
TRIES="${2:-50}"
total() { python3 -c "import json,math,sys; s=json.load(open(sys.argv[1])); print(math.ceil(s[-1]['start']*30))" "$EP/shots.json"; }
[ -f "$EP/shots.json" ] || blender -b --factory-startup --python-exit-code 1 -P "$SKILL/blockworld/run.py" -- "$EP" check >/dev/null
N=$(total)
for i in $(seq 1 "$TRIES"); do
  have=$(ls "$EP/frames" 2>/dev/null | grep -c '^f_.*\.jpg$')
  echo "$(date +%H:%M:%S) frames $have of $N"
  [ "$have" -ge "$N" ] && { echo "all $N frames rendered"; exit 0; }
  blender -b --factory-startup --python-exit-code 1 -P "$SKILL/blockworld/run.py" -- "$EP" resume > "$EP/render.log" 2>&1
  sleep 2
done
echo "stopped after $TRIES tries; see $EP/render.log"; exit 1
