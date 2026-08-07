# LEGACY: earlier OpenLRM-based avatar generation pipeline (SDXL -> Grounded-SAM -> OpenLRM).
# Kept for reference only; the current pipeline uses TripoSR (see tri_main_t2i.py / tri_main_i2i.py).
# Expects sibling clones in the working directory:
#   ./Grounded-Segment-Anything  (https://github.com/IDEA-Research/Grounded-Segment-Anything, with .pth checkpoints)
#   ./OpenLRM                    (https://github.com/3DTopia/OpenLRM)
# Outputs (mesh .ply + rendered video) are written under OpenLRM/dumps/.
import argparse
import os
import subprocess
import sys

from PIL import Image
from diffusers import AutoPipelineForText2Image, DiffusionPipeline
import torch
# pipeline_text2image = AutoPipelineForText2Image.from_pretrained(
#     "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True,add_watermarker=False,use_auth_token=False
# ).to("cuda")
#
# prompt = "Astronaut full body"
# image = pipeline_text2image(prompt=prompt).images[0]
# image.save("output.png")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt',type=str,default='Astronaut')
    args = parser.parse_args()
    prompt = args.prompt
    print(prompt)
    pipeline_text2image = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True,
        add_watermarker=False
    ).to("cuda")
    image = pipeline_text2image(prompt=prompt+"full body, one, 8k, ultra detail").images[0]
    image.save("output_SDXL.png")
    # Define the command as a string
    command_SAM = (
        f'python Grounded-Segment-Anything/grounded_sam_demo.py --config Grounded-Segment-Anything/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py '
        f'--grounded_checkpoint Grounded-Segment-Anything/groundingdino_swint_ogc.pth '
        f'--sam_checkpoint Grounded-Segment-Anything/sam_vit_h_4b8939.pth '
        f'--input_image output_SDXL.png --output_dir ./output '
        f'--box_threshold 0.3 --text_threshold 0.25 '
        f'--text_prompt "{prompt}" --device cuda'
    )
    subprocess.run(command_SAM, shell=True)

    original_image_path = "output/raw_image.jpg"
    mask_image_path = "output/mask.jpg"
    result_image_path = "result_image.png"
    original_img = Image.open(original_image_path)
    mask_img = Image.open(mask_image_path).convert("L")
    mask_img_resized = mask_img.resize(original_img.size, Image.Resampling.LANCZOS)
    white_background = Image.new("RGB", original_img.size, "WHITE")
    mask_inverted = Image.eval(mask_img_resized, lambda x: 255 - x)
    result_img = Image.composite(original_img, white_background, mask_inverted)
    result_img.save(result_image_path)
    #
    # os.chdir('/path/to/directory/containing/OpenLRM')
    # command_3D = 'python -m openlrm.launch infer.lrm --infer "./configs/infer-b.yaml" model_name="zxhezexin/openlrm-mix-base-1.1" image_input="./assets/sample_input/owl.png" export_video=true export_mesh=true'

    # Run the command
    #subprocess.run(command, shell=True)
    # 假设OpenLRM目录位于这个路径下

    os.chdir('OpenLRM')
    # 构建命令
    command_3D = 'python -m openlrm.launch infer.lrm --infer "./configs/infer-b.yaml" model_name="zxhezexin/openlrm-mix-base-1.1" image_input="../result_image.png" export_video=true export_mesh=true'
    subprocess.run(command_3D, shell=True)