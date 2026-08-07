import os
import os.path as osp
from Motion import BVH
import numpy as np
from glob import glob
import sys

def fullyConvery(in_dir):
    """
    This function converts a standard bvh file (except Mixamo bvh which has weird joints number) to standard npy pose file.
    (frame,joints,feats) -> (frame,joints,feats)
    e.g. HumanML3D: (frame,22,3) -> (frame,22,3)
    
    """
    bvh_files = glob(osp.join(in_dir,'*.bvh'))
    for idx, in_file in enumerate(bvh_files):
        anim, joint_names, frametime = BVH.load(in_file)
        motion = anim.positions # 100, 69 ,3
        print(f'This pose shape is',motion.shape)
        save_path = os.path.splitext(in_file)[0] + '.npy'
        np.save(save_path, motion)
        print(f"Motion data saved to {save_path}")



if __name__ == "__main__":
    fullyConvery(sys.argv[1])
     