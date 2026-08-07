import shutil
import os
retain_files = {"model000059999.pt", "opt000059999.pt", "args.json"}
def rename_files(directory):
    entries = os.listdir(directory)
    for entry in entries:  # for each animal
        animal_path = os.path.join(directory,entry)
        motion_entries = os.listdir(animal_path)
        for motion in motion_entries:
            motion_path = os.path.join(animal_path, motion)
            for item in os.listdir(motion_path):
                item_path = os.path.join(motion_path, item)
                if item not in retain_files:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        print(f"Deleted file: {item_path}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        print(f"Deleted folder: {item_path}")



def replace_empty(current_dir):
    # 遍历当前文件夹下的所有文件夹
    for folder_name in os.listdir(current_dir):
        folder_path = os.path.join(current_dir, folder_name)
        
        # 检查是否是文件夹
        if os.path.isdir(folder_path):
            # 新的文件夹名称，将空格替换为下划线
            new_folder_name = folder_name.replace(' ', '_')
            new_folder_path = os.path.join(current_dir, new_folder_name)
            
            # 重命名文件夹
            os.rename(folder_path, new_folder_path)
            print(f"Renamed folder: {folder_path} -> {new_folder_path}")



def rename_bvh(directory):
    # 遍历目录中所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.bvh'):
            # 构造旧的文件完整路径
            old_file = os.path.join(directory, filename)
            # 替换文件名中的空格为下划线
            new_filename = filename.replace(' ', '_')
            # 构造新的文件完整路径
            new_file = os.path.join(directory, new_filename)
            # 重命名文件
            os.rename(old_file, new_file)
            print(f"Renamed '{filename}' to '{new_filename}'")





# Example usage (edit paths before running):
# directory_path = './ckpt_samples'  # replace to ckpt folder
# rename_files(directory_path)

# bvh_folder = './dataset/zoo/Trex'
# rename_bvh(bvh_folder)

# rename_path = 'ckpt_samples/T'
# replace_empty(rename_path)
