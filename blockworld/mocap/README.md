# Motion-capture clip provenance

These pose JSON files identify CMU Graphics Lab motion-capture clips by subject and motion ID.
`source` in each file records the input BVH filename. `../mocap_convert.py` converts BVH joint
motion into the kit's simplified shoulder, hip, waist and head poses; these are not original BVH files.
The exact BVH distribution/version used for the existing conversions was not recorded.

| Local clip | Recorded BVH source |
|---|---|
| `chicken_dance_cmu18_15.json` | `18_15.bvh` |
| `dances_cmu15_04.json` | `15_04.bvh` |
| `jump_cmu13_39.json` | `13_39.bvh` |
| `punch_cmu02_05.json` | `02_05.bvh` |
| `run_cmu09_02.json` | `09_02.bvh` |
| `scared_cmu142_16.json` | `142_16.bvh` |
| `walk_cmu07_01.json` | `07_01.bvh` |
| `wave_cmu141_16.json` | `141_16.bvh` |

Original database: http://mocap.cs.cmu.edu/ (funded by NSF EIA-0196217).
BVH conversion reference: [Bruce Hahne / cgspeed](https://sites.google.com/a/cgspeed.com/cgspeed/motion-capture/the-motionbuilder-friendly-bvh-conversion-release-of-cmus-motion-capture-database).
The cgspeed release page states that its BVH files are free to use worldwide for any purpose.
CMU's data terms allow use in products, but prohibit selling the motion data itself, including converted
versions. Retain the source attribution and upstream terms when redistributing clips; do not treat these
files as newly authored, exclusively owned motion data or sell them as a standalone motion library.
