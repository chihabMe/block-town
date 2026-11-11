"""Runs an episode inside Blender.

    blender -b --factory-startup --python-exit-code 1 -P <skill>/blockworld/run.py -- EPISODE_DIR MODE [args]

EPISODE_DIR holds episode.py and script.txt. See anim.py for the modes (check, stills, frame, render, resume).
"""
import runpy, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not args:
    raise SystemExit(__doc__)
episode = Path(args[0]).resolve() / "episode.py"
if not episode.exists():
    raise SystemExit(f"{episode} not found")
runpy.run_path(str(episode), run_name="__main__")
