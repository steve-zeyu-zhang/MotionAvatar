import bpy
import argparse
import sys

def render_blend_file(blend_file_path, save_path, frame_start=None, frame_end=None):
    # Open the blend file
    bpy.ops.wm.open_mainfile(filepath=blend_file_path)

    # Set the rendering engine to Cycles
    bpy.context.scene.render.engine = 'CYCLES'

    # Set device type
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'

    # Enable GPU device(s)
    for device in bpy.context.preferences.addons['cycles'].preferences.devices:
        if device.type == 'CUDA':
            device.use = True

    # Print the current compute device type
    print("Compute Device Type:", bpy.context.preferences.addons['cycles'].preferences.compute_device_type)

    # Print enabled GPU devices
    for device in bpy.context.preferences.addons['cycles'].preferences.devices:
        if device.use:
            print(f"Device: {device.name} - Type: {device.type} - Enabled: {device.use}")

    # Set the frame range for rendering if provided
    if frame_start is not None:
        bpy.context.scene.frame_start = frame_start
    else:
        frame_start = bpy.context.scene.frame_start  # Use default value

    if frame_end is not None:
        bpy.context.scene.frame_end = frame_end
    else:
        frame_end = bpy.context.scene.frame_end  # Use default value

    # Print the frame range being used
    print(f"Rendering from frame {frame_start} to frame {frame_end}")

    # Render settings
    #bpy.context.scene.render.resolution_x = 1920
    #bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.filepath = save_path
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'

    # Execute render
    bpy.ops.render.render(animation=True, write_still=True)

def main():
    # Filter out Blender's own arguments
    args = sys.argv[sys.argv.index("--") + 1:]

    parser = argparse.ArgumentParser(description="Render a Blender file with specified frame range.")
    parser.add_argument('--blend_path', type=str, required=True, help='Path to the Blender .blend file')
    parser.add_argument('--save_path', type=str, required=True, help='Path to the save .mp4 file')
    parser.add_argument('--frame_start', type=int, help='Start frame for rendering', default=None)
    parser.add_argument('--frame_end', type=int, help='End frame for rendering', default=None)

    args = parser.parse_args(args)

    render_blend_file(args.blend_path, args.save_path, args.frame_start, args.frame_end)

if __name__ == "__main__":
    main()
