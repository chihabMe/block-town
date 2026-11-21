# Approved human locomotion

The user selected the faster ep18 chase on 2026-11-18 after rejecting running that felt too slow and movement that looked stationary. Use `blockworld/locomotion.py` for new human walking and running shots. Existing episodes keep their original helpers unless explicitly revised.

The approved run travels **7 studs/second**, with a **0.66-second full stride**, 0.18-second support intervals, longer steps, bent elbows, restrained arm pumping and a small flight phase. The grounded walk travels **3 studs/second**, with a 0.90-second stride and overlapping support intervals. Do not independently speed up the leg cycle or manually replace the root position after solving the feet. Cadence, stride distance and actual travel must agree.

Build a motion copy once at episode initialization. It copies the existing cast’s appearance and adds knee, ankle and elbow joints without changing the original cast model. Use the original cast member for other poses, carrying the motion copy only through the shots that need it.

```python
import locomotion as motion
RUN_MAX = motion.make_runner(MAX, 'Max.motion')
RUN_ZOE = motion.make_runner(ZOE, 'Zoe.motion')
RUNNERS = (RUN_MAX, RUN_ZOE)
motion.install_life_filter(RUNNERS)

@before_each_frame
def reset_motion(T):
    for c in RUNNERS:
        c['_locomotion_active'] = False

def chase(t, d, T):
    motion.move(RUN_MAX, (-2.5, 60, ROAD), 0, t, 'run')
    motion.move(RUN_ZOE, (2.3, 62, ROAD), 0, t, 'run', phase=.165)
    # Choose a camera that shows both runners' feet and visible world travel.
    shot((-10, 42-7*t*.88, 5.8), (-.6, 57.8-7*t*.88, 2.6), 54)
    focus(RUN_MAX, RUN_ZOE)
```

`phase` is in seconds and affects the gait while preserving the specified starting position. No extra root offset is needed. Use the actual surface height: `ROAD` for the road, `WALK` for a sidewalk, or the loaded place’s floor. The support foot stays fixed in world space; the other foot swings to its next contact. Generic character squash, idle joint offsets and camera punch are excluded during movement, while scene life and blinking remain active.

Show enough movement against the world. Avoid framing a foreground prop over the legs. Keep captions below visible feet in a movement review; check the full video’s captions as well. Use the episode’s actual cut length and narration to judge pace, rather than judging only a long isolated cycle.

For carrying a prop, solve the gait first, then steady the holding arm and elbow and attach the prop to that hand. The other arm can pump. Verify that the prop does not cover the face. The completed ep18 revision in `episodes/ep18-midnight-lost-found-v2/` demonstrates the grounded walk, carrying run and chase.

Run `check`, inspect native-rendered movement across multiple points in a stride, and measure planted-foot drift and sole clearance before accepting a new use. Straight paths are supported; turning, stairs and collision handling require additional planning. No downloaded models or paid generation are needed.
