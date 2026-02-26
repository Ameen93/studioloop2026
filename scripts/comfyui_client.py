"""
ComfyUI API client for StudioLoop asset generation.
Connects to ComfyUI running on Windows machine and manages workflow submission,
polling, and image download.
"""

import json
import time
import uuid
import urllib.request
import urllib.parse
from pathlib import Path


SERVER = "192.168.10.143:8000"
CLIENT_ID = str(uuid.uuid4())


def queue_prompt(workflow: dict) -> str:
    """Submit a workflow to ComfyUI. Returns prompt_id."""
    payload = json.dumps({"prompt": workflow, "client_id": CLIENT_ID}).encode("utf-8")
    req = urllib.request.Request(
        f"http://{SERVER}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def wait_for_completion(prompt_id: str, timeout: int = 300, poll_interval: float = 2.0) -> dict:
    """Poll history until the prompt completes. Returns the history entry."""
    start = time.time()
    while time.time() - start < timeout:
        url = f"http://{SERVER}/history/{prompt_id}"
        with urllib.request.urlopen(url) as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(poll_interval)
    raise TimeoutError(f"Prompt {prompt_id} did not complete within {timeout}s")


def download_image(prompt_id: str, history_entry: dict, output_path: str) -> str:
    """Download the first output image from a completed prompt. Returns saved path."""
    outputs = history_entry.get("outputs", {})
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            img = node_output["images"][0]
            params = urllib.parse.urlencode({
                "filename": img["filename"],
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
            })
            url = f"http://{SERVER}/view?{params}"
            with urllib.request.urlopen(url) as resp:
                data = resp.read()
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(data)
            return output_path
    raise ValueError(f"No images found in prompt {prompt_id} outputs")


def build_flux_workflow(
    prompt: str,
    width: int = 1024,
    height: int = 768,
    steps: int = 4,
    seed: int = 42,
    cfg: float = 1.0,
    loras: list[dict] | None = None,
    filename_prefix: str = "studioloop",
) -> dict:
    """
    Build a Flux Schnell workflow with optional LoRA stacking.

    loras: list of {"name": "file.safetensors", "strength": 0.7}
    """
    workflow = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "flux1-schnell.safetensors",
                "weight_dtype": "default",
            },
        },
        "2": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                "type": "flux",
            },
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "ae.safetensors"},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["2", 0]},
        },
        "5": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
            },
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["6", 0], "vae": ["3", 0]},
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {"images": ["7", 0], "filename_prefix": filename_prefix},
        },
    }

    # Chain LoRAs between UNETLoader and KSampler
    if loras:
        model_source = ["1", 0]  # starts from UNETLoader
        clip_source = ["2", 0]   # starts from DualCLIPLoader

        for i, lora in enumerate(loras):
            node_id = str(100 + i)
            workflow[node_id] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "lora_name": lora["name"],
                    "strength_model": lora.get("strength", 0.7),
                    "strength_clip": lora.get("strength", 0.7),
                    "model": model_source,
                    "clip": clip_source,
                },
            }
            model_source = [node_id, 0]
            clip_source = [node_id, 1]

        # Reconnect KSampler to last LoRA output
        workflow["6"]["inputs"]["model"] = model_source
        # Reconnect CLIPTextEncode to last LoRA's clip output
        workflow["4"]["inputs"]["clip"] = clip_source

    return workflow


def generate_image(
    prompt: str,
    output_path: str,
    width: int = 1024,
    height: int = 768,
    steps: int = 4,
    seed: int = 42,
    cfg: float = 1.0,
    loras: list[dict] | None = None,
    filename_prefix: str = "studioloop",
) -> str:
    """High-level: build workflow, submit, wait, download. Returns saved path."""
    workflow = build_flux_workflow(
        prompt=prompt,
        width=width,
        height=height,
        steps=steps,
        seed=seed,
        cfg=cfg,
        loras=loras,
        filename_prefix=filename_prefix,
    )
    prompt_id = queue_prompt(workflow)
    print(f"  Submitted prompt {prompt_id}, waiting...")
    history = wait_for_completion(prompt_id)
    saved = download_image(prompt_id, history, output_path)
    print(f"  Saved to {saved}")
    return saved
