# Amazing Z-Image Workflow v3.0

A workflow for "Z-Image-Turbo" extending the ComfyUI base workflow with additional features, particularly focused on high-quality image styles and ease of use. The package includes pre-configured workflows for GGUF and SAFETENSORS formats.

## Table of Contents
1. Features
2. Workflows Overview
3. Required Custom Nodes
4. Required Checkpoints Files
5. License

## Features
- Style Selector: Choose from fifteen customizable image styles.
- Z-Image Enhancer: Improves final image quality by performing a double pass.
- Spicy Impact Booster: Adds a subtle spicy condiment to the prompt (fully experimental).
- Alternative Sampler Switch: Easily test generation with an alternative sampler.
- Landscape Orientation Switch: Change to horizontal image generation with a single click.
- Smaller Images Switch: Generate smaller images, faster and consuming less VRAM.
- Preconfigured workflows for each checkpoint format (GGUF / SAFETENSORS).
- Custom sigma values fine-tuned to my personal preference (100% subjective).
- Generated images are saved in the "ZImage" folder, organized by date.
- Incorporates a trick to enable automatic CivitAI prompt detection.

## Workflows Overview
The available styles are organized into workflows based on their focus:
- `amazing-z-image` : The original general-purpose workflow with a variety of image styles.
- `amazing-z-comics`: Workflow dedicated to illustration (comics, anime, pixel art, etc.).
- `amazing-z-photo` : Workflow dedicated to photographic images (phone, vintage, production photos, etc.).

Each workflow comes in two versions, one for GGUF checkpoints and another for SafeTensors.
This is reflected in the filenames:
- `amazing-z-###_GGUF.json`       : Recommended for GPUs with 12GB or less VRAM.
- `amazing_z-###_SAFETENSORS.json`: Based directly on the ComfyUI example.

When using ComfyUI, you may encounter debates about the best checkpoint format. From my experience, GGUF quantized models provide a better balance between size and prompt response quality compared to SafeTensors versions. However, it's worth noting that ComfyUI includes optimizations that work more efficiently with SafeTensors files, which might make them preferable for some users despite their larger size. The optimal choice depends on factors like your ComfyUI version, PyTorch setup, CUDA configuration, GPU model, and available VRAM and RAM. To help you find the best fit for your system, I've included links to various checkpoint versions below.

## Required Custom Nodes
These nodes can be installed via ComfyUI-Manager or downloaded from their respective repositories:
- https://github.com/rgthree/rgthree-comfy : Required for both workflows.
- https://github.com/city96/ComfyUI-GGUF   : Required if you are using the workflow preconfigured for GGUF checkpoints.

## Required Checkpoints Files

### For "amazing-z-###_GGUF.json"
Workflows with checkpoint in GGUF format. (recommended)

- "z_image_turbo-Q5_K_S.gguf" [5.19 GB]
  Download: https://huggingface.co/jayn7/Z-Image-Turbo-GGUF/blob/main/z_image_turbo-Q5_K_S.gguf
  Local Directory: `ComfyUI/models/diffusion_models/`
  
- "Qwen3-4B.i1-Q5_K_S.gguf" [2.82 GB]
  Download: https://huggingface.co/mradermacher/Qwen3-4B-i1-GGUF/blob/main/Qwen3-4B.i1-Q5_K_S.gguf
  Local Directory: `ComfyUI/models/text_encoders/`
  
- "ae.safetensors" [335 MB]
  Download: https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors 
  Local Directory: `ComfyUI/models/vae/`

- "4x_Nickelback_70000G.safetensors" (for image enhancer) [66.9 MB]
  Download: https://huggingface.co/martin-rizzo/ESRGAN-4x/blob/main/4x_Nickelback_70000G.safetensors 
  Local Directory: `ComfyUI/models/upscale_models/`
  
- "4x_foolhardy_Remacri.safetensors" (for image enhancer) [66.9 MB]
  Download: https://huggingface.co/martin-rizzo/ESRGAN-4x/blob/main/4x_foolhardy_Remacri.safetensors 
  Local Directory: `ComfyUI/models/upscale_models/`


### For "amazing-z-###_SAFETENSORS.json"
Based directly on the official ComfyUI example.

- "z_image_turbo_bf16.safetensors" [12.3 GB]
  Download: https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors 
  Local Directory: `ComfyUI/models/diffusion_models/`
  
- "qwen_3_4b.safetensors" [8.04 GB]
  Download: https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/text_encoders/qwen_3_4b.safetensors
  Local Directory: `ComfyUI/models/text_encoders/`
  
- "ae.safetensors" [335 MB]
  Download: https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors
  Local Directory: `ComfyUI/models/vae/`
  
- "4x_Nickelback_70000G.safetensors" (for image enhancer) [66.9 MB]
  Download: https://huggingface.co/martin-rizzo/ESRGAN-4x/blob/main/4x_Nickelback_70000G.safetensors 
  Local Directory: `ComfyUI/models/upscale_models/`
  
- "4x_foolhardy_Remacri.safetensors" (for image enhancer) [66.9 MB]
  Download: https://huggingface.co/martin-rizzo/ESRGAN-4x/blob/main/4x_foolhardy_Remacri.safetensors 
  Local Directory: `ComfyUI/models/upscale_models/`
  

### For Low-VRAM Systems
If neither of the two provided versions nor their associated checkpoints perform adequately on your system, you can find links to several alternative checkpoint files below. Feel free to experiment with these options to determine which works best for you.

#### Diffusion Models (ComfyUI/models/diffusion_models/)

* https://huggingface.co/jayn7/Z-Image-Turbo-GGUF/tree/main
    This repository hosts various quantized versions of the `z_image_turbo` model (e.g., Q4_K_S, Q4_K_M, Q3_K_S). While some of these quantizations offer significantly reduced file sizes, this often comes at the expense of final output quality.

* https://huggingface.co/T5B/Z-Image-Turbo-FP8/tree/main
    Similar to the GGUF options, this repository provides two `z_image_turbo` models quantized to FP8 (8-bit floating point) in SafeTensors format. These can serve as replacements for the original SafeTensors model, but in my opinion, they degrade quality quite a bit.

#### Text Encoders (ComfyUI/models/text_encoders/)

* https://huggingface.co/mradermacher/Qwen3-4B-i1-GGUF/tree/main
    This repository offers various quantized versions of the `Qwen3-4B` text encoder in GGUF format (e.g., Q2_K, Q3_K_M). Note: Quantizations beginning with "IQ" might not work, as the GGUF node did not support them during my testing.


## License
This project is licensed under the Unlicense license.
See the "LICENSE" file for details.

## More Info
- https://github.com/martin-rizzo/AmazingZImageWorkflow
- https://civitai.com/models/2181458/amazing-z-image-workflow
- https://civitai.com/models/2213075/amazing-z-comics-workflow
- https://civitai.com/models/2225379/amazing-z-photo-workflow
