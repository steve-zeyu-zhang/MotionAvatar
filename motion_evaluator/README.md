# Motion Evaluator Training (T2M fork)

This component trains the **text-motion-matching evaluator** used to compute the quantitative metrics in Motion Avatar (R-precision, FID, MM-Dist, Diversity, MultiModality). It is a fork of [Guo et al.'s text-to-motion codebase (CVPR 2022)](https://github.com/EricGuo5513/text-to-motion), extended so that the movement autoencoder (`train_decomp_v3.py`) and the text/motion co-embedding evaluator (`train_tex_mot_match.py`) can be trained on **arbitrary skeletons** using a 6d-rotation motion representation (3 root-relative positions + 6d rotation = 9 dims per joint). For any `--dataset_name` other than the built-in `t2m` / `kit` / `6d`, the code infers `joints_num` and `dim_pose` directly from the `.npy` files under `./dataset/<name>/{new_joints,new_joint_vecs}/` and reads the kinematic chain from a BVH file in `./dataset/<name>/bvh/` (via the bundled `vis6d/` BVH utilities). This is how the animal-skeleton evaluator for the Zoo-300K metrics in the paper was trained.

## Installation

Create the conda environment (Python 3.7, PyTorch 1.6, CUDA 10.1):

```sh
conda env create -f environment.yaml
conda activate t2m
```

Notes:
- Requires a GPU supported by cudatoolkit 10.1 / PyTorch 1.6 (e.g. Titan X, 2080Ti); A100 and other sm_80+ GPUs are not supported by this toolchain.
- Install from `environment.yaml`; `requirements.txt` targets Python >= 3.8 environments.

### GloVe word vectors

Both training scripts load GloVe vectors through `WordVectorizer('./glove', 'our_vab')`. Place a `glove/` folder (containing `our_vab_data.npy`, `our_vab_idx.pkl`, `our_vab_words.pkl`) in this directory — download it with the script in the motion generation component:

```sh
cd ../motion_generation && bash prepare/download_glove.sh   # then copy/symlink glove/ here
```

or grab it from the upstream [text-to-motion](https://github.com/EricGuo5513/text-to-motion) / [HumanML3D](https://github.com/EricGuo5513/HumanML3D) releases.

## Data preparation

Each dataset lives in `./dataset/<dataset_name>/` with this layout:

```
./dataset/<dataset_name>/
├── new_joint_vecs/   # per-clip motion features, (n_frames, dim_pose) .npy
│                     #   6d representation: dim_pose = joints_num * 9
├── new_joints/       # per-clip joint positions, (n_frames, joints_num, 3) .npy
│                     #   used to infer joints_num for custom datasets
├── texts/            # per-clip text descriptions (.txt, T2M format)
├── bvh/              # >=1 .bvh file of the skeleton — the kinematic chain is
│                     #   read from the first .bvh found (custom datasets only)
├── Mean.npy          # feature mean over the training set
├── Std.npy           # feature std over the training set
├── train.txt         # clip-id list for training
└── val.txt           # clip-id list for validation
```

- For the built-in names, `t2m` maps to `./dataset/HumanML3D` (22 joints, dim_pose 263) and `kit` to `./dataset/KIT-ML` (21 joints, dim_pose 251); download from the [HumanML3D repo](https://github.com/EricGuo5513/HumanML3D). `6d` maps to `./dataset/6d` (22 joints, dim_pose 198). Any other name (e.g. `HumanML3D_6d`, or an animal dataset exported by the SinMDM/retargeting components of this release) uses the auto-inference path described above and additionally needs `new_joints/` and `bvh/`.
- `Mean.npy` / `Std.npy` can be computed with `scripts/cal_mean_variance.py` (edit its `data_dir`/`save_dir` paths at the bottom of the file).
- **Mean/Std for `train_tex_mot_match.py`:** it loads Mean/Std from `checkpoints/<dataset_name>/Comp_v6_KLD005/meta/{Mean.npy,Std.npy}` (`Comp_v6_KLD01` for `t2m`). For a custom dataset, create that folder and copy the dataset's `Mean.npy`/`Std.npy` into it before training stage 2.

## Usage

All checkpoints/logs are written under `./checkpoints/<dataset_name>/<name>/` and `./log/`.

**Stage 1 — train the movement autoencoder** (required by the evaluator):

```sh
python train_decomp_v3.py --name Decomp_SP001_SM001_H512 --gpu_id 0 --window_size 24 --dataset_name HumanML3D_6d
```

Replace `--dataset_name` with `t2m`, `kit`, `6d`, or your custom dataset name. During training it periodically renders reconstruction previews; for custom skeletons the 6d features are converted back through forward kinematics using the dataset's BVH.

**Stage 2 — train the text-motion matching evaluator** (this is the checkpoint the metrics use):

```sh
python train_tex_mot_match.py --name text_mot_match --gpu_id 0 --batch_size 8 --dataset_name HumanML3D_6d
```

It loads the stage-1 checkpoint from `checkpoints/<dataset_name>/Decomp_SP001_SM001_H512/model/latest.tar` (path configurable via `--decomp_name`) and produces `checkpoints/<dataset_name>/text_mot_match/model/finest.tar`, which `networks/evaluator_wrapper.py` wraps for metric computation. For custom datasets (e.g. the animal evaluator), metrics are computed from the motion generation component using this checkpoint. `train_tex.sh` contains this command as a runnable example.

## Acknowledgements & License

This component is a fork of [EricGuo5513/text-to-motion](https://github.com/EricGuo5513/text-to-motion) (Guo et al., *"Generating Diverse and Natural 3D Human Motions from Text"*, CVPR 2022), released under the MIT license — see [LICENSE](LICENSE) (Copyright 2022 Chuan Guo), which this fork retains. The `vis6d/` BVH/animation utilities derive from [Daniel Holden's motion library](https://theorangeduck.com) and [PeizhuoLi/ganimator](https://github.com/PeizhuoLi/ganimator) (attribution headers kept in-file), the same lineage as [SinMDM](https://github.com/SinMDM/SinMDM)'s motion utils; `utils/plot_script_sinmdm.py` follows SinMDM's arbitrary-skeleton renderer.
