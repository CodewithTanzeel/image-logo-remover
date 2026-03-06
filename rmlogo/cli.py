#!/usr/bin/env python3
"""
cli.py — Advanced Command-line interface for rmlogo (Image Logo Remover).

A professional CLI tool to remove watermarks/logos from images.
Uses automatic watermark detection + OpenCV inpainting.

Features:
  - Single file processing with output path prompting
  - Batch processing with timestamped output folders
  - Multi-threaded operations (auto-detected CPU cores)
  - Piping support (Unix/PowerShell/WSL compatible)
  - Per-image processing time tracking
  - JSON output for automation/scripting
  - Progress bars with tqdm
  - Dry-run preview mode
  - Pattern matching for batch filtering
  - Gemini AI hint integration (--bgrm)

Usage:
    rmlogo input.jpg                          # Single file with prompt
    rmlogo input.jpg --bgrm "hint text"       # With Gemini hint
    rmlogo --batch /path/to/folder/           # Batch processing
    rmlogo --batch /path --pattern "*.jpg"    # Batch with filter
    find . -name "*.jpg" | rmlogo --batch -   # Piping support
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

import cv2
import numpy as np
from tqdm import tqdm

from .auto_mask import generate_mask, visualize_mask, HintType
from .inference import remove_logo


VERSION = "2.1.0"

HINT_CHOICES = [
    "auto",
    "bottom-right",
    "bottom-left",
    "top-right",
    "top-left",
    "center",
    "full",
]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}


# ============================================================================
# GEMINI HINT PARSER (no API, purely text-based)
# ============================================================================


def parse_gemini_hint(text: str) -> HintType:
    """
    Parse Gemini-generated text to extract a position hint.

    Scans for natural language position keywords and returns the best match.
    Completely offline, no API calls.

    Args:
        text: Gemini output or any user text describing watermark location

    Returns:
        HintType: Detected position hint, or "auto" if nothing matched

    Example:
        >>> parse_gemini_hint("The watermark is in the bottom right corner")
        'bottom-right'
        >>> parse_gemini_hint("Entire image has watermark")
        'full'
        >>> parse_gemini_hint("I don't know")
        'auto'
    """
    text_lower = text.lower()

    # Define keyword patterns for each hint type
    patterns = {
        "bottom-right": [
            r"bottom\s+right",
            r"lower\s+right",
            r"bottom-right",
            r"bottom right",
            r"lower right",
        ],
        "bottom-left": [
            r"bottom\s+left",
            r"lower\s+left",
            r"bottom-left",
            r"bottom left",
            r"lower left",
        ],
        "top-right": [
            r"top\s+right",
            r"upper\s+right",
            r"top-right",
            r"top right",
            r"upper right",
        ],
        "top-left": [
            r"top\s+left",
            r"upper\s+left",
            r"top-left",
            r"top left",
            r"upper left",
        ],
        "center": [r"center", r"middle", r"centered", r"centre"],
        "full": [r"entire", r"whole\s+image", r"everywhere", r"full", r"complete"],
    }

    # Check patterns in priority order (most specific first)
    for hint, keywords in patterns.items():
        for keyword in keywords:
            if re.search(keyword, text_lower):
                return hint  # type: ignore

    # Fallback to auto if nothing matched
    return "auto"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def is_image_file(filepath: str) -> bool:
    """Check if file is a valid image format."""
    try:
        ext = Path(filepath).suffix.lower()
        if ext not in IMAGE_EXTENSIONS:
            return False
        # Try to read to validate it's actually an image
        img = cv2.imread(filepath)
        return img is not None
    except Exception:
        return False


def default_output_path(input_path: str) -> str:
    """Generate default output filename: cleaned_<input_name>.<ext>"""
    p = Path(input_path)
    return str(p.parent / f"{p.stem}_cleaned{p.suffix}")


def prompt_output_path(default_path: str) -> str:
    """
    Interactively prompt user for output path.

    Args:
        default_path: Default path to show in prompt

    Returns:
        User-provided path or default if empty input

    Raises:
        KeyboardInterrupt: If user cancels
    """
    while True:
        prompt = f"Save cleaned image to: [{default_path}]\n> "
        user_input = input(prompt).strip()
        chosen_path = user_input if user_input else default_path

        # Check if file exists
        if Path(chosen_path).exists():
            confirm = input(f"File already exists. Overwrite? [y/N]: ").strip().lower()
            if confirm == "y":
                return chosen_path
            # User said no, loop and ask again
            continue

        return chosen_path


def create_output_directory(base_name: str = "cleaned_images") -> str:
    """
    Create timestamped output directory.

    Args:
        base_name: Base directory name

    Returns:
        Path to created directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(base_name + "_" + timestamp)
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)


def validate_input(path: str) -> bool:
    """
    Validate that input file exists and is readable.

    Returns:
        True if valid, False otherwise
    """
    if not os.path.isfile(path):
        print(f"Error: Input file not found: {path}", file=sys.stderr)
        return False

    if not is_image_file(path):
        print(f"Error: Cannot read image file: {path}", file=sys.stderr)
        return False

    return True


def get_batch_files(folder: str, pattern: Optional[str] = None) -> list[str]:
    """
    Get list of image files from folder.

    Args:
        folder: Directory path
        pattern: Comma-separated patterns like "*.jpg,*.png" or None for all images

    Returns:
        List of valid image file paths
    """
    folder_path = Path(folder)

    if not folder_path.is_dir():
        raise ValueError(f"Folder not found: {folder}")

    # Parse patterns
    if pattern:
        patterns = [p.strip() for p in pattern.split(",")]
    else:
        patterns = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif", "*.tiff", "*.webp"]

    # Collect files
    files = []
    for pat in patterns:
        files.extend(folder_path.glob(pat))
        files.extend(folder_path.glob(pat.upper()))  # Case-insensitive on Unix

    # Convert to strings, remove duplicates, validate
    unique_files = list(set(str(f) for f in files if f.is_file()))
    valid_files = [f for f in sorted(unique_files) if is_image_file(f)]

    return valid_files


def pipe_to_batch() -> list[str]:
    """
    Read file paths from stdin (piped input).

    Returns:
        List of valid image file paths from pipe
    """
    files = []
    try:
        for line in sys.stdin:
            filepath = line.strip()
            if filepath and is_image_file(filepath):
                files.append(filepath)
    except KeyboardInterrupt:
        pass

    return files


def validate_batch_args(args) -> bool:
    """Validate batch mode arguments."""
    if not args.batch:
        return True

    if args.batch != "-" and not Path(args.batch).is_dir():
        print(f"Error: Folder not found: {args.batch}", file=sys.stderr)
        return False

    if args.threads and (args.threads < 1 or args.threads > 128):
        print(
            f"Error: --threads must be between 1 and 128, got {args.threads}",
            file=sys.stderr,
        )
        return False

    return True


def get_thread_count(user_override: Optional[int] = None) -> int:
    """
    Calculate optimal thread count.

    Args:
        user_override: User-specified thread count, or None for auto-detection

    Returns:
        Number of threads to use
    """
    if user_override:
        return user_override

    cpu_count = os.cpu_count() or 4
    # Use half the CPU cores, capped at 8
    return min(max(1, cpu_count // 2), 8)


# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================


def process_image(
    input_path: str,
    output_path: str,
    hint: HintType = "auto",
    verbose: bool = False,
    save_mask: Optional[str] = None,
) -> tuple[bool, dict]:
    """
    Process a single image: detect watermark, remove it, save result.

    Returns:
        Tuple of (success: bool, metadata: dict)
    """
    start_time = time.time()
    metadata = {
        "input": input_path,
        "output": output_path,
        "status": "failed",
        "time_ms": 0,
        "error": None,
    }

    try:
        if verbose:
            print(f"Loading image: {input_path}")

        image = cv2.imread(input_path)
        if image is None:
            raise ValueError("Cannot read image")

        h, w = image.shape[:2]
        if verbose:
            print(f"Image size: {w}×{h}")

        if verbose:
            print(f"Detecting watermark (hint={hint})...")

        mask = generate_mask(image, hint=hint)

        mask_pixels = (mask > 127).sum()
        mask_pct = 100 * mask_pixels / mask.size
        if verbose:
            print(f"Detected watermark region: {mask_pixels} pixels ({mask_pct:.2f}%)")

        if save_mask:
            if verbose:
                print(f"Saving mask visualization: {save_mask}")
            cv2.imwrite(save_mask, visualize_mask(image, mask))

        if verbose:
            print("Removing watermark...")

        result = remove_logo(image, mask)

        if verbose:
            print(f"Saving result: {output_path}")

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        success = cv2.imwrite(output_path, result)
        if not success:
            raise ValueError(f"Failed to save output")

        elapsed_ms = int((time.time() - start_time) * 1000)
        metadata["status"] = "success"
        metadata["time_ms"] = elapsed_ms
        return True, metadata

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        metadata["status"] = "failed"
        metadata["time_ms"] = elapsed_ms
        metadata["error"] = str(e)
        return False, metadata


def process_single(
    input_path: str,
    output_path: Optional[str] = None,
    hint: HintType = "auto",
    verbose: bool = False,
    save_mask: Optional[str] = None,
) -> int:
    """
    Process single file with interactive output prompt.

    Returns:
        Exit code (0=success, 1=failure)
    """
    if not validate_input(input_path):
        return 1

    # Determine output path
    if output_path is None:
        output_path = default_output_path(input_path)

    # Always ask user for output path (no --no-ask bypass)
    output_path = prompt_output_path(output_path)

    # Process
    success, metadata = process_image(
        input_path=input_path,
        output_path=output_path,
        hint=hint,
        verbose=verbose,
        save_mask=save_mask,
    )

    if success:
        elapsed_sec = metadata["time_ms"] / 1000
        print(f"[OK] Saved to: {output_path} ({elapsed_sec:.2f}s)")
        return 0
    else:
        print(f"[ERROR] {metadata['error']}", file=sys.stderr)
        return 1


def process_batch(
    files: list[str],
    output_dir: str,
    hint: HintType = "auto",
    threads: int = 4,
    verbose: bool = False,
    quiet: bool = False,
    json_output: bool = False,
) -> tuple[int, list[dict]]:
    """
    Process multiple images in parallel using thread pool.

    Returns:
        Tuple of (exit_code, results_list)
    """
    if not files:
        print("Error: No image files found", file=sys.stderr)
        return 1, []

    if not quiet:
        print(f"Found {len(files)} images")
        print(f"Output directory: {output_dir}")
        print(f"Using {threads} threads")
        print()

    results = []
    failed_count = 0

    # Create progress bar
    pbar = tqdm(total=len(files), disable=quiet, desc="Processing", unit="img")

    def process_worker(input_file: str) -> tuple[str, bool, dict]:
        """Worker function for thread pool."""
        filename = Path(input_file).name
        output_file = str(
            Path(output_dir)
            / f"{Path(input_file).stem}_cleaned{Path(input_file).suffix}"
        )

        success, metadata = process_image(
            input_path=input_file,
            output_path=output_file,
            hint=hint,
            verbose=False,
        )

        return filename, success, metadata

    # Process with thread pool
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(process_worker, f): f for f in files}

        for future in as_completed(futures):
            try:
                filename, success, metadata = future.result()
                results.append(metadata)

                elapsed_sec = metadata["time_ms"] / 1000
                if success:
                    if not quiet:
                        pbar.write(f"[OK] {filename} ({elapsed_sec:.2f}s)")
                else:
                    if not quiet:
                        pbar.write(f"[FAIL] {filename} - {metadata['error']}")
                    failed_count += 1

                pbar.update(1)

            except Exception as e:
                if not quiet:
                    pbar.write(f"[ERROR] Error processing: {str(e)}")
                failed_count += 1
                pbar.update(1)

    pbar.close()

    # Summary
    succeeded = len(files) - failed_count
    total_time_ms = sum(r.get("time_ms", 0) for r in results)
    avg_time_ms = total_time_ms / len(files) if files else 0

    print()
    print("=" * 70)
    print(f"Summary: {succeeded}/{len(files)} passed | Failed: {failed_count}")
    print(
        f"Total time: {total_time_ms / 1000:.2f}s | Average: {avg_time_ms / 1000:.2f}s per image"
    )
    print(f"Output directory: {output_dir}")
    print("=" * 70)

    # JSON output if requested
    if json_output:
        json_output_path = Path(output_dir) / "processing_log.json"
        json_data = {
            "status": "success" if failed_count == 0 else "partial",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(files),
                "succeeded": succeeded,
                "failed": failed_count,
                "total_time_ms": total_time_ms,
                "average_time_ms": avg_time_ms,
            },
            "results": results,
        }
        with open(json_output_path, "w") as f:
            json.dump(json_data, f, indent=2)
        print(f"JSON log saved to: {json_output_path}")

    return 0 if failed_count == 0 else 1, results


def dry_run_batch(files: list[str], output_dir: str) -> bool:
    """
    Preview batch processing without actually processing.

    Returns:
        True if user confirms to proceed
    """
    if not files:
        print("Error: No image files found")
        return False

    print()
    print("-" * 70)
    print("DRY RUN MODE - Preview Only")
    print("-" * 70)
    print(f"Found: {len(files)} images")
    print()

    total_size = 0
    for f in files[:10]:  # Show first 10
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  - {Path(f).name} ({size_mb:.2f} MB)")
        total_size += size_mb

    if len(files) > 10:
        for f in files[10:]:
            total_size += os.path.getsize(f) / (1024 * 1024)
        print(f"  ... and {len(files) - 10} more files")

    estimated_time = len(files) * 2.1  # ~2.1s per image on average
    print()
    print(f"Total disk needed: ~{total_size:.1f} MB")
    print(f"Estimated time: ~{estimated_time:.1f}s")
    print(f"Output folder: {output_dir}")
    print()

    response = input("Continue? [Y/n] ").strip().lower()
    return response != "n"


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="rmlogo",
        description="Remove watermarks/logos from images using automatic detection and OpenCV inpainting.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples - Single File:
  %(prog)s photo.jpg                    Interactive output path prompt
  %(prog)s photo.jpg -o result.png      Specify output explicitly
  %(prog)s photo.jpg --hint bottom-right   Hint watermark location
  %(prog)s photo.jpg --bgrm "watermark is bottom right"   Use Gemini hint

Examples - Batch Processing:
  %(prog)s --batch /path/to/folder/     Process all images
  %(prog)s --batch /path --pattern "*.jpg"    Only JPEGs
  %(prog)s --batch /path --threads 4 -v       Use 4 threads + verbose

Examples - Piping (Advanced):
  find . -name "*.jpg" | %(prog)s --batch -
  Get-ChildItem *.jpg | %(prog)s --batch -

Position Hints:
  auto          Automatically detect (default)
  bottom-right  Watermark in bottom-right corner
  bottom-left   Watermark in bottom-left corner
  top-right     Watermark in top-right corner
  top-left      Watermark in top-left corner
  center        Watermark near center
  full          Treat entire image as watermark

Gemini Integration (--bgrm):
  Paste Gemini AI response describing watermark location.
  The tool parses it offline to extract the position hint.
  Example: %(prog)s photo.jpg --bgrm "The watermark is in the bottom right"

Options:
  -q, --quiet   Suppress progress output
  -v, --verbose Show detailed progress
  --json        Output results as JSON
  --dry-run     Preview batch without processing
        """,
    )

    # Positional argument (optional for batch mode)
    parser.add_argument(
        "input",
        nargs="?",
        metavar="INPUT",
        help="Path to image file (optional if using --batch)",
    )

    # Single file options
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="Output path (single mode only)",
    )

    # Common options
    parser.add_argument(
        "--hint",
        choices=HINT_CHOICES,
        default="auto",
        help="Watermark position hint (default: auto)",
    )

    parser.add_argument(
        "--bgrm",
        metavar="TEXT",
        help="Paste Gemini AI response here. Tool parses it to extract position hint.",
    )

    parser.add_argument(
        "--save-mask",
        metavar="PATH",
        help="Save detected mask visualization to file",
    )

    # Batch options
    parser.add_argument(
        "--batch",
        metavar="PATH",
        help="Batch mode: process folder. Use '-' for stdin piping.",
    )

    parser.add_argument(
        "--pattern",
        metavar="PATTERNS",
        help='File pattern filter: "*.jpg" or "*.jpg,*.png" (default: all images)',
    )

    parser.add_argument(
        "--threads",
        type=int,
        metavar="N",
        help="Number of worker threads (default: auto-detect)",
    )

    parser.add_argument(
        "--output-dir",
        metavar="PATH",
        help="Override default output directory for batch mode",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview batch processing without executing",
    )

    # Output options
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed progress messages",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )

    args = parser.parse_args(argv)

    # Validate arguments
    if not validate_batch_args(args):
        return 1

    # BATCH MODE
    if args.batch:
        if args.batch == "-":
            # Read from stdin (piping)
            if not args.quiet:
                print("Reading filenames from stdin...", file=sys.stderr)
            files = pipe_to_batch()
        else:
            # Read from folder
            files = get_batch_files(args.batch, args.pattern)

        if not files:
            print(f"Error: No image files found", file=sys.stderr)
            return 1

        # Create output directory
        if args.output_dir:
            output_dir = args.output_dir
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        else:
            output_dir = create_output_directory("cleaned_images")

        # Dry-run mode
        if args.dry_run:
            if not dry_run_batch(files, output_dir):
                return 0

        # Get thread count
        thread_count = get_thread_count(args.threads)

        # Determine hint (--bgrm overrides --hint)
        hint = args.hint
        if args.bgrm:
            detected_hint = parse_gemini_hint(args.bgrm)
            if detected_hint != "auto":
                print(f"[Gemini hint detected: {detected_hint}]")
                hint = detected_hint

        # Process batch
        exit_code, results = process_batch(
            files=files,
            output_dir=output_dir,
            hint=hint,
            threads=thread_count,
            verbose=args.verbose,
            quiet=args.quiet,
            json_output=args.json,
        )

        return exit_code

    # SINGLE FILE MODE
    if not args.input:
        parser.print_help()
        return 1

    # Determine hint (--bgrm overrides --hint)
    hint = args.hint
    if args.bgrm:
        detected_hint = parse_gemini_hint(args.bgrm)
        if detected_hint != "auto":
            print(f"[Gemini hint detected: {detected_hint}]")
            hint = detected_hint

    return process_single(
        input_path=args.input,
        output_path=args.output,
        hint=hint,
        verbose=args.verbose,
        save_mask=args.save_mask,
    )


if __name__ == "__main__":
    sys.exit(main())
