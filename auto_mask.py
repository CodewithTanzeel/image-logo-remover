"""
auto_mask.py — Automatic watermark / logo region detection.

Detects watermarks in images without requiring a user-provided mask.
Uses multiple heuristics:
  1. Low saturation (grey) region detection — most watermarks are grey
  2. Corner-zone filtering — watermarks typically appear in corners
  3. Largest connected component — removes noise, keeps main watermark
  4. Optional position hints for better accuracy

Public API:
    mask = generate_mask(image_bgr)
    mask = generate_mask(image_bgr, hint="bottom-right")
"""

from __future__ import annotations

import cv2
import numpy as np
from typing import Literal

HintType = Literal[
    "auto", 
    "bottom-right", 
    "bottom-left", 
    "top-right", 
    "top-left", 
    "center", 
    "full"
]

CORNER_FRAC = 0.30
MIN_BLOB_AREA = 100
SAT_THRESHOLD = 50
VAL_MIN = 40
VAL_MAX = 230


def _get_corner_roi(h: int, w: int, corner: str) -> tuple[int, int, int, int]:
    """Return (y_start, y_end, x_start, x_end) for a corner zone."""
    ch, cw = int(h * CORNER_FRAC), int(w * CORNER_FRAC)
    
    corners = {
        "top-left":     (0, ch, 0, cw),
        "top-right":    (0, ch, w - cw, w),
        "bottom-left":  (h - ch, h, 0, cw),
        "bottom-right": (h - ch, h, w - cw, w),
    }
    
    if corner not in corners:
        raise ValueError(f"Unknown corner: {corner}")
    
    return corners[corner]


def _create_corner_mask(h: int, w: int) -> np.ndarray:
    """Create a mask that covers all four corner zones."""
    mask = np.zeros((h, w), dtype=np.uint8)
    
    for corner in ["top-left", "top-right", "bottom-left", "bottom-right"]:
        y0, y1, x0, x1 = _get_corner_roi(h, w, corner)
        mask[y0:y1, x0:x1] = 255
    
    return mask


def _detect_grey_regions(image_bgr: np.ndarray) -> np.ndarray:
    """
    Detect low-saturation (grey) regions that are likely watermarks.
    
    Most text/graphic watermarks are semi-transparent grey overlays.
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]
    
    grey_mask = (
        (s_channel < SAT_THRESHOLD) & 
        (v_channel > VAL_MIN) & 
        (v_channel < VAL_MAX)
    ).astype(np.uint8) * 255
    
    return grey_mask


def _keep_largest_component(mask: np.ndarray, min_area: int = MIN_BLOB_AREA) -> np.ndarray:
    """Keep only the largest connected component above min_area."""
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    
    if num_labels <= 1:
        return mask
    
    areas = stats[1:, cv2.CC_STAT_AREA]
    
    if len(areas) == 0 or areas.max() < min_area:
        return np.zeros_like(mask)
    
    largest_idx = np.argmax(areas) + 1
    result = (labels == largest_idx).astype(np.uint8) * 255
    
    return result


def _morphology_cleanup(mask: np.ndarray) -> np.ndarray:
    """Apply morphological operations to clean up the mask."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    
    cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
    
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.dilate(cleaned, kernel_small, iterations=2)
    
    _, cleaned = cv2.threshold(cleaned, 127, 255, cv2.THRESH_BINARY)
    
    return cleaned


def _score_corners(grey_mask: np.ndarray, h: int, w: int) -> dict[str, float]:
    """Score each corner zone by grey pixel density."""
    scores = {}
    
    for corner in ["bottom-right", "bottom-left", "top-right", "top-left"]:
        y0, y1, x0, x1 = _get_corner_roi(h, w, corner)
        roi = grey_mask[y0:y1, x0:x1]
        score = float(np.count_nonzero(roi)) / roi.size
        scores[corner] = score
    
    return scores


def _fallback_corner_mask(h: int, w: int, corner: str = "bottom-right") -> np.ndarray:
    """Create a solid mask for the specified corner (last resort fallback)."""
    mask = np.zeros((h, w), dtype=np.uint8)
    y0, y1, x0, x1 = _get_corner_roi(h, w, corner)
    mask[y0:y1, x0:x1] = 255
    return mask


def generate_mask(
    image_bgr: np.ndarray,
    hint: HintType = "auto",
) -> np.ndarray:
    """
    Automatically generate a watermark mask for the given image.
    
    Args:
        image_bgr: Input image in BGR format, shape [H, W, 3], dtype uint8.
        hint: Position hint to guide detection. Options:
            - "auto": Automatically choose best corner (default)
            - "bottom-right": Force detection in bottom-right corner
            - "bottom-left": Force detection in bottom-left corner
            - "top-right": Force detection in top-right corner
            - "top-left": Force detection in top-left corner
            - "center": Look for centered watermark
            - "full": Return mask covering entire image
    
    Returns:
        Binary mask, shape [H, W], dtype uint8.
        White (255) = watermark region to remove.
        Black (0) = background to preserve.
    
    Raises:
        ValueError: If image has invalid shape or unknown hint.
    
    Example:
        >>> img = cv2.imread("photo.jpg")
        >>> mask = generate_mask(img, hint="auto")
        >>> cv2.imwrite("mask.png", mask)
    """
    if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError(
            f"image_bgr must be [H, W, 3], got shape {image_bgr.shape}"
        )
    
    h, w = image_bgr.shape[:2]
    
    if hint == "full":
        return np.full((h, w), 255, dtype=np.uint8)
    
    grey_mask = _detect_grey_regions(image_bgr)
    
    if hint == "center":
        yc0, yc1 = int(h * 0.2), int(h * 0.8)
        xc0, xc1 = int(w * 0.2), int(w * 0.8)
        center_mask = np.zeros_like(grey_mask)
        center_mask[yc0:yc1, xc0:xc1] = grey_mask[yc0:yc1, xc0:xc1]
        largest = _keep_largest_component(center_mask)
        if np.count_nonzero(largest) > MIN_BLOB_AREA * 10:
            return _morphology_cleanup(largest)
        full_center = np.zeros((h, w), dtype=np.uint8)
        full_center[yc0:yc1, xc0:xc1] = 255
        return full_center
    
    corner_mask = _create_corner_mask(h, w)
    grey_in_corners = cv2.bitwise_and(grey_mask, corner_mask)
    
    if hint in ["bottom-right", "bottom-left", "top-right", "top-left"]:
        y0, y1, x0, x1 = _get_corner_roi(h, w, hint)
        corner_grey = np.zeros_like(grey_mask)
        corner_grey[y0:y1, x0:x1] = grey_mask[y0:y1, x0:x1]
        largest = _keep_largest_component(corner_grey)
        
        if np.count_nonzero(largest) > MIN_BLOB_AREA:
            return _morphology_cleanup(largest)
        
        return _fallback_corner_mask(h, w, hint)
    
    largest = _keep_largest_component(grey_in_corners)
    
    if np.count_nonzero(largest) > MIN_BLOB_AREA:
        return _morphology_cleanup(largest)
    
    scores = _score_corners(grey_mask, h, w)
    best_corner = max(scores, key=scores.get)
    
    return _fallback_corner_mask(h, w, best_corner)


def visualize_mask(image_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Create a visualization overlay showing the detected mask on the image.
    
    Args:
        image_bgr: Original image [H, W, 3]
        mask: Binary mask [H, W]
    
    Returns:
        BGR image with red overlay on masked regions.
    """
    overlay = image_bgr.copy()
    overlay[mask > 127] = [0, 0, 255]
    return overlay
