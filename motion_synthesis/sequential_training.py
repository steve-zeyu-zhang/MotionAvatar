import os
import subprocess
import argparse


def train_bvh_files(base_dir, save_dir, num_steps, device):
    # 遍历base_dir中的所有子目录和文件
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.bvh'):
                # 获取完整的文件路径
                file_path = os.path.join(root, file)
                # 获取动物的名称和动作名称
                parts = file.split('-')
                animal_name = parts[0]
                action_name = '-'.join(parts[1:]).replace('.bvh', '')

                # 定义保存模型参数的目录
                model_save_dir = os.path.join(save_dir, animal_name, action_name)

                # 构建训练命令
                train_command = [
                    'python', '-m', 'train.train_sinmdm',
                    '--arch', 'unet',
                    '--dataset', 'bvh_general',
                    '--save_dir', model_save_dir,
                    '--sin_path', file_path,
                    '--device', str(device),
                    '--lr_method', 'ExponentialLR',
                    '--lr_gamma', '0.99998',
                    '--use_scale_shift_norm',
                    '--use_checkpoint',
                    '--num_steps', str(num_steps)
                ]

                # 执行训练命令
                print(f"Starting training for {file_path}")
                subprocess.run(train_command)
                print(f"Finished training for {file_path}")


def main():
    parser = argparse.ArgumentParser(description='Train one SinMDM model per BVH file.')
    parser.add_argument('--base_dir', type=str, default='dataset/zoo',
                        help='The base directory containing BVH files (searched recursively).')
    parser.add_argument('--save_dir', type=str, default='ckpt_samples',
                        help='The directory to save trained models.')
    parser.add_argument('--num_steps', type=int, default=60000,
                        help='Number of training steps.')
    parser.add_argument('--device', type=int, default=0,
                        help='CUDA device id passed to each training run.')
    args = parser.parse_args()

    train_bvh_files(args.base_dir, args.save_dir, args.num_steps, args.device)


if __name__ == '__main__':
    main()
