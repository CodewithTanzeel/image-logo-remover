# Image Logo Remover - CLI Tool

A professional, zero-friction CLI tool to remove watermarks and logos from images. Uses automatic watermark detection and OpenCV inpainting — **no GPU required, no model downloads needed**.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## Features

- **Single File Mode** — Process one image with interactive output path prompting
- **Batch Processing** — Process entire folders with automatic timestamped output directories
- **Multi-threaded** — Auto-detects CPU cores for optimal performance (~1.7x faster)
- **Piping Support** — Integrate with Unix `find`, PowerShell `Get-ChildItem`, and WSL commands
- **Per-Image Timing** — Track processing time for each image
- **JSON Output** — Machine-readable results for automation and scripting
- **Progress Tracking** — Visual progress bars with tqdm (can be disabled with `-q`)
- **Dry-Run Mode** — Preview batch processing before executing
- **Pattern Matching** — Filter files by pattern (e.g., `*.jpg,*.png`)
- **Fast** — OpenCV inpainting, no heavy ML inference
- **Cross-platform** — Works on Windows (PowerShell), macOS, Linux

---

## Installation

### From PyPI (Recommended)

```bash
pip install rmlogo
```

### From GitHub

```bash
pip install git+https://github.com/CodewithanZeeL/image-logo-remover.git
```

### From Source

```bash
git clone https://github.com/CodewithanZeeL/image-logo-remover.git
cd image-logo-remover
pip install -e .
```

---

## Quick Start

### Single File Mode

```bash
# Process with interactive output path prompt
rmlogo photo.jpg
# → "Save cleaned image to: [./cleaned_photo.jpg]"
# → Press Enter to accept default, or type custom path

# Specify output explicitly
rmlogo photo.jpg -o result.png

# With position hint
rmlogo photo.jpg --hint bottom-right

# Debug mode - see detected mask
rmlogo photo.jpg --save-mask debug_mask.png -v
```

### Batch Processing

```bash
# Process all images in folder (creates timestamped output directory)
rmlogo --batch ./photos/
# → Output: ./cleaned_images_20250224_153042/

# Only process JPEGs
rmlogo --batch ./photos/ --pattern "*.jpg"

# Multiple patterns
rmlogo --batch ./photos/ --pattern "*.jpg,*.png"

# Use specific number of threads (default: auto-detect)
rmlogo --batch ./photos/ --threads 4

# Verbose output with detailed progress
rmlogo --batch ./photos/ -v

# Quiet mode (minimal output)
rmlogo --batch ./photos/ -q

# Preview before processing (dry-run)
rmlogo --batch ./photos/ --dry-run

# Save processing log as JSON
rmlogo --batch ./photos/ --json
```

### Advanced: Piping Support

Use with Unix `find`, PowerShell, or WSL for powerful filtering:

```bash
# UNIX/Linux - Process only JPEGs modified in last 24 hours
find /path/to/photos -name "*.jpg" -mtime -1 | rmlogo --batch -

# UNIX/Linux - Process files over 2MB
find /path/to/photos -name "*.jpg" -size +2M | rmlogo --batch -

# PowerShell - Process files from current directory
Get-ChildItem *.jpg | Select-Object FullName | rmlogo --batch -

# PowerShell - Process files modified today
Get-ChildItem *.jpg | Where-Object { $_.LastWriteTime -gt [datetime]::Today } | rmlogo --batch -

# WSL/Linux with piping to other tools
ls /mnt/c/Photos/*.jpg | rmlogo --batch - --json | jq '.summary'

# Combine with other image tools
find . -name "*.jpg" | rmlogo --batch - -q --threads 6
```

---

## Usage Reference

### Command-Line Syntax

```
usage: rmlogo [-h] [-o PATH] [--hint HINT] [--bgrm TEXT] [--save-mask PATH]
              [--batch PATH] [--pattern PATTERNS] [--threads N]
              [--output-dir PATH] [--dry-run]
              [-q] [-v] [--json] [--version]
              [INPUT]

Remove watermarks/logos from images using automatic detection.

positional arguments:
  INPUT                 Path to image file (optional if using --batch)

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

Single File Options:
  -o PATH, --output PATH
                        Output path (single mode only)

Common Options:
  --hint HINT           Watermark position: auto, bottom-right, bottom-left,
                        top-right, top-left, center, full (default: auto)
  --bgrm TEXT           Paste Gemini AI response here to extract position hint
  --save-mask PATH      Save detected mask visualization to file

Batch Mode Options:
  --batch PATH          Folder to process or '-' for stdin piping
  --pattern PATTERNS    Filter files: "*.jpg" or "*.jpg,*.png"
  --threads N           Number of worker threads (default: auto-detect)
  --output-dir PATH     Custom output directory (default: timestamped)
  --dry-run             Preview batch without processing

Output Options:
  -q, --quiet           Suppress progress output
  -v, --verbose         Show detailed progress messages
  --json                Output results as JSON
```

---

## Position Hints

| Hint | Description |
|------|-------------|
| `auto` | Automatically detect watermark location (default) |
| `bottom-right` | Watermark in bottom-right corner |
| `bottom-left` | Watermark in bottom-left corner |
| `top-right` | Watermark in top-right corner |
| `top-left` | Watermark in top-left corner |
| `center` | Watermark near center of image |
| `full` | Treat entire image as watermark region |

For best results, use `auto` first. If detection misses the watermark, try specifying the corner.

---

## Output Examples

### Single File Mode

```
$ logo-remover photo.jpg
Save cleaned image to: [./cleaned_photo.jpg]
> ./results/photo_final.png
✓ Cleaned image saved to: ./results/photo_final.png (2.10s)
```

### Batch Mode - Normal Progress

```
$ logo-remover --batch ./photos/ --threads 4
Found 5 images
Output directory: ./cleaned_images_20250224_153042
Using 4 threads

Processing: |████████░░| 80% [4/5]
✓ photo1.jpg (2.1s)
✓ photo2.jpg (1.9s)
✓ photo3.jpg (2.3s)
✓ photo4.jpg (2.0s)
⏳ photo5.jpg

======================================================================
Summary: 5/5 ✓ | Failed: 0
Total time: 12.30s | Average: 2.46s per image
Output directory: ./cleaned_images_20250224_153042
======================================================================
```

### Batch Mode - Dry-Run

```
$ logo-remover --batch ./photos/ --dry-run

----------------------------------------------------------------------
DRY RUN MODE - Preview Only
----------------------------------------------------------------------
Found: 5 images

  - photo1.jpg (2.00 MB)
  - photo2.jpg (1.50 MB)
  - photo3.jpg (2.30 MB)
  - photo4.jpg (1.80 MB)
  - photo5.jpg (2.10 MB)

Total disk needed: ~9.7 MB
Estimated time: ~12.3s
Output folder: ./cleaned_images_20250224_153042

Continue? [Y/n] Y
→ Processing...
```

### Batch Mode - JSON Output

```bash
$ logo-remover --batch ./photos/ --json
# Creates: ./cleaned_images_20250224_153042/processing_log.json
```

Contents:
```json
{
  "status": "success",
  "timestamp": "2025-02-24T15:30:42.123Z",
  "summary": {
    "total": 5,
    "succeeded": 5,
    "failed": 0,
    "total_time_ms": 12300,
    "average_time_ms": 2460
  },
  "results": [
    {
      "input": "./photos/photo1.jpg",
      "output": "./cleaned_images_20250224_153042/photo1_cleaned.jpg",
      "status": "success",
      "time_ms": 2100
    }
  ]
}
```

---

## How It Works

1. **Grey Region Detection** — Watermarks are typically low-saturation (grey) overlays. The tool detects these using HSV color space analysis.

2. **Corner Filtering** — Most watermarks appear in image corners. The detector scores each corner zone and selects the best region.

3. **Largest Component Selection** — Keeps only the largest connected grey region, filtering out noise.

4. **Morphological Cleanup** — Smooths mask edges and fills small gaps.

5. **OpenCV Inpainting** — Uses Telea's inpainting algorithm to reconstruct the watermark region from surrounding pixels.

```
Input Image → Grey Detection → Corner Filter → Cleanup → Inpaint → Clean Image
```

---

## Performance

### Typical Performance (8-core CPU, 2MB JPEG)

| Mode | Time | Speedup |
|------|------|---------|
| Single file | ~2.1s | — |
| Batch (5 files, 1 thread) | ~10.5s | 1.0x |
| Batch (5 files, 4 threads) | ~6.2s | 1.7x |
| Batch (5 files, 8 threads) | ~5.8s | 1.8x |

Thread count auto-detection formula: `min(CPU_cores // 2, 8)`

---

## Limitations

- **Best for corner watermarks** — Small logos in corners work best
- **Large overlays** — Watermarks covering >30% may leave artifacts
- **Semi-transparent only** — Solid/opaque watermarks harder to detect
- **Uniform backgrounds** — Works better on photos than graphics/textures

---

## Examples by Use Case

### Photography Studio

```bash
# Process a day's batch of photos
rmlogo --batch ./photo_shoot_20250224/ --threads 8 -v

# Archive organized by date
rmlogo --batch ./photos_2025/ --output-dir ./cleaned_archive_2025/
```

### Batch Processing with Verification

```bash
# First: preview
rmlogo --batch ./images/ --dry-run

# Then: process and save JSON for QA
rmlogo --batch ./images/ --json

# Analyze results
cat ./cleaned_images_*/processing_log.json | jq '.summary'
```

### Integration with Other Tools

```bash
# Send only successful results to another process
rmlogo --batch ./photos/ --json | jq -r '.results[] | select(.status=="success") | .output'

# Process and send to cloud storage
find ./photos -name "*.jpg" | rmlogo --batch - --json | \
  jq -r '.results[] | .output' | xargs -I {} aws s3 cp {} s3://my-bucket/
```

### Scripting & Automation

```bash
#!/bin/bash
# Automatic cleanup script

INPUT_DIR="./watermarked_photos"
OUTPUT_BASE="./cleaned_photos"

# Create timestamped output
OUTPUT_DIR="${OUTPUT_BASE}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Process
rmlogo --batch "$INPUT_DIR" --output-dir "$OUTPUT_DIR" --json

# Check results
RESULTS="${OUTPUT_DIR}/processing_log.json"
SUCCEEDED=$(jq '.summary.succeeded' "$RESULTS")
FAILED=$(jq '.summary.failed' "$RESULTS")

echo "Processed: $SUCCEEDED succeeded, $FAILED failed"
echo "Results in: $OUTPUT_DIR"
```

---

## Troubleshooting

### Watermark Not Detected

1. Try specifying a position hint:
   ```bash
   rmlogo photo.jpg --hint bottom-right
   ```

2. Save the mask to inspect:
   ```bash
   rmlogo photo.jpg --save-mask debug.png -v
   ```

3. Check if watermark is very faint or in center:
   ```bash
   rmlogo photo.jpg --hint center
   ```

### Slow Performance

1. Check available CPU cores:
   ```bash
   # Windows: View system info
   # Linux/Mac: nproc
   ```

2. Manually specify thread count:
   ```bash
   rmlogo --batch ./photos/ --threads 4
   ```

3. Use quiet mode to reduce I/O:
   ```bash
   rmlogo --batch ./photos/ -q
   ```

### Permission Errors

Ensure read/write permissions:
```bash
# Linux/Mac
chmod +x cli.py
```

---

## Project Structure

```
image-logo-remover/
├── rmlogo/             # Main package directory
│   ├── __init__.py     # Package initialization
│   ├── cli.py          # Command-line interface entry point
│   ├── auto_mask.py    # Automatic watermark detection
│   └── inference.py    # OpenCV inpainting logic
├── tests/              # Test suite with pytest
├── pyproject.toml      # Package configuration
├── README.md           # This file
└── LICENSE             # GPL-3.0 license
```

---

## Dependencies

```
opencv-python>=4.9.0   # Image processing
numpy>=1.26.0          # Numerical operations
pillow>=10.0.0         # Image I/O compatibility
tqdm>=4.66.0           # Progress bars
```

All dependencies are installed automatically via pip.

---

## Contributing

Contributions welcome! Areas for improvement:

- Better watermark detection algorithms
- Support for batch filtering by image properties
- Optimization for very large images
- Additional inpainting methods
- More comprehensive tests

---

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- OpenCV for inpainting algorithms
- Computer vision community for watermark detection research
- tqdm for beautiful progress bars
