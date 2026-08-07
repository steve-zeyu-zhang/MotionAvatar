# Headless Rendering

This is the final rendering step of the Motion Avatar pipeline: it turns the retargeted, animated
avatars into videos. Two independent, self-contained `bpy` scripts are provided:

- **`render_fbx.py`** — imports an animated `.fbx` (e.g. the output of the retargeting step),
  builds a simple scene (orthographic camera, sun light, Cycles GPU settings) and renders the
  full animation to `<name>.mp4`. Supports single-file and batch-folder modes.
- **`blend.py`** — opens an existing `.blend` file (e.g. a scene composed in the GUI), forces
  Cycles + CUDA, optionally overrides the frame range, and renders its animation to an MP4.

## Installation

Install a [Blender](https://www.blender.org/download/) **2.9x/3.x** build with Cycles (bundled by
default), following the TEMOS
[Blender setup guide](https://github.com/Mathux/TEMOS?tab=readme-ov-file#rendering-motions-high_brightness)
(which uses Blender 2.93).

Both scripts run inside Blender's bundled Python.

**GPU:** both scripts render with Cycles on CUDA (NVIDIA GPU) and enable all CUDA devices.

## Data preparation

Inputs are either:

- animated `.fbx` files, such as the `output.fbx` produced by [`../retarget/`](../retarget/), or
- `.blend` scene files prepared in the Blender GUI.

## Usage

### Render one FBX to MP4

```bash
YOUR_BLENDER_PATH/blender --background --python render_fbx.py -- --fbx PATH_TO_DATA.fbx --output YOUR_OUTPUT_FOLDER
```

Output: `YOUR_OUTPUT_FOLDER/<name>.mp4` (Cycles GPU, 1920x1080, 128 samples, 20 fps, H.264).
If `--output` is omitted, files go to `./render_output`.

### Batch-render every FBX under a folder

```bash
YOUR_BLENDER_PATH/blender --background --python render_fbx.py -- --folder FOLDER_WITH_FBXS --output YOUR_OUTPUT_FOLDER
```

The folder is searched recursively; each `<name>.fbx` becomes `<name>.mp4`.

### Render a .blend file's animation

```bash
YOUR_BLENDER_PATH/blender --background --python blend.py -- --blend_path SCENE.blend --save_path OUTPUT_PATH [--frame_start N] [--frame_end M]
```

`blend.py` renders exactly one `.blend` file per invocation.
`--frame_start`/`--frame_end` default to the frame range stored in the `.blend` file.

## Acknowledgements & License

- [TEMOS](https://github.com/Mathux/TEMOS) — the headless-Blender rendering workflow and
  installation instructions these scripts follow (no TEMOS code is included here).
- Both scripts are original work by the Motion Avatar authors, released under this repository's
  license (see the repository root).
