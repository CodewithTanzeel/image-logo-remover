"""
cli.py — command-line interface for the logo remover.

Usage:
    python cli.py --image photo.jpg --mask mask.png --output result.jpg
    python cli.py --image photo.jpg --mask mask.png           # saves to cleaned_photo.jpg
    python cli.py --image photo.jpg --mask mask.png --model custom_weights.pth

Mask convention: white (255) = logo region to remove, black (0) = keep.
"""

import argparse
import os
import sys

import cv2

from inference import load_model, remove_logo

DEFAULT_MODEL = os.path.join(os.path.dirname(__file__),
                             "fine_tuned_watermark_remover.pth")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Remove a logo/watermark from an image using a trained PyTorch model.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --image photo.jpg --mask mask.png
  python cli.py --image photo.jpg --mask mask.png --output cleaned.jpg
  python cli.py --image photo.jpg --mask mask.png --model my_weights.pth
        """,
    )
    parser.add_argument("--image", required=True,
                        help="Path to the source image (JPEG or PNG).")
    parser.add_argument("--mask", required=True,
                        help="Path to the mask image (grayscale). "
                             "White pixels mark the logo region to remove.")
    parser.add_argument("--output", default=None,
                        help="Path to save the cleaned image. "
                             "Defaults to cleaned_<image_filename> in the same directory.")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Path to the .pth model file. Default: {DEFAULT_MODEL}")
    return parser.parse_args()


def default_output_path(image_path: str) -> str:
    directory = os.path.dirname(os.path.abspath(image_path))
    basename = os.path.basename(image_path)
    name, ext = os.path.splitext(basename)
    return os.path.join(directory, f"cleaned_{name}{ext if ext else '.jpg'}")


def main():
    args = parse_args()

    # --- Validate inputs ---
    if not os.path.isfile(args.image):
        print(f"[ERROR] Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.mask):
        print(f"[ERROR] Mask file not found: {args.mask}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.model):
        print(f"[ERROR] Model file not found: {args.model}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or default_output_path(args.image)

    # --- Load model ---
    print(f"Loading model from: {args.model}")
    model = load_model(args.model)

    # --- Load image and mask ---
    image_bgr = cv2.imread(args.image)
    if image_bgr is None:
        print(f"[ERROR] Could not read image: {args.image}", file=sys.stderr)
        sys.exit(1)

    mask_gray = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE)
    if mask_gray is None:
        print(f"[ERROR] Could not read mask: {args.mask}", file=sys.stderr)
        sys.exit(1)

    print(f"Image size : {image_bgr.shape[1]}x{image_bgr.shape[0]} px")
    print(f"Mask size  : {mask_gray.shape[1]}x{mask_gray.shape[0]} px")

    # --- Run inference ---
    print("Running inference...")
    result_bgr = remove_logo(model, image_bgr, mask_gray)

    # --- Save output ---
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    success = cv2.imwrite(output_path, result_bgr)
    if not success:
        print(f"[ERROR] Failed to save output image to: {output_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Done. Cleaned image saved to: {output_path}")


if __name__ == "__main__":
    main()
