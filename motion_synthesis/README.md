# Animal Motion Synthesis (SinMDM fork)

This directory contains the **animal motion data-synthesis pipeline** of
[Motion Avatar](https://steve-zeyu-zhang.github.io/MotionAvatar/) (BMVC 2024).
It is a fork of [SinMDM](https://github.com/SinMDM/SinMDM) (Single Motion
Diffusion) adapted to arbitrary animal skeletons: for each of the 878 motion
clips of the 65 Truebones Zoo animals, one single-motion diffusion model is
trained (`--dataset bvh_general`), and the trained models are then used to
synthesize augmented motions via unconditional sampling, in-betweening, and
expansion. The augmented BVH motions are converted to `.npy` feature arrays
that feed the downstream text-to-motion (MoMask-based) training of Motion
Avatar.

You can generate the animal motion data you want yourself (train per-motion
models on your source clips and augment them via sampling and editing), or
bring your own animal motion data, then convert and align it for downstream
training with the conversion chain used by ZooGen: `utils/fbx2bvh.py` (FBX → BVH) →
`bvh2npy.py` / `bvh2vec.py` (BVH → per-joint feature arrays) →
`mean_std.py` (dataset Mean/Std and evaluator meta). Alternatively, the
ready-made **Zoo-300K** text–motion dataset is released at
<https://huggingface.co/SteveZeyuZhang/Zoo-300K>. See *Data preparation*
below for details.

The Truebones Zoo and Mixamo motion data are commercially licensed and cannot
be redistributed here — see *Data preparation* for how to obtain them. Train
the per-motion diffusion checkpoints (65 animals × ~13 motions each) with the
commands under *Usage*.

## Installation

Tested on Ubuntu 18.04, Python 3.8, PyTorch 1.13 + CUDA 11.7 (the
`environment.yml` pins Linux conda builds):

```
conda env create -f environment.yml
conda activate SinMDM
```

`utils/fbx2bvh.py` additionally requires [Blender](https://www.blender.org/)
(it runs inside Blender's bundled Python via `bpy`).

## Data preparation

The pipeline consumes BVH files named `Animal-Action.bvh` (e.g.
`Jaguar-Attack.bvh`) — the animal name before the first `-` and the action name
after it determine the checkpoint layout `<save_dir>/<Animal>/<Action>/`.

**Option A — download the preprocessed Truebones Zoo BVH set** (hosted by the
upstream SinMDM authors):

```
mkdir -p dataset
bash prepare/download_truebones_zoo_dataset.sh
```

**Option B — convert your own Truebones FBX files.** The
[Truebones Zoo](https://truebones.gumroad.com/) dataset is commercial; obtain
it from Truebones, then edit the `in_dir` path at the top of
`utils/fbx2bvh.py` and run it inside Blender:

```
blender -b -P utils/fbx2bvh.py
```

The converted files are written to `<in_dir>/fbx2bvh/`.

Reference metadata shipped in this repo:

- `output.csv` — manifest of the 878 filtered motions (Animal, Motion Name,
  file name) across the 65 animals.
- `docs/animal_groups.md` — how the 65 animals were partitioned into 15
  parallel training groups for the paper's HPC runs.

## Usage

### 1. Batch training (one model per motion)

`sequential_training.py` walks a BVH directory recursively and launches one
SinMDM training run per `.bvh` file:

```
python sequential_training.py --base_dir dataset/zoo --save_dir ckpt_samples --num_steps 60000 --device 0
```

or via the shell wrapper (`-b` motion folder, `-s` save dir, `-n` steps,
`-d` CUDA device):

```
bash sequential_training.sh -b dataset/zoo -s ckpt_samples -n 60000 -d 0
```

Checkpoints are saved to `<save_dir>/<Animal>/<Action>/model000059999.pt`.

To train a single motion directly:

```
python -m train.train_sinmdm --arch unet --dataset bvh_general --save_dir <save_dir> --sin_path <Animal-Action.bvh> --lr_method ExponentialLR --lr_gamma 0.99998 --use_scale_shift_norm --use_checkpoint --num_steps 60000
```

### 2. Motion synthesis

Unconditional variations of the trained motion (the training `sin_path` and
dataset are restored from the checkpoint's `args.json`):

```
python -m sample.generate --model_path ckpt_samples/Jaguar/Attack/model000059999.pt --num_samples 5
```

Motion editing — in-betweening and expansion (`--edit_mode` also supports
`upper_body`, `lower_body`, `harmonization` from upstream):

```
python -m sample.edit --model_path ckpt_samples/Jaguar/Attack/model000059999.pt --edit_mode in_betweening --prefix_end 0.25 --suffix_start 0.75
python -m sample.edit --model_path ckpt_samples/Jaguar/Attack/model000059999.pt --edit_mode expansion --prefix_length 0.15 --suffix_length 0.15
```

For in-betweening toward a *different* reference motion, pass `--ref_motion
<other.bvh>` (the prefix/suffix are then taken from the reference motion).
The reference clip must use the same skeleton and match the training motion's
frame count (crop with `--num_frames` if needed).
Edited results are written next to the checkpoint under
`<ckpt_dir>/<edit_mode>/edit_*/`, including `.bvh` exports saved with `zyx`
rotation order so the channel order comes out X,Y,Z for retargeting.

### 3. BVH → npy conversion

Convert a folder of `.bvh` files (input or generated) to `.npy` arrays saved
next to each file:

```
python bvh2npy.py <bvh_folder>          # raw local joint positions (frames, joints, 3)
python bvh2npy_animate.py <bvh_folder>  # FK world-space positions (frames, joints, 3)
python bvh2vec.py <bvh_folder>          # per-joint [pos(3) + 6d rot(6)] -> (frames, joints*9)
python bvh2vec_animate.py <bvh_folder>  # same, with FK global positions
python check_empty_npy.py <npy_folder>  # flag converted files containing NaN
```

### 4. Dataset statistics for downstream training

After processing the converted motions into a HumanML3D-style dataset layout
(`./dataset/<name>/new_joint_vecs/` and `./dataset/<name>/new_joints/`, done in
the Motion Avatar text-to-motion component), build the Mean/Std files and the
T2M-evaluator directory skeleton:

```
python mean_std.py <dataset_name>
```

This writes `./dataset/<name>/{Mean,Std}.npy` and
`./checkpoints/<name>/Comp_v6_KLD005/{opt.txt, meta/mean.npy, meta/std.npy}`
(using the `assets/opt.txt` template).

### Utilities

- `clear_extra_folder.py` — helper functions to prune checkpoint folders down
  to the final `model/opt 000059999.pt` + `args.json` and to replace spaces in
  file/folder names (edit the example paths at the bottom before use).
- `prepare/` — download scripts for the upstream SinMDM datasets, pretrained
  models, and T2M evaluators.

## Acknowledgements & License

This component is a fork of
[SinMDM: Single Motion Diffusion](https://github.com/SinMDM/SinMDM)
(Raab et al.), released under the MIT License — see the [LICENSE](LICENSE)
file, which is inherited from upstream. `diffusion/` derives from
[openai/guided-diffusion](https://github.com/openai/guided-diffusion),
`Motion/` from the Holden et al. / Ganimator BVH stack, and
`utils/fbx2bvh.py` is a variation of the
[cvpr2018nkn](https://github.com/rubenvillegas/cvpr2018nkn) converter.
The Truebones Zoo motion data is a commercial product of
[Truebones Motions](https://truebones.gumroad.com/) and is subject to its own
license terms.
