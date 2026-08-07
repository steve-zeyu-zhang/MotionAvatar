# Use TripoSR for 3D, i2i
import argparse
import os
import subprocess
import sys
from datetime import datetime
from PIL import Image
from diffusers import AutoPipelineForText2Image, DiffusionPipeline
import torch

if __name__ == '__main__':
    now = datetime.now() 
    time_str = now.strftime("%Y-%m-%d_%H-%M-%S")

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, nargs="+", help="Path to input image(s).")
    parser.add_argument('--prompt',type=str,default='human')
    parser.add_argument('--mc_resolution',type=int,default=256)
    parser.add_argument('--triposr_dir',type=str,default='./TripoSR',
                        help='Path to a local clone of https://github.com/VAST-AI-Research/TripoSR')
    parser.add_argument('--grounded_sam_dir',type=str,default='./Grounded-Segment-Anything',
                        help='Path to a local clone of https://github.com/IDEA-Research/Grounded-Segment-Anything (with the .pth checkpoints inside)')
    args = parser.parse_args()
    img_name = args.image[0]
    prompt = args.prompt
    mc_resolution = args.mc_resolution
    triposr_dir = args.triposr_dir
    gsam_dir = args.grounded_sam_dir
    print('The original image is at',img_name)
    # pipeline_text2image = AutoPipelineForText2Image.from_pretrained(
    #     "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True,
    #     add_watermarker=False
    # ).to("cuda")
    # image = pipeline_text2image(prompt=prompt+"full body, one, 8k, ultra detail").images[0]
    # image.save("output_SDXL.png")
    # Define the command as a string
    command_SAM = (
        f'python {gsam_dir}/grounded_sam_demo.py --config {gsam_dir}/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py '
        f'--grounded_checkpoint {gsam_dir}/groundingdino_swint_ogc.pth '
        f'--sam_checkpoint {gsam_dir}/sam_vit_h_4b8939.pth '
        f'--input_image {img_name} --output_dir ./output '
        f'--box_threshold 0.3 --text_threshold 0.25 '
        f'--text_prompt "{prompt}" --device cuda'
    )
    subprocess.run(command_SAM, shell=True)

    original_image_path = "output/raw_image.jpg"
    mask_image_path = "output/mask.jpg"
    img_clean_name = os.path.basename(img_name)

    result_image_path = img_clean_name
    print('SAM output goes to',result_image_path)
    original_img = Image.open(original_image_path)
    mask_img = Image.open(mask_image_path).convert("L")
    mask_img_resized = mask_img.resize(original_img.size, Image.Resampling.LANCZOS)
    white_background = Image.new("RGB", original_img.size, "WHITE")
    mask_inverted = Image.eval(mask_img_resized, lambda x: 255 - x)
    result_img = Image.composite(original_img, white_background, mask_inverted)
    result_img.save(result_image_path)
    folder_dir = img_clean_name.split('.')[0]+f'_mc_{mc_resolution}_{time_str}'
    command_TripoSR = (
           f'python {triposr_dir}/run.py {result_image_path} --output-dir output/{folder_dir} --mc-resolution {mc_resolution} --render'
        )

    subprocess.run(command_TripoSR, shell=True)
