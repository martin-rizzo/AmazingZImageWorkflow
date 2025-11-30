# Simple Z-Image Workflow

A workflow developed while experimenting with z-image, incorporating additional features beyond the base ComfyUI workflow. This repository includes three workflows optimized for different GPU VRAM capacities.

## Features

- Predefined styles for experimentation
- Configured to work with both .safetensors and .gguf formats for adaptable VRAM usage 
- Additional nodes to enable automatic prompt detection by CivitAI
- Custom sigma values (personal preference noted for better prompt adherence)

## Workflow Overview

The repository contains three workflow files, each optimized for different GPU VRAM capacities:

1. simple_zimage-SAFETENSORS.json: Suitable for 8GB+ VRAM
2. simple_zimage-GGUF.json: Recommended for 4-12GB VRAM 
3. simple_zimage-GGUFSMALL.json: For systems with less than 8GB VRAM

Each workflow requires the custom "rgthree" node. The GGUF workflows also require the additional "ComfyUI-GGUF" nodes.

## Workflow Files and Checkpoints

### simple_zimage-SAFETENSORS.json
Suitable for GPUs with 8GB+ VRAM.
Checkpoints used:
- z_image_turbo_bf16.safetensors: Diffusion model (Download from Hugging Face, Local Directory: ComfyUI/models/diffusion_models/)
- qwen_3_4b.safetensors: Text encoder model (Download from Hugging Face, Local Directory: ComfyUI/models/text_encoders/)  
- ae.safetensors: VAE model (Download from Hugging Face, Local Directory: comfyui/models/vae/)

### simple_zimage-GGUF.json
Recommended for GPUs with less than 12GB VRAM.
Checkpoints used:
- z_image_turbo-Q5_K_M.gguf: Diffusion model (Download from Hugging Face, Local Directory: ComfyUI/models/diffusion_models/)
- Qwen3-4B.i1-Q5_K_M.gguf: Text encoder model (Download from Hugging Face, Local Directory: ComfyUI/models/text_encoders/)  
- ae.safetensors: VAE model (Local Directory: comfyui/models/vae/)

### simple_zimage-GGUFSMALL.json
For GPUs with less than 8GB VRAM.
Checkpoints used:
- z_image_turbo-Q3_K_M.gguf: Diffusion model (Download from Hugging Face, Local Directory: ComfyUI/models/diffusion_models/)
- Qwen3-4B.i1-Q2_K.gguf: Text encoder model (Download from Hugging Face, Local Directory: ComfyUI/models/text_encoders/)  
- ae.safetensors: VAE model (Local Directory: comfyui/models/vae/)

Please note that the smaller GGUF variant may struggle to accurately follow prompts at times.

## License

This project is licensed under the Unlicense.

