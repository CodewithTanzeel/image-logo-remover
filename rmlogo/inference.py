"""
inference.py — Core watermark removal using OpenCV inpainting.

This module provides the main removal function using cv2.inpaint which
actually works for watermark removal (unlike the original CNN model which
learned an identity mapping).

Public API:
    result = remove_logo(image_bgr, mask_gray)
    
Conventions:
    - image_bgr : numpy uint8 [H, W, 3]  (OpenCV BGR format)
    - mask_gray : numpy uint8 [H, W]     (white=255 = logo to remove)
    - returns   : numpy uint8 [H, W, 3]  (cleaned image, same size as input)
"""

from __future__ import annotations

import cv2
import numpy as np

DEFAULT_INPAINT_RADIUS = 5
DEFAULT_INPAINT_METHOD = cv2.INPAINT_TELEA


def remove_logo(
    image_bgr: np.ndarray,
    mask_gray: np.ndarray,
    radius: int = DEFAULT_INPAINT_RADIUS,
    method: int = DEFAULT_INPAINT_METHOD,
) -> np.ndarray:
    """
    Remove a logo/watermark from an image using OpenCV inpainting.
    
    Args:
        image_bgr: Input image in BGR format, shape [H, W, 3], dtype uint8.
        mask_gray: Binary mask where white (255) marks the logo region.
                   Shape [H, W], dtype uint8. Must match image spatial dims.
        radius:    Inpainting radius (default 5). Larger = smoother but slower.
        method:    cv2.INPAINT_TELEA (default) or cv2.INPAINT_NS.
    
    Returns:
        Cleaned image as uint8 BGR array, same shape as input.
    
    Raises:
        ValueError: If image or mask have invalid shapes/sizes.
    
    Example:
        >>> img = cv2.imread("watermarked.jpg")
        >>> mask = generate_mask(img, hint="auto")
        >>> result = remove_logo(img, mask)
        >>> cv2.imwrite("cleaned.jpg", result)
    """
    if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError(
            f"image_bgr must be [H, W, 3], got shape {image_bgr.shape}"
        )
    
    if mask_gray.ndim != 2:
        raise ValueError(
            f"mask_gray must be [H, W], got shape {mask_gray.shape}"
        )
    
    if image_bgr.shape[:2] != mask_gray.shape:
        raise ValueError(
            f"Image {image_bgr.shape[:2]} and mask {mask_gray.shape} "
            f"spatial dimensions must match"
        )
    
    binary_mask = np.where(mask_gray > 127, 255, 0).astype(np.uint8)
    
    result = cv2.inpaint(image_bgr, binary_mask, radius, method)
    
    return result


def remove_logo_multi_scale(
    image_bgr: np.ndarray,
    mask_gray: np.ndarray,
    scales: list[int] | None = None,
) -> np.ndarray:
    """
    Multi-scale inpainting for large watermark regions.
    
    For watermarks covering >10% of the image, single-pass inpainting
    can leave artifacts. This method:
      1. Downsamples image and mask
      2. Inpaints at smaller scale (better context)
      3. Upsamples and blends result
    
    Args:
        image_bgr: Input image [H, W, 3]
        mask_gray: Binary mask [H, W]
        scales:    List of downsample scales, e.g. [4, 2, 1]
                   Default [4] for masks covering >20% of image
    
    Returns:
        Cleaned image [H, W, 3]
    """
    h, w = image_bgr.shape[:2]
    mask_coverage = (mask_gray > 127).sum() / mask_gray.size
    
    if scales is None:
        if mask_coverage > 0.20:
            scales = [4]
        elif mask_coverage > 0.10:
            scales = [2]
        else:
            scales = [1]
    
    if 1 in scales:
        return remove_logo(image_bgr, mask_gray)
    
    scale = scales[0]
    small_h, small_w = h // scale, w // scale
    
    small_img = cv2.resize(
        image_bgr, (small_w, small_h), interpolation=cv2.INTER_AREA
    )
    small_mask = cv2.resize(
        mask_gray, (small_w, small_h), interpolation=cv2.INTER_NEAREST
    )
    
    small_result = remove_logo(small_img, small_mask, radius=max(3, scale))
    
    result = cv2.resize(
        small_result, (w, h), interpolation=cv2.INTER_CUBIC
    )
    
    mask_3ch = np.stack([mask_gray > 127] * 3, axis=2)
    blended = np.where(mask_3ch, result, image_bgr)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    edge_mask = cv2.dilate(mask_gray, kernel) - cv2.erode(mask_gray, kernel)
    _, edge_mask = cv2.threshold(edge_mask, 10, 255, cv2.THRESH_BINARY)
    
    blended = cv2.inpaint(blended.astype(np.uint8), edge_mask, 2, cv2.INPAINT_TELEA)
    
    return blended
