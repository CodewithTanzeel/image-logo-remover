"""
inference.py — core inference functions for the logo remover pipeline.

Public API:
    model = load_model(pth_path)
    result_bgr = remove_logo(model, image_bgr, mask_gray)

Conventions:
    - image_bgr : numpy uint8 [H, W, 3]  (OpenCV BGR)
    - mask_gray : numpy uint8 [H, W]     (white=255 → logo area to remove)
    - returns   : numpy uint8 [H, W, 3]  (OpenCV BGR, same spatial size as input)
"""

import cv2
import numpy as np
import torch

from model import SimpleLogoRemover

# Model is trained at 256×256; resize inputs to this before inference.
MODEL_INPUT_SIZE = 256

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_model(pth_path: str) -> SimpleLogoRemover:
    """Load weights into the reconstructed architecture and set to eval mode."""
    model = SimpleLogoRemover()
    state = torch.load(pth_path, map_location=DEVICE)
    # Handle checkpoints that wrap weights under a 'state_dict' key
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    model.load_state_dict(state)
    model.to(DEVICE)
    model.eval()
    return model


def _preprocess(image_bgr: np.ndarray, mask_gray: np.ndarray):
    """
    Convert image + mask to a [1, 4, 256, 256] float tensor.
    Returns the tensor and the original (h, w) for restoring output size.
    """
    orig_h, orig_w = image_bgr.shape[:2]

    # Resize both to model input size
    img = cv2.resize(image_bgr, (MODEL_INPUT_SIZE, MODEL_INPUT_SIZE),
                     interpolation=cv2.INTER_LINEAR)
    mask = cv2.resize(mask_gray, (MODEL_INPUT_SIZE, MODEL_INPUT_SIZE),
                      interpolation=cv2.INTER_NEAREST)

    # BGR → RGB, normalise to [0, 1]
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    mask_norm = mask.astype(np.float32) / 255.0

    # [H, W, 3] → [3, H, W]
    img_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1)
    # [H, W] → [1, H, W]
    mask_tensor = torch.from_numpy(mask_norm).unsqueeze(0)

    # Concatenate to [4, H, W] then add batch dim → [1, 4, H, W]
    input_tensor = torch.cat([img_tensor, mask_tensor], dim=0).unsqueeze(0)
    return input_tensor.to(DEVICE), orig_h, orig_w


def _postprocess(output_tensor: torch.Tensor, orig_h: int, orig_w: int) -> np.ndarray:
    """
    Convert model output tensor [1, 3, 256, 256] back to a uint8 BGR numpy array
    at the original image resolution.
    """
    # [1, 3, H, W] → [H, W, 3], float32 in [0, 1]
    out = output_tensor.squeeze(0).permute(1, 2, 0).cpu().detach().numpy()
    out = np.clip(out, 0.0, 1.0)
    out_uint8 = (out * 255).astype(np.uint8)

    # RGB → BGR for OpenCV
    out_bgr = cv2.cvtColor(out_uint8, cv2.COLOR_RGB2BGR)

    # Resize back to original spatial dimensions if needed
    if (orig_h, orig_w) != (MODEL_INPUT_SIZE, MODEL_INPUT_SIZE):
        out_bgr = cv2.resize(out_bgr, (orig_w, orig_h),
                             interpolation=cv2.INTER_LINEAR)
    return out_bgr


def remove_logo(model: SimpleLogoRemover,
                image_bgr: np.ndarray,
                mask_gray: np.ndarray) -> np.ndarray:
    """
    Run the full logo-removal pipeline.

    Args:
        model      : loaded SimpleLogoRemover (from load_model())
        image_bgr  : input image as OpenCV BGR uint8 array [H, W, 3]
        mask_gray  : mask as grayscale uint8 array [H, W],
                     white (255) marks the logo region to remove

    Returns:
        Cleaned image as OpenCV BGR uint8 array [H, W, 3],
        same spatial size as the input image.
    """
    if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError(f"image_bgr must be [H, W, 3], got {image_bgr.shape}")
    if mask_gray.ndim != 2:
        raise ValueError(f"mask_gray must be [H, W], got {mask_gray.shape}")

    input_tensor, orig_h, orig_w = _preprocess(image_bgr, mask_gray)

    with torch.no_grad():
        output_tensor = model(input_tensor)

    return _postprocess(output_tensor, orig_h, orig_w)
