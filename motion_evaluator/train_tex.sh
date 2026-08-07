#!/bin/bash
# Example: train the text-motion matching evaluator on the HumanML3D_6d dataset
# (HumanML3D re-represented as 3D root-relative positions + 6d rotations, 9 dims/joint).
#
# The dataset is expected under ./dataset/<dataset_name>/ — if it lives elsewhere
# (e.g. on fast local storage), symlink it into place first:
#
#   ln -s /path/to/HumanML3D_6d ./dataset/HumanML3D_6d
#
# Prerequisites (see README.md):
#   1. glove/ word vectors in the repo root
#   2. Stage-1 decomp checkpoint: checkpoints/HumanML3D_6d/Decomp_SP001_SM001_H512/model/latest.tar
#      (train it with train_decomp_v3.py)
#   3. Mean/Std at checkpoints/HumanML3D_6d/Comp_v6_KLD005/meta/{Mean.npy,Std.npy}

python train_tex_mot_match.py --name text_mot_match --gpu_id 0 --batch_size 8 --dataset_name HumanML3D_6d
