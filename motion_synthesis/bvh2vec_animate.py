import os
import os.path as osp
from Motion import BVH
import numpy as np
import torch
from Motion.transforms import quat2repr6d
from glob import glob
from Motion.Animation import positions_global as anim_pos
from Motion.Animation import Animation
from Motion.Quaternions import Quaternions
from Motion.transforms import repr6d2quat
import sys


def fullyConvery(in_dir):
    """
    This function converts a standard bvh file (except Mixamo bvh which has weird joints number) to a 6d rotation file using SinMDM method.
    (frame,joints,feats) -> (frame,joints*feats+6)
    e.g. HumanML3D: (frame,22,3) -> cat6d -> (frame,22,9) -> animate -> cat6d -> flat1d -> (frame,198)
    
    """
    bvh_files = glob(osp.join(in_dir,'*.bvh'))
    for idx, in_file in enumerate(bvh_files):
        anim, joint_names, frametime = BVH.load(in_file)
        print(f'This pose shape is',anim.positions.shape)
        repr_6d = quat2repr6d(torch.tensor(anim.rotations.qs))
        motion = np.concatenate([anim.positions, repr_6d], axis=2) 
        quats = repr6d2quat(repr_6d).numpy()
        anim2 = Animation(rotations=Quaternions(quats), positions=motion[:, :, :3],
                                    orients=anim.orients, offsets=anim.offsets, parents=anim.parents)
        motion2 = anim_pos(anim2)# 100, 69,3

        dim_9 = np.concatenate([motion2, repr_6d], axis=2)

        n_frames, n_joints, n_feats = dim_9.shape
        print(f"9d shape is",dim_9.shape)
        final = dim_9.reshape(n_frames,-1) #100,297
        print(f'flat shape is',final.shape)
        save_path = os.path.splitext(in_file)[0] + '.npy'
        np.save(save_path, final)
        print(f"Motion data saved to {save_path}")

if __name__ == "__main__":
    fullyConvery(sys.argv[1])