# Avatar Generation (Text / Image → 3D Mesh)

This directory contains the avatar-generation stage of the **Motion Avatar** pipeline: a text prompt is turned into an image with **SDXL** (via `diffusers`), the subject is segmented out with **Grounded-Segment-Anything** and composited onto a white background, and **TripoSR** reconstructs a textured 3D mesh from that image. The scripts here are thin orchestration layers that shell out to local clones of the upstream repos (see Installation below). The resulting mesh is then rigged and motion-retargeted in the next pipeline stage (see the `blender/` component of this repository).

## Installation

Tested with Python 3.10 and CUDA 11.8, on Linux and Windows 11.

```bash
conda create -n motionavatar-gen python=3.10 -y
conda activate motionavatar-gen

# PyTorch with CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# glue-script dependencies (diffusers/SDXL, PIL)
pip install -r requirements.txt
```

### 1. TripoSR (required)

Clone into this directory and install its requirements:

```bash
git clone https://github.com/VAST-AI-Research/TripoSR.git
pip install -r TripoSR/requirements.txt
```

The TripoSR model weights (`stabilityai/TripoSR`) auto-download from Hugging Face on first run.

### 2. Grounded-Segment-Anything (required)

Both `tri_main_t2i.py` and `tri_main_i2i.py` call Grounded-SAM for subject segmentation / background removal.

```bash
git clone https://github.com/IDEA-Research/Grounded-Segment-Anything.git
cd Grounded-Segment-Anything
python -m pip install -e segment_anything
pip install --no-build-isolation -e GroundingDINO
pip install opencv-python pycocotools matplotlib onnxruntime onnx

# model checkpoints
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
wget https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
cd ..
```

### 3. OpenLRM (optional, legacy pipeline only)

Install this to run the legacy `main_openlrm.py`:

```bash
git clone https://github.com/3DTopia/OpenLRM.git
cd OpenLRM && pip install -r requirements.txt && cd ..
```

## Data preparation

No dataset is required for this stage. All model weights are downloaded automatically (SDXL `stabilityai/stable-diffusion-xl-base-1.0` and `stabilityai/TripoSR` from Hugging Face; OpenLRM `zxhezexin/openlrm-mix-base-1.1` likewise) except the two Grounded-SAM checkpoints fetched with `wget` above. The expected working-directory layout is:

```
avatar_generation/
├── tri_main_t2i.py
├── tri_main_i2i.py
├── main_openlrm.py               # legacy OpenLRM variant
├── requirements.txt
├── TripoSR/                      # cloned
├── Grounded-Segment-Anything/    # cloned
│   ├── sam_vit_h_4b8939.pth
│   └── groundingdino_swint_ogc.pth
└── OpenLRM/                      # cloned (optional, legacy only)
```

Run the scripts from this directory. If you cloned the upstream repos elsewhere, point the scripts at them with `--triposr_dir` / `--grounded_sam_dir`.

## Usage

### Text → 3D avatar (`tri_main_t2i.py`)

```bash
python tri_main_t2i.py --prompt "a golden retriever" --mesh_name result_mesh --mc_resolution 256
```

| Flag | Default | Meaning |
|---|---|---|
| `--prompt` | `Astronaut` | Text prompt; the script appends `", full body, one, 8k, ultra detail"` and also uses the raw prompt as the Grounded-SAM segmentation query |
| `--mesh_name` | `result_mesh` | Basename of the white-background intermediate image (`<mesh_name>.png`) |
| `--mc_resolution` | `256` | TripoSR marching-cubes resolution; higher values (e.g. 1024) give finer meshes but need more VRAM |
| `--triposr_dir` | `./TripoSR` | Path to the TripoSR clone |
| `--grounded_sam_dir` | `./Grounded-Segment-Anything` | Path to the Grounded-SAM clone (with the `.pth` checkpoints inside) |

Steps: SDXL generates `output_SDXL.png` → Grounded-SAM writes `output/raw_image.jpg` + `output/mask.jpg` → the script composites the subject onto white as `<mesh_name>.png` → TripoSR writes the mesh to `output/0/mesh.obj` plus a NeRF-rendered turntable (`--render` is always passed).

### Image → 3D avatar (`tri_main_i2i.py`)

```bash
python tri_main_i2i.py --image path/to/img.png --prompt "dog" --mc_resolution 256
```

Same flags as above, minus `--mesh_name`, plus `--image` (input image path; `--prompt` here is the Grounded-SAM query for what to segment, no SDXL involved). Output goes to a timestamped directory `output/<img>_mc_<res>_<timestamp>/0/mesh.obj` with renders.

### Legacy: OpenLRM variant (`main_openlrm.py`)

The earlier pipeline (SDXL → Grounded-SAM → OpenLRM instead of TripoSR):

```bash
python main_openlrm.py --prompt "Astronaut"
```

It expects `./Grounded-Segment-Anything` and `./OpenLRM` clones in the working directory and writes the mesh (`.ply`) and a rendered video under `OpenLRM/dumps/`.

### Output format and next stage

TripoSR exports `mesh.obj` by default; the legacy OpenLRM path exports `.ply`. The generated mesh is the input to the rigging / motion-retargeting stage in `blender/` (Auto-Rig Pro based), which animates the avatar with the generated motion.

## Acknowledgements & License

This stage builds directly on:

- [TripoSR](https://github.com/VAST-AI-Research/TripoSR) (Tripo AI & Stability AI) — MIT license
- [SDXL](https://arxiv.org/abs/2307.01952) via [diffusers](https://github.com/huggingface/diffusers) (`stabilityai/stable-diffusion-xl-base-1.0`)
- [Grounded-Segment-Anything](https://github.com/IDEA-Research/Grounded-Segment-Anything) (IDEA-Research) — Apache-2.0 license
- [OpenLRM](https://github.com/3DTopia/OpenLRM) — Apache-2.0 license (legacy variant)

Each upstream repo keeps its own license in its own clone; model weights are subject to their respective model licenses on Hugging Face. The glue scripts in this directory are released under this repository's license (see the repository root).
