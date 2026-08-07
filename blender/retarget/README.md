# Motion Retargeting (Auto-Rig Pro)

This is the motion-retargeting step of the Motion Avatar pipeline: it takes an **already-rigged FBX
avatar** (human or animal), a **BVH motion clip** (e.g. produced by the motion-generation stage),
and an **Auto-Rig Pro bone-mapping preset** (`.bmap`), and produces an **animated FBX** with the
motion baked onto the avatar's skeleton.

**Rigging:** seven rigged demo avatars are included in `motion_collection/rigged_model/`. To use
your own avatar, rig the generated mesh with Auto-Rig Pro's Smart Rig in the Blender GUI first,
then pass the rigged FBX to this script.

## Installation

1. Install [Blender 4.0](https://www.blender.org/download/).
2. Purchase and install the [Auto-Rig Pro](https://blendermarket.com/products/auto-rig-pro) addon
   (**paid, required** — the script calls its `arp.*` operators), and
   enable it in Blender's addon preferences.

The script runs inside Blender's bundled Python and uses the standard library plus `bpy`.

## Data preparation

Expected layout (as shipped in this directory):

```
retarget/
├── retarget.py
└── motion_collection/
    ├── match_map/           # Auto-Rig Pro bone-mapping presets (.bmap), authored for this project
    │   ├── human.bmap       # used with -human
    │   ├── anaconda.bmap    ┐
    │   ├── bird.bmap        │
    │   ├── coyote.bmap      │ used with -a <name>
    │   ├── horse.bmap       │
    │   ├── Jaguar.bmap      │
    │   └── spider.bmap      ┘
    ├── motion_demo/         # demo BVH motion clips (generated human motions)
    │   ├── box_kick.bvh
    │   ├── run_clockwise.bvh
    │   ├── salsa_dance.bvh
    │   └── street_dance.bvh
    └── rigged_model/        # rigged demo avatars, ready to retarget
        ├── miqilin.fbx      # human
        ├── anaconda.fbx
        ├── bird.fbx
        ├── coyote.fbx
        ├── horse.fbx
        ├── Jaguar.fbx
        └── spider.fbx
```

The `.bmap` presets are loaded automatically relative to `retarget.py`'s own location, so you can
run Blender from any working directory.

For animals, provide a **BVH motion clip whose skeleton matches the corresponding `.bmap` preset**.
The presets were authored against [Truebones Zoo](https://truebones.gumroad.com/) skeletons.
Truebones clips are commercially licensed and therefore **not** redistributed here — obtain them
under your own license. The bundled human demo clips are generated motions using an SMPL-style
skeleton that matches `human.bmap`.

## Usage

General form (note the `--` separating Blender's own arguments from the script's):

```
blender -b -P retarget.py -- -fbx <rigged_avatar.fbx> -t <motion.bvh> -s <start_frame> -e <end_frame> -o <output.fbx> [-human | -a <animal>]
```

Human example (uses `match_map/human.bmap`):

```
blender -b -P retarget.py -- -fbx motion_collection/rigged_model/miqilin.fbx -t motion_collection/motion_demo/box_kick.bvh -s 0 -e 200 -o output.fbx -human
```

Animal example (uses `match_map/Jaguar.bmap`; the BVH must be a Truebones Jaguar clip you licensed
yourself):

```
blender -b -P retarget.py -- -fbx motion_collection/rigged_model/Jaguar.fbx -t Jaguar-Attack.bvh -s 0 -e 200 -o output.fbx -a Jaguar
```

Arguments:

| Flag | Long form | Default | Meaning |
|---|---|---|---|
| `-fbx` | `--fbx_name` | `root.fbx` | Rigged avatar FBX (retarget target) |
| `-t` | `--target_motion_name` | *(required)* | BVH motion clip (retarget source) |
| `-s` | `--start_frame` | `0` | First frame to retarget/bake |
| `-e` | `--end_frame` | `200` | Last frame to retarget/bake |
| `-o` | `--output_fbx` | `output.fbx` | Output animated FBX path |
| `-human` | `--is_human` | off | Use the human bone map (`human.bmap`) |
| `-a` | `--animal` | — | Animal bone map to use; one of `anaconda`, `bird`, `coyote`, `horse`, `Jaguar`, `spider` |

Notes:

- Pass exactly one of `-human` or `-a <animal>`, choosing the animal name from the list above
  (each name corresponds to a `.bmap` preset in `match_map/`).

## Acknowledgements & License

- [Auto-Rig Pro](https://blendermarket.com/products/auto-rig-pro) — commercial Blender addon that
  performs the actual retargeting; it is **not** bundled and must be purchased separately.
- [Truebones Zoo](https://truebones.gumroad.com/) — the animal skeletons the `.bmap` presets were
  authored against. Truebones motion data is commercially licensed and not included here.
- `retarget.py` and the `.bmap` presets are original work by the Motion Avatar authors, released
  under this repository's license (see the repository root).
