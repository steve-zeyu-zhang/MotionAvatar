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
    This function converts a standard bvh file (except Mixamo bvh which has weird joints number) to standard npy pose file.
    (frame,joints,feats) -> cat 6d -> (frame,joints,feats+9) -> animation ->  (frame,joints,feats)
    e.g. HumanML3D: (frame,22,3) -> (frame,22,9) -> (frame,22,3)
    
    """
    bvh_files = glob(osp.join(in_dir,'*.bvh'))
    for idx, in_file in enumerate(bvh_files):
        anim, joint_names, frametime = BVH.load(in_file)
        print(f'This pose shape is',anim.positions.shape)
        repr_6d = quat2repr6d(torch.tensor(anim.rotations.qs))
        motion = np.concatenate([anim.positions, repr_6d], axis=2) # 100,69,9
        quats = repr6d2quat(repr_6d).numpy()
        anim = Animation(rotations=Quaternions(quats), positions=motion[:, :, :3],
                                    orients=anim.orients, offsets=anim.offsets, parents=anim.parents)
        final = anim_pos(anim) # 100, 69, 3
        save_path = os.path.splitext(in_file)[0] + '.npy'
        np.save(save_path, final)
        print(f'This final pose shape is',final.shape)
        print(f"Motion data saved to {save_path}")

if __name__ == "__main__":
    fullyConvery(sys.argv[1])