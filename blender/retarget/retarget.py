import argparse
import bpy
import os
import sys
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
def get_script_args():
    argv = sys.argv
    if "--" not in argv:
        argv = []  # 如果没有找到 "--"，就假设没有脚本参数
    else:
        argv = argv[argv.index("--") + 1:]  # 获取所有 "--" 之后的参数
    parser = argparse.ArgumentParser(description="Remap and Export Animation")
    parser.add_argument("-fbx", "--fbx_name", type=str, default="root.fbx", help="FBX file name")
    parser.add_argument("-t", "--target_motion_name", type=str, required=True, help="Target motion name")
    parser.add_argument("-s", "--start_frame", type=int, default=0, help="Start frame")
    parser.add_argument("-e", "--end_frame", type=int, default=200, help="End frame")
    parser.add_argument("-o", "--output_fbx", type=str, default="output.fbx", help="Output FBX file name")
    parser.add_argument("-human", "--is_human", action="store_true", default=False, help="the FBX is for human?")
    parser.add_argument('-a','--animal',type=str,help='if not a human, please tell me what kind of animal you are using')
    args = parser.parse_known_args(argv)[0]
    return args

args = get_script_args()

# Assuming that the FBX and BVH files are at the same location as the provided names
# Import FBX
bpy.ops.import_scene.fbx(filepath=args.fbx_name)
# 获取当前选中的对象
selected_objects = bpy.context.selected_objects

# 筛选出骨架对象
imported_armatures = [obj for obj in selected_objects if obj.type == 'ARMATURE']

# 如果确实导入了新的骨架对象，获取其名称
if imported_armatures:
    # 可能有多个骨架，所以这里获取最后一个骨架的名称，它通常是最新导入的
    armature_name = imported_armatures[-1].name
    print(f"The imported armature name is: {armature_name}")
else:
    print("No armature was imported.")
    raise NameError

target_name = armature_name


# Import BVH
bpy.ops.import_anim.bvh(filepath=args.target_motion_name)

# 获取当前选中的对象
selected_objects = bpy.context.selected_objects

# 筛选出骨架对象
imported_armatures = [obj for obj in selected_objects if obj.type == 'ARMATURE']

# 如果确实导入了新的骨架对象，获取其名称
if imported_armatures:
    # 可能有多个骨架，所以这里获取最后一个骨架的名称，它通常是最新导入的
    armature_name = imported_armatures[-1].name
    print(f"The imported armature name is: {armature_name}")
    armature = imported_armatures[-1]
    armature.rotation_euler[2] = -math.pi / 2
else:
    print("No armature was imported.")
    raise NameError

source_name = armature_name


# ... Insert the remapping operations here ...
# E.g., setting up constraints, retargeting, etc.
bpy.context.scene.source_rig = source_name
bpy.context.scene.target_rig = target_name
bpy.ops.arp.auto_scale()
bpy.ops.arp.build_bones_list()

if args.is_human:
    bpy.ops.arp.import_config('EXEC_DEFAULT', filepath=os.path.join(SCRIPT_DIR, 'motion_collection', 'match_map', 'human.bmap'))
else:
    print('it is an animal')
    animal_type = args.animal
    bpy.ops.arp.import_config('EXEC_DEFAULT', filepath=os.path.join(SCRIPT_DIR, 'motion_collection', 'match_map', f'{animal_type}.bmap'))
bpy.ops.arp.redefine_rest_pose()
bone_names =["LeftUpLeg","LeftLeg","RightUpLeg","RightLeg","LeftArm","LeftForeArm","RightArm","RightForeArm"]
obj = bpy.data.objects[source_name]
for bone_name in bone_names:
    if bone_name in obj.pose.bones:
        obj.pose.bones[bone_name].bone.select = True
bpy.ops.arp.copy_bone_rest()
bpy.ops.arp.save_pose_rest()
bpy.ops.arp.retarget(frame_start=args.start_frame, frame_end=args.end_frame)

# Select the armature to be exported
armature_name = target_name  # Replace with the actual name of your armature
bpy.data.objects[armature_name].select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects[armature_name]

# Set up the frames for baking the animation
bpy.context.scene.frame_start = args.start_frame
bpy.context.scene.frame_end = args.end_frame



# select the Armature you want to export
armature_name = target_name


bpy.ops.object.select_all(action='DESELECT')

# select all child objects
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE' and obj.name == armature_name:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        for child in obj.children:
            if child.type == 'MESH':
                child.select_set(True)
        break


selected_objects = bpy.context.selected_objects


print("Selected objects:")
for obj in selected_objects:
    print(obj.name)
# Export the final armature animation to FBX
output_fbx_path = bpy.path.abspath(args.output_fbx)  # Ensure the path is absolute
bpy.ops.export_scene.fbx(
    filepath=output_fbx_path,
    use_selection=True,    # 导出选中的对象
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Z',     # 前向轴设置为'-Z'
    axis_up='Y',           # 上向轴设置为'Y'
    global_scale=1.0,
    apply_unit_scale=True,
    bake_space_transform=False,
    object_types={'MESH', 'ARMATURE'},  # 包含网格和骨架
    use_mesh_modifiers=True,  # 应用所有修改器
    use_mesh_modifiers_render=True,
    mesh_smooth_type='FACE',  # 平滑类型
    use_subsurf=False,
    use_mesh_edges=False,
    use_tspace=False,        # 切线空间导出
    use_custom_props=False,
    add_leaf_bones=True,     # 添加末端骨骼
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    use_armature_deform_only=False,
    armature_nodetype='NULL',
    bake_anim=True,          # 确保导出动画
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=True,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=1.0,
    path_mode='COPY',
    embed_textures=False,
    batch_mode='OFF',
    use_batch_own_dir=True,
    use_metadata=True
)

print(f"Exported remapped animation to '{output_fbx_path}'")