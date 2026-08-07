import os
import os.path as osp
from Motion import BVH
import numpy as np
import torch
from Motion.transforms import quat2repr6d
from glob import glob
import sys


def fullyConvery(in_dir):
    """
    This function converts a standard bvh file (except Mixamo bvh which has weird joints number) to a 6d rotation file using SinMDM method.
    (frame,joints,feats) -> (frame,joints*feats)
    e.g. HumanML3D: (frame,22,3) -> cat6d -> (frame,22,9) -> flat1d -> (frame,198)
    
    """
    bvh_files = glob(osp.join(in_dir,'*.bvh'))
    for idx, in_file in enumerate(bvh_files):
        anim, joint_names, frametime = BVH.load(in_file)
        print(f'This pose shape is',anim.positions.shape)
        repr_6d = quat2repr6d(torch.tensor(anim.rotations.qs))
        motion = np.concatenate([anim.positions, repr_6d], axis=2) # 100, 69, 9
        n_frames, n_joints, n_feats = motion.shape
        print(f"9d shape is",motion.shape)
        final = motion.reshape(n_frames,-1) # 100,621
        print(f'flat shape is',final.shape)
        save_path = os.path.splitext(in_file)[0] + '.npy'
        np.save(save_path, final)
        print(f"Motion data saved to {save_path}")

if __name__ == "__main__":
    fullyConvery(sys.argv[1])