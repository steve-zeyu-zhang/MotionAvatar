# Motion Generation (MoMask fork)

This directory contains the motion-generation component of **Motion Avatar: Generate Human and Animal Avatars with Arbitrary Motion** (BMVC 2024). It is a fork of [MoMask](https://github.com/EricGuo5513/momask-codes) (CVPR 2024) and provides the three-stage text-to-motion pipeline used in the paper: (1) an RVQ-VAE motion tokenizer, (2) a masked transformer that maps text to base-layer motion tokens, and (3) a residual transformer that predicts the residual token layers. It also includes evaluation scripts (FID, R-precision, MM-Dist, MPJPE) and inference scripts that turn a text prompt into a motion sequence saved as `.npy`, rendered `.mp4`, and exported `.bvh` (via `visualization/joints2bvh.py`), which the downstream rigging/retargeting stage consumes.

**Human and animal motion:** the same three-stage recipe trains both. The registered dataset configs are HumanML3D (`--dataset_name t2m`, 22 joints) and KIT-ML (`--dataset_name kit`, 21 joints). For animal motion, prepare your data with the conversion chain in `motion_synthesis/` (`bvh2vec.py` → `mean_std.py`, which produces the feature arrays plus the Mean/Std and evaluator meta in the same dataset layout), adjust the dataset config (joint count / feature dimension) to your skeleton, and train with the same commands. For evaluation on animal motion, use the arbitrary-skeleton evaluator trained with `motion_evaluator/`.

## Installation

Tested with Python 3.7.13, PyTorch 1.12.0 (CUDA 11.3), numpy 1.21.5 on Linux.

Option A — conda environment (fully pinned, linux-64, includes ffmpeg for video rendering):

```bash
conda env create -f environment.yml
conda activate momask
```

Option B — pip (canonical dependency list):

```bash
pip install -r requirements.txt
```

Notes:

* Video previews are written with the `mpeg4` codec — open them in a standard desktop video player.

### Pretrained models, evaluators, and GloVe

```bash
bash prepare/download_models.sh     # pretrained HumanML3D + KIT-ML checkpoints
bash prepare/download_evaluator.sh  # T2M evaluator checkpoints
bash prepare/download_glove.sh      # GloVe word vectors (used by the evaluators)
```

## Data preparation

Follow the official [HumanML3D](https://github.com/EricGuo5513/HumanML3D) instructions to build the dataset, then place (or symlink) it at:

```
./dataset/HumanML3D/
    new_joint_vecs/   # 263-dim motion features, one .npy per clip
    new_joints/       # 22-joint xyz positions
    texts/            # text annotations
    Mean.npy
    Std.npy
    train.txt
    val.txt
    test.txt
```

## Usage

All results and checkpoints are written to `./checkpoints/<dataset_name>/<name>/`.

wandb logging is **off by default**. Add `--wandb` to any train/eval command to enable it (requires `wandb login`); add `--team` and set the `WANDB_ENTITY` environment variable to log to a team entity instead of your personal account.

### Training (three stages)

Stage 1 must finish before stages 2 and 3; stages 2 and 3 can then run in parallel (both need `--vq_name` pointing at the stage-1 model).

```bash
# Stage 1: RVQ-VAE motion tokenizer
python train_vq.py --name rvq_bs512 --gpu_id 0 --dataset_name t2m --batch_size 512 \
    --num_quantizers 6 --max_epoch 50 --quantize_dropout_prob 0.2 --gamma 0.05

# Stage 2: masked transformer (text -> base-layer tokens)
python train_t2m_transformer.py --name mtrans_bs64 --gpu_id 0 --dataset_name t2m \
    --batch_size 64 --vq_name rvq_bs512

# Stage 3: residual transformer (residual token layers)
python train_res_transformer.py --name rtrans_bs64 --gpu_id 0 --dataset_name t2m \
    --batch_size 64 --vq_name rvq_bs512 --cond_drop_prob 0.2 --share_weight
```

Key flags: `--dataset_name` (`t2m` = HumanML3D), `--name` (experiment name / checkpoint dir), `--vq_name` (stage-1 model used for tokenization; its `net_best_fid.tar` is loaded), `--batch_size` (512 for RVQ; 64 on HumanML3D for the transformers).

### Evaluation

```bash
# RVQ reconstruction quality (FID, MPJPE, R-precision)
python eval_t2m_vq.py --gpu_id 0 --name rvq_nq6_dc512_nc512_noshare_qdp0.2 \
    --dataset_name t2m --ext rvq_nq6

# Full text-to-motion generation (FID, R-precision, MM-Dist, multimodality)
python eval_t2m_trans_res.py --res_name tres_nlayer8_ld384_ff1024_rvq6ns_cdp0.2_sw \
    --name t2m_nlayer8_nhead6_ld384_ff1024_cdp0.1_rvq6ns --dataset_name t2m \
    --gpu_id 0 --cond_scale 4 --time_steps 10 --ext evaluation
```

`--name` is the masked-transformer experiment, `--res_name` the residual transformer; the model names above match the pretrained checkpoints from `prepare/download_models.sh`. Results are written to `./checkpoints/<dataset_name>/<name>/eval/<ext>.log`.

### Generation (inference)

```bash
# Single prompt (motion length estimated automatically when --motion_length 0)
python gen_t2m.py --gpu_id 0 --ext exp1 \
    --text_prompt "A person is walking on a treadmill." --motion_length 0

# Batch of prompts from a file (one "prompt#length" per line; see assets/text_prompt.txt)
python gen_t2m.py --gpu_id 0 --ext exp2 --text_path assets/text_prompt.txt
```

Outputs go to `./generation/<ext>/`: `joints/` holds `.npy` joint positions, and `animations/` holds `.mp4` previews plus `.bvh` exports (both a raw version and an `_ik` version with foot-contact IK cleanup). By default it loads the pretrained model names above; override with `--name` / `--res_name` for your own runs.

The repository also includes `edit_t2m.py` for temporal inpainting of an existing motion.

## Acknowledgements & License

This component is a fork of [MoMask: Generative Masked Modeling of 3D Human Motions](https://github.com/EricGuo5513/momask-codes) by Chuan Guo et al. (CVPR 2024); the model, data-processing, and evaluation code are theirs. Data formats and evaluators come from [HumanML3D / text-to-motion](https://github.com/EricGuo5513/HumanML3D). Our changes are limited to experiment infrastructure (optional wandb logging, download mirrors, video-codec fix).

Released under the MIT License — see [LICENSE](./LICENSE) (Copyright (c) 2023 Chuan Guo, upstream MoMask). If you use this code, please cite both MoMask and Motion Avatar (arXiv:2405.11286).
