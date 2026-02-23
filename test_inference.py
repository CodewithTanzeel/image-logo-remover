"""
test_inference.py — smoke test for the full logo-removal pipeline.

What it tests:
  1. Model weights load without errors (all keys match, no unexpected keys)
  2. Forward pass runs without exceptions on a real dataset image
  3. Output shape matches input shape
  4. Output dtype is uint8, values are in [0, 255]
  5. Saves result to test_output.jpg for visual inspection

Run:
    python test_inference.py
"""

import os
import sys

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Locate a real test image from the dataset
# ---------------------------------------------------------------------------

DATASET_TEST_DIR = os.path.join(
    os.path.dirname(__file__),
    "watermark_removal_dataset", "wm-nown", "test", "watermark",
)
MODEL_PATH = os.path.join(os.path.dirname(__file__),
                          "fine_tuned_watermark_remover.pth")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "test_output.jpg")

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

errors = []


def check(condition: bool, name: str, detail: str = ""):
    if condition:
        print(f"  [{PASS}] {name}")
    else:
        msg = f"  [{FAIL}] {name}" + (f" — {detail}" if detail else "")
        print(msg)
        errors.append(name)


# ---------------------------------------------------------------------------
# 1. Find a test image
# ---------------------------------------------------------------------------

print("\n=== Logo Remover — Smoke Test ===\n")
print("[1] Locating test image...")

test_image_path = None
if os.path.isdir(DATASET_TEST_DIR):
    candidates = [f for f in os.listdir(DATASET_TEST_DIR)
                  if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if candidates:
        test_image_path = os.path.join(DATASET_TEST_DIR, sorted(candidates)[0])

if test_image_path:
    print(f"     Using dataset image: {test_image_path}")
else:
    # Fall back to a synthetic 256×256 colour image
    print("     Dataset test images not found — using synthetic 256×256 image.")
    synthetic_img = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
    test_image_path = os.path.join(os.path.dirname(__file__), "_synthetic_test.jpg")
    cv2.imwrite(test_image_path, synthetic_img)

check(os.path.isfile(test_image_path), "Test image accessible")

# ---------------------------------------------------------------------------
# 2. Load image and build a synthetic white mask covering top-left 30%
# ---------------------------------------------------------------------------

print("\n[2] Loading image and building mask...")

image_bgr = cv2.imread(test_image_path)
check(image_bgr is not None, "Image decoded by OpenCV",
      f"cv2.imread returned None for {test_image_path}")

if image_bgr is not None:
    h, w = image_bgr.shape[:2]
    print(f"     Image size: {w}×{h} px")

    # White box over the top-left 30% of the image (simulated logo region)
    mask_gray = np.zeros((h, w), dtype=np.uint8)
    mask_gray[: int(h * 0.30), : int(w * 0.30)] = 255
    check(mask_gray.sum() > 0, "Mask has white pixels (logo region set)")
else:
    mask_gray = None

# ---------------------------------------------------------------------------
# 3. Load model
# ---------------------------------------------------------------------------

print("\n[3] Loading model...")
check(os.path.isfile(MODEL_PATH), "Model file exists", MODEL_PATH)

model = None
if os.path.isfile(MODEL_PATH):
    try:
        from inference import load_model
        model = load_model(MODEL_PATH)
        check(True, "Model loaded and weights match architecture")
    except Exception as exc:
        check(False, "Model loaded and weights match architecture", str(exc))

# ---------------------------------------------------------------------------
# 4. Run inference
# ---------------------------------------------------------------------------

print("\n[4] Running inference...")

result = None
if model is not None and image_bgr is not None and mask_gray is not None:
    try:
        from inference import remove_logo
        result = remove_logo(model, image_bgr, mask_gray)
        check(True, "Inference completed without exception")
    except Exception as exc:
        check(False, "Inference completed without exception", str(exc))

# ---------------------------------------------------------------------------
# 5. Validate output
# ---------------------------------------------------------------------------

print("\n[5] Validating output...")

if result is not None:
    check(result.ndim == 3 and result.shape[2] == 3,
          "Output has 3 channels (BGR)", str(result.shape))
    check(result.dtype == np.uint8,
          "Output dtype is uint8", str(result.dtype))
    check(result.shape[:2] == image_bgr.shape[:2],
          "Output spatial size matches input",
          f"got {result.shape[:2]}, expected {image_bgr.shape[:2]}")
    check(result.min() >= 0 and result.max() <= 255,
          f"Output values in [0, 255] (got [{result.min()}, {result.max()}])")

    # Save for visual inspection
    saved = cv2.imwrite(OUTPUT_PATH, result)
    check(saved, f"Output saved to {OUTPUT_PATH}")
else:
    print(f"  [SKIP] Output validation skipped (inference did not produce a result)")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print()
if errors:
    print(f"RESULT: {len(errors)} test(s) FAILED: {', '.join(errors)}")
    sys.exit(1)
else:
    print("RESULT: All tests PASSED.")
    print(f"        Visual output saved to: {OUTPUT_PATH}")
    sys.exit(0)
