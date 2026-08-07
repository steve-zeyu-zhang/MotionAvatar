import bpy
import sys
import os


def setup_gpu_rendering():
    bpy.context.preferences.addons['cycles'].preferences.get_devices()

    if bpy.context.preferences.addons['cycles'].preferences.devices is None:
        print("No devices found. Check if Cycles is enabled and GPU is supported.")
        return

    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
    bpy.context.scene.cycles.device = 'GPU'

    for device in bpy.context.preferences.addons['cycles'].preferences.devices:
        if device.type == 'CUDA':
            device.use = True


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def import_fbx(fbx_filepath):
    bpy.ops.import_scene.fbx(filepath=fbx_filepath)


def setup_camera(obj):
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    bpy.context.scene.camera = camera

    camera.data.type = 'ORTHO'

    max_dim = max(obj.dimensions)
    obj.scale = (1 / max_dim, 1 / max_dim, 1 / max_dim)
    camera.data.ortho_scale = 500

    camera.location = (500, 400, 500)
    camera.rotation_euler = (1.0, 0, 2.2)


def setup_render_settings(output_path, resolution=(1920, 1080), samples=128, fps=20):
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.resolution_x = resolution[0]
    bpy.context.scene.render.resolution_y = resolution[1]
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.fps = fps
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.cycles.samples = samples
    setup_gpu_rendering()


def setup_lighting(obj):
    bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 10, 10))
    light = bpy.context.object
    light.data.energy = 5.0
    light.data.angle = 3.1415927

    light.location = (
        obj.location.x, obj.location.y - max(obj.dimensions), obj.location.z + max(obj.dimensions) * 0.5)


def prepare_scene(fbx_filepath, output_path):
    clear_scene()
    import_fbx(fbx_filepath)
    obj = bpy.context.selected_objects[0]
    setup_camera(obj)
    setup_lighting(obj)
    setup_render_settings(output_path)


def render_animation():
    bpy.ops.render.render(animation=True, write_still=True)


if __name__ == '__main__':
    # Defaults
    mode = "FILE"  # default to processing a single FILE
    fbx_path = ""  # Path to the FBX file or folder
    output_folder = f"./render_output"  # Default output path

    if '--' in sys.argv:
        args_index = sys.argv.index('--') + 1
        argv = sys.argv[args_index:]
    else:
        argv = []

    # Parse custom command line arguments
    for i, arg in enumerate(argv):
        if arg == "--fbx":
            fbx_path = argv[i + 1]
        elif arg == "--folder":
            fbx_path = argv[i + 1]
            mode = "FOLDER"
        elif arg == "--output":
            output_folder = argv[i + 1]

    # Check mode and process accordingly
    if mode == "FILE":
        # Check if the file exists
        if not os.path.isfile(fbx_path):
            print(f"Error: {fbx_path} does not exist.")
            exit(1)

        output_file = os.path.join(output_folder, os.path.basename(fbx_path).replace('.fbx', '.mp4'))
        prepare_scene(fbx_path, output_file)
        render_animation()

    elif mode == "FOLDER":
        # Check if the folder exists
        if not os.path.isdir(fbx_path):
            print(f"Error: {fbx_path} does not exist.")
            exit(1)

            # Iterate over files in the directory
        for root, dirs, files in os.walk(fbx_path):
            for file in files:
                if file.lower().endswith(".fbx"):
                    fbx_file = os.path.join(root, file)
                    output_file = os.path.join(output_folder, os.path.basename(fbx_file).replace('.fbx', '.mp4'))
                    prepare_scene(fbx_file, output_file)
                    render_animation()

# Output message
print("Rendering completed.")
