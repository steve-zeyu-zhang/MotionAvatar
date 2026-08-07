import numpy as np
import sys
import os
from os.path import join as pjoin


# root_rot_velocity (B, seq_len, 1)
# root_linear_velocity (B, seq_len, 2)
# root_y (B, seq_len, 1)
# ric_data (B, seq_len, (joint_num - 1)*3)
# rot_data (B, seq_len, (joint_num - 1)*6)
# local_velocity (B, seq_len, joint_num*3)
# foot contact (B, seq_len, 4)
def mean_variance(data_dir, save_dir, joints_num, checkpoints_dir, meta_dir, name):
    print("Number of joints:", joints_num)
    file_list = os.listdir(data_dir)
    data_list = []

    for file in file_list:
        data = np.load(pjoin(data_dir, file))
        if np.isnan(data).any():
            print(file)
            continue
        data_list.append(data)

    data = np.concatenate(data_list, axis=0)
    print(data.shape)
    Mean = data.mean(axis=0)
    Std = data.std(axis=0)
    Std[0:1] = Std[0:1].mean() / 1.0
    Std[1:3] = Std[1:3].mean() / 1.0
    Std[3:4] = Std[3:4].mean() / 1.0
    Std[4: 4+(joints_num - 1) * 3] = Std[4: 4+(joints_num - 1) * 3].mean() / 1.0
    Std[4+(joints_num - 1) * 3: 4+(joints_num - 1) * 9] = Std[4+(joints_num - 1) * 3: 4+(joints_num - 1) * 9].mean() / 1.0
    Std[4+(joints_num - 1) * 9: 4+(joints_num - 1) * 9 + joints_num*3] = Std[4+(joints_num - 1) * 9: 4+(joints_num - 1) * 9 + joints_num*3].mean() / 1.0
    Std[4 + (joints_num - 1) * 9 + joints_num * 3: ] = Std[4 + (joints_num - 1) * 9 + joints_num * 3: ].mean() / 1.0

    # assert 8 + (joints_num - 1) * 9 + joints_num * 3 == Std.shape[-1]

    np.save(pjoin(save_dir, 'Mean.npy'), Mean)
    np.save(pjoin(save_dir, 'Std.npy'), Std)

    os.makedirs(meta_dir, exist_ok=True)
    os.makedirs(checkpoints_dir, exist_ok=True)

    np.save(pjoin(meta_dir, 'mean.npy'), Mean)
    np.save(pjoin(meta_dir, 'std.npy'), Std)


    # Read the contents of the opt.txt file
    with open("./assets/opt.txt", "r") as file:
        opt_contents = file.readlines()

    # Modify the 'dataset_name' line
    dataset_line_index = 3  # Index starts from 0
    dataset_name = "dataset_name: " + name + "\n"
    opt_contents[dataset_line_index] = dataset_name

    # Write the modified content to opt.txt in the new location
    with open(os.path.join(checkpoints_dir,'opt.txt'), 'w') as file:
        file.writelines(opt_contents)

    return Mean, Std


if __name__ == '__main__':
    data_dir = './dataset/' + sys.argv[1] + '/new_joint_vecs/'
    save_dir = './dataset/' + sys.argv[1]
    folder_path = './dataset/' + sys.argv[1] + '/new_joints/'
    num_joint = np.load(os.path.join(folder_path, [f for f in os.listdir(folder_path) if f.endswith('.npy')][0])).shape[1]
    checkpoints_dir = './checkpoints/' + sys.argv[1] + '/Comp_v6_KLD005'
    meta_dir = './checkpoints/' + sys.argv[1] + '/Comp_v6_KLD005/meta'
    name = sys.argv[1]
    mean, std = mean_variance(data_dir, save_dir, num_joint, checkpoints_dir, meta_dir, name)