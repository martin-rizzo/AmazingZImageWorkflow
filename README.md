# Simple Z-Image Workflow

A workflow developed while experimenting with z-image, incorporating additional features beyond the base ComfyUI workflow.
This repository includes three workflows optimized for different GPU VRAM capacities.

## Features

- Includes some configurable styles for testing and experimentation.
- Versions in both .safetensors and .gguf formats to support a range of GPUs.
- Custom sigma values adjusted to my preference (subjectively better prompt adherence).
- Includes a trick to enable CivitAI automatic prompt detection.

## Workflow Overview

The repository contains three workflow files, each optimized for different GPU VRAM capacities:

 1. **simple_zimage-GGUF.json**       : Recommended for GPUs with 12GB or less VRAM.
 2. **simple_zimage-GGUFSMALL.json**  : For GPUs with less than 8GB VRAM.
 3. **simple_zimage-SAFETENSORS.json**: Based directly on the ComfyUI example.

## Workflow Files and Checkpoints
> [!NOTE]
> All workflows requires the custom "rgthree" nodes. \
> The GGUF workflows also require the additional custom "ComfyUI-GGUF" nodes.

### "simple_zimage-GGUF.json"
Works smoothly with 12GB of VRAM or less, it may handle around 8GB as well. \
Checkpoints used:

 - __[z_image_turbo-Q5_K_M.gguf](https://huggingface.co/jayn7/Z-Image-Turbo-GGUF/blob/main/z_image_turbo-Q5_K_M.gguf)__ <sub>(5.52 GB)</sub>\
   Local Directory: __`ComfyUI/models/diffusion_models/`__
 - __[Qwen3-4B.i1-Q5_K_M.gguf](https://huggingface.co/mradermacher/Qwen3-4B-i1-GGUF/blob/main/Qwen3-4B.i1-Q5_K_M.gguf)__ <sub>(2.89 GB)</sub>\
   Local Directory: __`ComfyUI/models/text_encoders/`__
 - __[ae.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors)__ <sub>(335 MB)</sub>\
   Local Directory: __`ComfyUI/models/vae/`__

### "simple_zimage-GGUFSMALL.json"
Optimized for GPUs with limited VRAM (less than 8GB), though prompt accuracy might be affected. \
Checkpoints used:

  - __[z_image_turbo-Q3_K_M.gguf](https://huggingface.co/jayn7/Z-Image-Turbo-GGUF/blob/main/z_image_turbo-Q3_K_M.gguf)__ <sub>(4.12 GB)</sub>\
    Local Directory: __`ComfyUI/models/diffusion_models/`__
  - __[Qwen3-4B.i1-Q2_K.gguf](https://huggingface.co/mradermacher/Qwen3-4B-i1-GGUF/blob/main/Qwen3-4B.i1-Q2_K.gguf)__ <sub>(1.67 GB)</sub>\
    Local Directory: __`ComfyUI/models/text_encoders/`__
  - __[ae.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors)__ <sub>(335 MB)</sub>\
    Local Directory: __`ComfyUI/models/vae/`__

### "simple_zimage-SAFETENSORS.json"
Based directly on the official ComfyUI example, suitable for GPUs with around 12GB of VRAM or more. \
Checkpoints used:

  - __[z_image_turbo_bf16.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors)__ <sub>(12.3 GB)</sub>\
    Local Directory: __`ComfyUI/models/diffusion_models/`__
  - __[qwen_3_4b.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/text_encoders/qwen_3_4b.safetensors)__ <sub>(8.04 GB)</sub>\
    Local Directory: __`ComfyUI/models/text_encoders/`__
  - __[ae.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors)__ <sub>(335 MB)</sub>\
    Local Directory: __`ComfyUI/models/vae/`__


## License

This project is licensed under the Unlicense.

