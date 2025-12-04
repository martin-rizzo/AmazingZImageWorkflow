<div align="center">

# Amazing Z-Image Workflow
[![Platform](https://img.shields.io/badge/platform%3A-ComfyUI-007BFF)](#)
[![License](https://img.shields.io/github/license/martin-rizzo/AmazingZImageWorkflow?label=license%3A&color=28A745)](#)
[![Version](https://img.shields.io/github/v/tag/martin-rizzo/AmazingZImageWorkflow?label=version%3A&color=D07250)](#)
[![Last](https://img.shields.io/github/last-commit/martin-rizzo/AmazingZImageWorkflow?label=last%20commit%3A)](#) |
[<img src="https://img.shields.io/badge/CivitAI%3A-AmazingZImageWorkflow-EEE?labelColor=1971C2&logo=c%2B%2B&logoColor=white" height="22">](https://civitai.com/models/2181458/amazing-z-image-workflow)  
<img src="files/banner.png" width="75%"></img>

</div>

A workflow developed while experimenting with [Z-Image-Turbo](https://github.com/Tongyi-MAI/Z-Image), extending the ComfyUI base workflow with additional features. This repository includes pre-configured workflows for GGUF and SAFETENSORS formats.

## Table of Contents
1. [Features](#features)
2. [Workflow Overview](#workflow-overview)
3. [Required Custom Nodes](#required-custom-nodes)
4. [Required Checkpoints Files]([#required-checkpoints-files)
   - [For "amazing_zimage-GGUF.json"](#for-amazing_zimage-ggufjson)
   - [For "amazing_zimage-SAFETENSORS.json"](#for-amazing_zimage-safetensorsjson)
   - [For Low-VRAM Systems](#for-low-vram-systems)
5. [License](#license)

## Features

- **Style Selector:** Choose from fourteen customizable image styles for experimentation.
- **Sampler Selector:** Easily pick between the two optimal samplers.
- Preconfigured workflows for each checkpoint formats (GGUF / Safetensors).
- Custom sigma values subjectively adjusted.
- Generated images are saved in the "ZImage" folder, organized by date.
- Includes a trick to enable automatic CivitAI prompt detection.

## Workflow Overview

The repository contains two workflow files:

 1. **"amazing_zimage-GGUF.json"**       : Recommended for GPUs with 12GB or less VRAM.
 2. **"amazing_zimage-SAFETENSORS.json"**: Based directly on the ComfyUI example.

<sub>You'll often come across discussions about the best file format for ComfyUI. Based on my experience, GGUF quantized models offer a better balance between compactness and maintaining good prompt response compared to SafeTensors versions. However, it's also true that ComfyUI has internal speed enhancements that work more effectively with SafeTensors, which might lead you to prefer larger SafeTensors files. The reality is that this depends on several factors: your ComfyUI version, PyTorch setup, CUDA configuration, GPU type, and available VRAM and RAM. To help you out, I've included links below to various checkpoint versions so you can determine what works best for your specific system.</sub>

## Required Custom Nodes

These nodes can be installed via [ComfyUI-Manager](https://github.com/Comfy-Org/ComfyUI-Manager) or downloaded from their respective repositories.

 - **[rgthree](https://github.com/rgthree/rgthree-comfy)**: Required for both workflows.
 - **[ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF)**: Required if you are using the workflow preconfigured for GGUF checkpoints.

## Required Checkpoints Files

### For "amazing_zimage-GGUF.json"

This is my recommended workflow. \
Using **Q5_K_S** quants, you will likely achieve the best balance between file size and prompt response.

 - __[z_image_turbo-Q5_K_S.gguf](https://huggingface.co/jayn7/Z-Image-Turbo-GGUF/blob/main/z_image_turbo-Q5_K_S.gguf)__ <sub>(5.19 GB)</sub>\
   Local Directory: __`ComfyUI/models/diffusion_models/`__
 - __[Qwen3-4B.i1-Q5_K_S.gguf](https://huggingface.co/mradermacher/Qwen3-4B-i1-GGUF/blob/main/Qwen3-4B.i1-Q5_K_S.gguf)__ <sub>(2.82 GB)</sub>\
   Local Directory: __`ComfyUI/models/text_encoders/`__
 - __[ae.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors)__ <sub>(335 MB)</sub>\
   Local Directory: __`ComfyUI/models/vae/`__

### For "amazing_zimage-SAFETENSORS.json"

Based directly on the official ComfyUI example. \
<sub>While it may require more than 12GB of VRAM to run smoothly, ComfyUI's optimizations may allow it to work well on your system.</sub>

  - __[z_image_turbo_bf16.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors)__ <sub>(12.3 GB)</sub>\
    Local Directory: __`ComfyUI/models/diffusion_models/`__
  - __[qwen_3_4b.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/text_encoders/qwen_3_4b.safetensors)__ <sub>(8.04 GB)</sub>\
    Local Directory: __`ComfyUI/models/text_encoders/`__
  - __[ae.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors)__ <sub>(335 MB)</sub>\
    Local Directory: __`ComfyUI/models/vae/`__

### For Low-VRAM Systems

If neither of the two versions nor their checkpoints function adequately on your system, you can find below links to several checkpoint files in GGUF and SafeTensors formats. Feel free to try these alternatives and see which one works best for you.

- Links will be provided soon.

## License

This project is licensed under the Unlicense license.\
See the ["LICENSE"](LICENSE) file for details.

