# Blender Stage — Retargeting & Rendering

This directory contains the Blender-based post-processing stage of the Motion Avatar pipeline
([arXiv 2405.11286](https://arxiv.org/abs/2405.11286)). After an avatar mesh has been generated
and rigged, and a motion has been generated as BVH, the scripts here (1) retarget the BVH motion
onto the rigged avatar with Auto-Rig Pro and (2) render the resulting animation headlessly.

Both steps run inside Blender's bundled Python (`blender --background --python ...`).

| Subdirectory | Purpose |
|---|---|
| [`retarget/`](retarget/) | Retarget a BVH motion clip onto a rigged FBX avatar (human or animal) using the Auto-Rig Pro addon; exports an animated FBX. |
| [`render/`](render/) | Headless Cycles rendering: animated FBX → MP4 video (`render_fbx.py`), or render an existing `.blend` scene (`blend.py`). |

See each subdirectory's README for installation, data layout, and exact commands.

**Rigging:** rig the generated avatar mesh with Auto-Rig Pro's Smart Rig in the Blender GUI
before retargeting.
